import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { calculateSM2, getQualityScore } from "@/lib/sm2";
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
  const { questionId, selectedAnswerIds, timeElapsedMs } = await request.json();

  if (!questionId || !selectedAnswerIds) {
    return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
  }

  const question = await prisma.question.findUnique({
    where: { id: questionId },
    include: { topic: true },
  });

  if (!question) {
    return NextResponse.json({ error: "Question not found" }, { status: 404 });
  }

  // Check answer correctness
  const answers = question.answers as unknown as Answer[];
  const correctAnswerIds = answers.filter((a) => a.isCorrect).map((a) => a.id);
  const selectedIds = Array.isArray(selectedAnswerIds) ? selectedAnswerIds : [selectedAnswerIds];

  const isCorrect =
    correctAnswerIds.length === selectedIds.length &&
    correctAnswerIds.every((id) => selectedIds.includes(id));

  // Get or create progress record
  const existing = await prisma.userQuestionProgress.findUnique({
    where: {
      userId_questionId: { userId: session.userId, questionId },
    },
  });

  const quick = timeElapsedMs < 10000;
  const quality = getQualityScore(isCorrect, quick);

  const sm2 = calculateSM2(
    quality,
    existing?.easeFactor ?? 2.5,
    existing?.interval ?? 0,
    existing?.repetitions ?? 0
  );

  // Update progress
  await prisma.userQuestionProgress.upsert({
    where: {
      userId_questionId: { userId: session.userId, questionId },
    },
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
      questionId,
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

  // If incorrect, create documentation entries
  if (!isCorrect && question.documentationLinks && question.topicId) {
    const docLinks = question.documentationLinks as unknown as DocLink[];
    for (const link of docLinks) {
      await prisma.userDocumentation.upsert({
        where: {
          userId_topicId_docUrl: {
            userId: session.userId,
            topicId: question.topicId,
            docUrl: link.url,
          },
        },
        update: {},
        create: {
          userId: session.userId,
          topicId: question.topicId,
          docUrl: link.url,
          linkedQuestionId: questionId,
          status: "unread",
        },
      });
    }
  }

  // Update user's lastActiveAt and streak
  const user = await prisma.user.findUnique({ where: { id: session.userId } });
  if (user) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const lastActive = user.lastActiveAt ? new Date(user.lastActiveAt) : null;
    const lastActiveDay = lastActive ? new Date(lastActive) : null;
    if (lastActiveDay) lastActiveDay.setHours(0, 0, 0, 0);

    let streakCount = user.streakCount;
    if (!lastActiveDay || lastActiveDay.getTime() < today.getTime()) {
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      streakCount =
        lastActiveDay && lastActiveDay.getTime() === yesterday.getTime()
          ? streakCount + 1
          : 1;
    }

    await prisma.user.update({
      where: { id: session.userId },
      data: { lastActiveAt: new Date(), streakCount },
    });
  }

  return NextResponse.json({
    correct: isCorrect,
    correctAnswerIds,
    explanation: question.explanation,
    documentationLinks: question.documentationLinks,
    sm2Update: {
      status: sm2.status,
      nextReviewDate: sm2.nextReviewDate.toISOString(),
      interval: sm2.interval,
    },
  });
}
