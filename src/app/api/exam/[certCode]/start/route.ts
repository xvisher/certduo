import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function POST(
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
  });
  if (!cert) {
    return NextResponse.json({ error: "Certification not found" }, { status: 404 });
  }

  // Get all active questions for this certification, randomized
  const questions = await prisma.question.findMany({
    where: { certificationId: cert.id, isActive: true },
    select: {
      id: true,
      questionText: true,
      questionType: true,
      answers: true,
      source: true,
      sourceIcon: true,
      communityScore: true,
      difficulty: true,
    },
  });

  // Shuffle
  const shuffled = questions.sort(() => Math.random() - 0.5);

  // Create exam record
  const exam = await prisma.exam.create({
    data: {
      userId: session.userId,
      certificationId: cert.id,
      totalQuestions: shuffled.length,
      status: "in_progress",
    },
  });

  return NextResponse.json({
    examId: exam.id,
    questions: shuffled,
    totalQuestions: shuffled.length,
  });
}
