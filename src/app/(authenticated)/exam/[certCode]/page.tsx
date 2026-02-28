"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { QuestionCard } from "@/components/question/QuestionCard";
import { Button } from "@/components/ui/button";
import type { Question } from "@/types";

type Phase = "loading" | "confirm" | "exam" | "submitting";

interface ExamData {
  examId: string;
  questions: Question[];
  totalQuestions: number;
}

interface Answer {
  questionId: string;
  selectedAnswerIds: string[];
}

export default function ExamPage() {
  const params = useParams();
  const router = useRouter();
  const certCode = params.certCode as string;

  const [phase, setPhase] = useState<Phase>("loading");
  const [examData, setExamData] = useState<ExamData | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPhase("confirm");
  }, []);

  async function startExam() {
    setPhase("loading");
    try {
      const res = await fetch(`/api/exam/${certCode}/start`, { method: "POST" });
      if (!res.ok) {
        const data = await res.json();
        setError(data.error || "Failed to start exam");
        setPhase("confirm");
        return;
      }
      const data: ExamData = await res.json();
      setExamData(data);
      setPhase("exam");
    } catch {
      setError("Failed to start exam");
      setPhase("confirm");
    }
  }

  function handleAnswer(selectedAnswerIds: string[]) {
    if (!examData) return;
    const question = examData.questions[currentIndex];

    setAnswers((prev) => {
      const existing = prev.findIndex((a) => a.questionId === question.id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { questionId: question.id, selectedAnswerIds };
        return updated;
      }
      return [...prev, { questionId: question.id, selectedAnswerIds }];
    });

    // Auto-advance
    if (currentIndex < examData.questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }

  async function submitExam() {
    if (!examData) return;
    setPhase("submitting");

    const res = await fetch(`/api/exam/${certCode}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ examId: examData.examId, answers }),
    });

    if (res.ok) {
      const data = await res.json();
      router.push(`/exam/${certCode}/results/${data.examId}`);
    } else {
      setError("Failed to submit exam");
      setPhase("exam");
    }
  }

  if (phase === "loading" || phase === "submitting") {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="w-8 h-8 border-2 border-[#0078D4] border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-500">{phase === "submitting" ? "Submitting exam..." : "Loading..."}</p>
      </div>
    );
  }

  if (phase === "confirm") {
    return (
      <div className="text-center py-12">
        <div className="text-5xl mb-4">📝</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Final Exam</h1>
        <p className="text-gray-500 mb-2 text-sm">
          {certCode.toUpperCase()} · Pass threshold: 70%
        </p>
        <p className="text-gray-400 text-sm mb-6">
          All questions for this certification will be presented in random order.
        </p>
        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        <div className="flex gap-3 justify-center">
          <Button variant="outline" onClick={() => router.back()}>
            Not yet
          </Button>
          <Button onClick={startExam}>Start Exam →</Button>
        </div>
      </div>
    );
  }

  if (!examData) return null;

  const currentQuestion = examData.questions[currentIndex];
  const answeredCount = answers.length;
  const progress = Math.round((currentIndex / examData.totalQuestions) * 100);
  const hasAnswered = answers.some((a) => a.questionId === currentQuestion?.id);

  return (
    <div className="space-y-5">
      {/* Progress */}
      <div>
        <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
          <span className="font-bold text-[#0078D4]">{certCode.toUpperCase()} Exam</span>
          <span>{currentIndex + 1} / {examData.totalQuestions}</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-[#0078D4] rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {examData.questions.map((q, i) => {
          const answered = answers.some((a) => a.questionId === q.id);
          return (
            <button
              key={q.id}
              onClick={() => setCurrentIndex(i)}
              className={`w-8 h-8 shrink-0 rounded-lg text-xs font-semibold transition-colors
                ${i === currentIndex
                  ? "bg-[#0078D4] text-white"
                  : answered
                  ? "bg-green-100 text-green-700"
                  : "bg-gray-100 text-gray-500"
                }`}
            >
              {i + 1}
            </button>
          );
        })}
      </div>

      {/* Question */}
      {currentQuestion && (
        <QuestionCard
          question={currentQuestion}
          onAnswer={(ids) => handleAnswer(ids)}
          disabled={false}
        />
      )}

      {/* Submit when all answered */}
      {answeredCount === examData.totalQuestions && (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
          <p className="text-blue-800 font-medium mb-3 text-sm">
            All {answeredCount} questions answered. Ready to submit?
          </p>
          <Button onClick={submitExam} className="w-full">
            Submit Exam
          </Button>
        </div>
      )}

      {/* Jump to unanswered */}
      {answeredCount < examData.totalQuestions && hasAnswered && (
        <Button
          variant="outline"
          className="w-full"
          onClick={() => {
            const nextUnanswered = examData.questions.findIndex(
              (q) => !answers.some((a) => a.questionId === q.id)
            );
            if (nextUnanswered >= 0) setCurrentIndex(nextUnanswered);
          }}
        >
          Next Unanswered ({examData.totalQuestions - answeredCount} remaining)
        </Button>
      )}
    </div>
  );
}
