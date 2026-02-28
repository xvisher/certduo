import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ certCode: string }> }
) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { certCode } = await params;

  // Read questionCount from query string (2 | 3 | 5, default 5)
  const searchParams = request.nextUrl.searchParams;
  const rawCount = parseInt(searchParams.get("questionCount") ?? "5", 10);
  const questionCount = [2, 3, 5].includes(rawCount) ? rawCount : 5;

  const cert = await prisma.certification.findUnique({
    where: { code: certCode.toUpperCase() },
  });
  if (!cert) {
    return NextResponse.json({ error: "Certification not found" }, { status: 404 });
  }

  const enrollment = await prisma.userCertification.findUnique({
    where: {
      userId_certificationId: { userId: session.userId, certificationId: cert.id },
    },
  });
  if (!enrollment) {
    return NextResponse.json({ error: "Not enrolled" }, { status: 403 });
  }

  // Get questions due for review (SM-2 scheduling)
  const now = new Date();
  const reviewDue = await prisma.userQuestionProgress.findMany({
    where: {
      userId: session.userId,
      question: { certificationId: cert.id, isActive: true },
      status: { in: ["learning", "review"] },
      nextReviewDate: { lte: now },
    },
    include: { question: { include: { topic: true } } },
    orderBy: { nextReviewDate: "asc" },
    take: questionCount,
  });

  // Get new/unseen questions
  const seenQuestionIds = await prisma.userQuestionProgress.findMany({
    where: { userId: session.userId, question: { certificationId: cert.id } },
    select: { questionId: true },
  });
  const seenIds = seenQuestionIds.map((q) => q.questionId);

  const newQuestions = await prisma.question.findMany({
    where: {
      certificationId: cert.id,
      isActive: true,
      id: { notIn: seenIds },
    },
    include: { topic: true },
    take: Math.max(0, questionCount - reviewDue.length),
    orderBy: [{ moduleId: "asc" }, { difficulty: "asc" }],
  });

  // Determine current topic (prefer topic of first question, then module default)
  const firstQuestion = reviewDue[0]?.question ?? newQuestions[0];
  let topic = firstQuestion?.topic ?? null;

  if (!topic) {
    const currentModule = enrollment.currentModuleId
      ? await prisma.module.findUnique({
          where: { id: enrollment.currentModuleId },
          include: { topics: { orderBy: { orderIndex: "asc" }, take: 1 } },
        })
      : await prisma.module.findFirst({
          where: { certificationId: cert.id },
          orderBy: { orderIndex: "asc" },
          include: { topics: { orderBy: { orderIndex: "asc" }, take: 1 } },
        });
    topic = currentModule?.topics[0] ?? null;
  }

  // Check free tier limit
  const user = await prisma.user.findUnique({ where: { id: session.userId } });
  let questionsToReturn = [
    ...reviewDue.map((p) => p.question),
    ...newQuestions,
  ];

  if (user?.tier === "free") {
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    const todayAnswered = await prisma.userQuestionProgress.count({
      where: {
        userId: session.userId,
        lastAnsweredAt: { gte: todayStart },
      },
    });
    const remaining = Math.max(0, 10 - todayAnswered);
    questionsToReturn = questionsToReturn.slice(0, remaining);
  }

  return NextResponse.json({
    topic,
    questions: questionsToReturn.slice(0, questionCount),
    reviewCount: reviewDue.length,
    totalPending: reviewDue.length + (seenIds.length === 0 ? newQuestions.length : 0),
    questionCount,
  });
}
