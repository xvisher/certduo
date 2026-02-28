import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { calculateSM2 } from "@/lib/sm2";
import type { Answer, DocLink } from "@/types";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ certCode: string }> }
) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { certCode } = await params;
  const { examId, answers } = await request.json();

  if (!examId || !answers) {
    return NextResponse.json({ error: "Missing examId or answers" }, { status: 400 });
  }

  const exam = await prisma.exam.findUnique({
    where: { id: examId, userId: session.userId },
  });
  if (!exam) {
    return NextResponse.json({ error: "Exam not found" }, { status: 404 });
  }
  if (exam.status === "completed") {
    return NextResponse.json({ error: "Exam already completed" }, { status: 400 });
  }

  // Grade each answer
  const questionIds = (answers as { questionId: string; selectedAnswerIds: string[] }[]).map(
    (a) => a.questionId
  );

  const questions = await prisma.question.findMany({
    where: { id: { in: questionIds } },
  });
  const questionMap = new Map(questions.map((q) => [q.id, q]));

  let correctCount = 0;
  const gradedAnswers: Array<{
    questionId: string;
    selectedAnswerIds: string[];
    isCorrect: boolean;
    correctAnswerIds: string[];
  }> = [];

  const incorrectQuestions: Array<{
    question: (typeof questions)[0];
    selectedAnswerIds: string[];
    documentationLinks?: DocLink[];
  }> = [];

  for (const answer of answers as { questionId: string; selectedAnswerIds: string[] }[]) {
    const q = questionMap.get(answer.questionId);
    if (!q) continue;

    const qAnswers = q.answers as unknown as Answer[];
    const correctIds = qAnswers.filter((a) => a.isCorrect).map((a) => a.id);
    const selectedIds = Array.isArray(answer.selectedAnswerIds)
      ? answer.selectedAnswerIds
      : [answer.selectedAnswerIds];

    const isCorrect =
      correctIds.length === selectedIds.length &&
      correctIds.every((id) => selectedIds.includes(id));

    if (isCorrect) correctCount++;
    else {
      incorrectQuestions.push({
        question: q,
        selectedAnswerIds: selectedIds,
        documentationLinks: q.documentationLinks as unknown as DocLink[],
      });
    }

    gradedAnswers.push({ questionId: answer.questionId, selectedAnswerIds: selectedIds, isCorrect, correctAnswerIds: correctIds });

    // Update SM-2 progress for each question
    const existing = await prisma.userQuestionProgress.findUnique({
      where: { userId_questionId: { userId: session.userId, questionId: answer.questionId } },
    });

    const quality = isCorrect ? 4 : 1;
    const sm2 = calculateSM2(
      quality,
      existing?.easeFactor ?? 2.5,
      existing?.interval ?? 0,
      existing?.repetitions ?? 0
    );

    await prisma.userQuestionProgress.upsert({
      where: { userId_questionId: { userId: session.userId, questionId: answer.questionId } },
      update: {
        status: sm2.status,
        easeFactor: sm2.easeFactor,
        interval: sm2.interval,
        repetitions: sm2.repetitions,
        nextReviewDate: sm2.nextReviewDate,
        lastAnsweredAt: new Date(),
        lastAnswerCorrect: isCorrect,
        timesAnswered: { increment: 1 },
        timesCorrect: isCorrect ? { increment: 1 } : undefined,
      },
      create: {
        userId: session.userId,
        questionId: answer.questionId,
        status: sm2.status,
        easeFactor: sm2.easeFactor,
        interval: sm2.interval,
        repetitions: sm2.repetitions,
        nextReviewDate: sm2.nextReviewDate,
        lastAnsweredAt: new Date(),
        lastAnswerCorrect: isCorrect,
        timesAnswered: 1,
        timesCorrect: isCorrect ? 1 : 0,
      },
    });

    // Create doc entries for incorrect answers
    if (!isCorrect && q.documentationLinks && q.topicId) {
      const docLinks = q.documentationLinks as unknown as DocLink[];
      for (const link of docLinks) {
        await prisma.userDocumentation.upsert({
          where: {
            userId_topicId_docUrl: {
              userId: session.userId,
              topicId: q.topicId,
              docUrl: link.url,
            },
          },
          update: {},
          create: {
            userId: session.userId,
            topicId: q.topicId,
            docUrl: link.url,
            linkedQuestionId: q.id,
            status: "unread",
          },
        });
      }
    }
  }

  const score = (correctCount / questions.length) * 100;
  const passed = score >= 70;

  // Update exam record
  await prisma.exam.update({
    where: { id: examId },
    data: {
      score,
      passed,
      correctAnswers: correctCount,
      status: "completed",
      completedAt: new Date(),
      answers: gradedAnswers,
    },
  });

  // If passed, mark certification as completed
  if (passed) {
    const cert = await prisma.certification.findUnique({
      where: { code: certCode.toUpperCase() },
    });
    if (cert) {
      await prisma.userCertification.updateMany({
        where: { userId: session.userId, certificationId: cert.id },
        data: { status: "completed", completedAt: new Date(), percentComplete: 100 },
      });
    }
  }

  return NextResponse.json({
    examId,
    score: Math.round(score * 10) / 10,
    passed,
    totalQuestions: questions.length,
    correctAnswers: correctCount,
    incorrectQuestions: incorrectQuestions.map((iq) => ({
      question: iq.question,
      selectedAnswerIds: iq.selectedAnswerIds,
      documentationLinks: iq.documentationLinks,
    })),
    completedAt: new Date().toISOString(),
  });
}
