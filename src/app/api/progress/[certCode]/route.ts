import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ certCode: string }> }
) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { certCode } = await params;

  const cert = await prisma.certification.findUnique({
    where: { code: certCode.toUpperCase() },
    include: {
      modules: {
        orderBy: { orderIndex: "asc" },
        include: { topics: true },
      },
    },
  });
  if (!cert) {
    return NextResponse.json({ error: "Certification not found" }, { status: 404 });
  }

  const [allProgress, pendingDocs, recentAnswers] = await Promise.all([
    prisma.userQuestionProgress.findMany({
      where: { userId: session.userId, question: { certificationId: cert.id } },
      include: { question: { select: { topicId: true, moduleId: true, difficulty: true } } },
    }),
    prisma.userDocumentation.count({
      where: {
        userId: session.userId,
        status: { not: "confirmed" },
        topic: { module: { certificationId: cert.id } },
      },
    }),
    prisma.userQuestionProgress.findMany({
      where: {
        userId: session.userId,
        question: { certificationId: cert.id },
        lastAnsweredAt: { not: null },
      },
      orderBy: { lastAnsweredAt: "desc" },
      take: 20,
      include: { question: { select: { topicId: true } } },
    }),
  ]);

  const statusMap: Record<string, number> = {};
  for (const p of allProgress) {
    statusMap[p.status] = (statusMap[p.status] || 0) + 1;
  }

  const totalQuestions = await prisma.question.count({
    where: { certificationId: cert.id, isActive: true },
  });

  // Weak topics: lowest accuracy
  const topicAccuracy: Record<string, { correct: number; total: number }> = {};
  for (const p of allProgress) {
    const topicId = p.question.topicId;
    if (!topicId) continue;
    if (!topicAccuracy[topicId]) topicAccuracy[topicId] = { correct: 0, total: 0 };
    topicAccuracy[topicId].total += p.timesAnswered;
    topicAccuracy[topicId].correct += p.timesCorrect;
  }

  const weakTopics = Object.entries(topicAccuracy)
    .filter(([, v]) => v.total > 0)
    .map(([topicId, v]) => ({
      topicId,
      accuracy: v.total > 0 ? Math.round((v.correct / v.total) * 100) : 0,
    }))
    .sort((a, b) => a.accuracy - b.accuracy)
    .slice(0, 5);

  return NextResponse.json({
    certification: cert,
    totalQuestions,
    mastered: statusMap["mastered"] || 0,
    reviewing: statusMap["review"] || 0,
    learning: statusMap["learning"] || 0,
    unseen: totalQuestions - Object.values(statusMap).reduce((a, b) => a + b, 0),
    pendingDocs,
    examReady:
      totalQuestions - Object.values(statusMap).reduce((a, b) => a + b, 0) === 0 &&
      pendingDocs === 0,
    weakTopics,
  });
}
