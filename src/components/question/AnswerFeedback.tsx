"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import type { Answer, DocLink, AnswerResult } from "@/types";

interface AnswerFeedbackProps {
  result: AnswerResult;
  question: { answers: Answer[]; questionText: string };
  onContinue: () => void;
  onDocConfirm?: (docUrl: string) => void;
}

export function AnswerFeedback({ result, question, onContinue, onDocConfirm }: AnswerFeedbackProps) {
  const { correct, correctAnswerIds, explanation, documentationLinks } = result;
  const answers = question.answers as Answer[];
  const correctAnswers = answers.filter((a) => correctAnswerIds.includes(a.id));

  return (
    <div
      className={`rounded-2xl border-2 p-6 ${
        correct
          ? "border-[#107C10] bg-green-50 answer-correct"
          : "border-[#D13438] bg-red-50 answer-incorrect"
      }`}
    >
      {/* Result header */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">{correct ? "✅" : "❌"}</span>
        <div>
          <div className={`font-bold text-lg ${correct ? "text-green-700" : "text-red-700"}`}>
            {correct ? "Correct!" : "Not quite"}
          </div>
          {!correct && (
            <div className="text-sm text-red-600">
              Correct: {correctAnswers.map((a) => a.text).join(", ")}
            </div>
          )}
        </div>
      </div>

      {/* Explanation */}
      {explanation && (
        <div className="bg-white rounded-xl p-4 mb-4 border border-gray-100">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            Explanation
          </div>
          <p className="text-gray-700 text-sm leading-relaxed">{explanation}</p>
        </div>
      )}

      {/* Documentation links (always shown) */}
      {documentationLinks && documentationLinks.length > 0 && (
        <div className="mb-4">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            {correct ? "Dive deeper" : "Read to understand"}
          </div>
          <div className="space-y-2">
            {(documentationLinks as DocLink[]).map((doc, i) => (
              <div key={i} className="flex items-center gap-2 bg-white rounded-xl p-3 border border-gray-100">
                <input
                  type="checkbox"
                  id={`doc-${i}`}
                  className="rounded accent-[#0078D4]"
                  onChange={(e) => e.target.checked && onDocConfirm?.(doc.url)}
                />
                <label htmlFor={`doc-${i}`} className="flex-1 text-sm">
                  <Link
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#0078D4] hover:underline"
                  >
                    {doc.title || doc.url}
                  </Link>
                  <span className="ml-1 text-gray-400 text-xs">→ Microsoft Learn</span>
                </label>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SM-2 status */}
      <div className="flex items-center justify-between">
        <div className="text-xs text-gray-500">
          Next review:{" "}
          {result.sm2Update.interval === 1
            ? "Tomorrow"
            : `In ${result.sm2Update.interval} days`}{" "}
          ({result.sm2Update.status})
        </div>
        <Button onClick={onContinue} size="sm">
          Continue →
        </Button>
      </div>
    </div>
  );
}
