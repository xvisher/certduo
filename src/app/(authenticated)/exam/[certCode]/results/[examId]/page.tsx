import { notFound } from "next/navigation";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { ExamResults } from "@/components/exam/ExamResults";
import type { Question, DocLink } from "@/types";

export default async function ExamResultsPage({
  params,
}: {
  params: Promise<{ certCode: string; examId: string }>;
}) {
  const session = await getSession();
  if (!session) return null;

  const { certCode, examId } = await params;

  const exam = await prisma.exam.findUnique({
    where: { id: examId, userId: session.userId },
    include: { certification: true },
  });

  if (!exam || !exam.score) notFound();

  // Fetch incorrect question details
  const answersData = (exam.answers as Array<{
    questionId: string;
    selectedAnswerIds: string[];
    isCorrect: boolean;
  }>) || [];

  const incorrectAnswers = answersData.filter((a) => !a.isCorrect);
  const incorrectQuestions = await Promise.all(
    incorrectAnswers.map(async (a) => {
      const q = await prisma.question.findUnique({ where: { id: a.questionId } });
      if (!q) return null;
      return {
        question: q as unknown as Question,
        selectedAnswerIds: a.selectedAnswerIds,
        documentationLinks: q.documentationLinks as unknown as DocLink[],
      };
    })
  );

  const validIncorrect = incorrectQuestions.filter(Boolean) as NonNullable<
    (typeof incorrectQuestions)[0]
  >[];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Exam Results</h1>
        <p className="text-gray-500 mt-1 text-sm">{exam.certification.name}</p>
      </div>

      <ExamResults
        score={exam.score}
        passed={exam.passed || false}
        totalQuestions={exam.totalQuestions}
        correctAnswers={exam.correctAnswers}
        incorrectQuestions={validIncorrect}
        certCode={certCode}
        examId={examId}
      />
    </div>
  );
}
