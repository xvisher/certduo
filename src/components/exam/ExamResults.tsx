"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import type { Question, DocLink } from "@/types";

interface IncorrectQuestion {
  question: Question;
  selectedAnswerIds: string[];
  documentationLinks?: DocLink[];
}

interface ExamResultsProps {
  score: number;
  passed: boolean;
  totalQuestions: number;
  correctAnswers: number;
  incorrectQuestions: IncorrectQuestion[];
  certCode: string;
  examId: string;
}

export function ExamResults({
  score,
  passed,
  totalQuestions,
  correctAnswers,
  incorrectQuestions,
  certCode,
}: ExamResultsProps) {
  return (
    <div className="max-w-2xl mx-auto">
      {/* Score card */}
      <div
        className={`rounded-3xl p-8 mb-6 text-center ${
          passed
            ? "bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200"
            : "bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200"
        }`}
      >
        <div className="text-5xl mb-4">{passed ? "🎉" : "📖"}</div>
        <div className={`text-5xl font-bold mb-2 ${passed ? "text-green-700" : "text-red-700"}`}>
          {Math.round(score)}%
        </div>
        <div className={`text-lg font-semibold mb-1 ${passed ? "text-green-700" : "text-red-700"}`}>
          {passed ? "Passed!" : "Not passed yet"}
        </div>
        <div className="text-gray-500 text-sm">
          {correctAnswers} / {totalQuestions} correct · Pass threshold: 70%
        </div>
        {passed && (
          <div className="mt-4 text-green-600 font-medium">
            Certification marked as completed. Great work!
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: "Score", value: `${Math.round(score)}%`, color: passed ? "text-green-600" : "text-red-600" },
          { label: "Correct", value: correctAnswers.toString(), color: "text-gray-900" },
          { label: "Incorrect", value: (totalQuestions - correctAnswers).toString(), color: "text-gray-900" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-2xl border border-gray-100 p-4 text-center">
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
            <div className="text-gray-500 text-xs mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Incorrect questions */}
      {incorrectQuestions.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">
            Questions to review ({incorrectQuestions.length})
          </h3>
          <div className="space-y-3 mb-6">
            {incorrectQuestions.slice(0, 10).map((iq) => (
              <div key={iq.question.id} className="bg-white rounded-2xl border border-gray-100 p-4">
                <p className="text-sm text-gray-700 font-medium mb-2 line-clamp-2">
                  {iq.question.questionText}
                </p>
                {iq.documentationLinks && iq.documentationLinks.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {iq.documentationLinks.map((doc, i) => (
                      <Link
                        key={i}
                        href={doc.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-[#0078D4] hover:underline bg-blue-50 px-2 py-1 rounded-lg"
                      >
                        📖 {doc.title || "Read more"}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <Link href={`/learn/${certCode.toLowerCase()}/review`} className="flex-1">
          <Button variant="outline" className="w-full">
            Review Documentation
          </Button>
        </Link>
        <Link href="/dashboard" className="flex-1">
          <Button className="w-full">Back to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
