"use client";

import { useState, useEffect } from "react";
import { SourceBadge } from "./SourceBadge";
import { Button } from "@/components/ui/button";
import type { Question, Answer } from "@/types";

interface QuestionCardProps {
  question: Question;
  onAnswer: (selectedAnswerIds: string[], timeElapsedMs: number) => void;
  disabled?: boolean;
}

export function QuestionCard({ question, onAnswer, disabled }: QuestionCardProps) {
  const [selected, setSelected] = useState<string[]>([]);
  const [startTime] = useState(Date.now());
  const isMultiple = question.questionType === "MULTIPLE_CHOICE";

  useEffect(() => {
    setSelected([]);
  }, [question.id]);

  function toggleAnswer(answerId: string) {
    if (disabled) return;
    if (isMultiple) {
      setSelected((prev) =>
        prev.includes(answerId) ? prev.filter((id) => id !== answerId) : [...prev, answerId]
      );
    } else {
      setSelected([answerId]);
    }
  }

  function handleSubmit() {
    if (selected.length === 0) return;
    onAnswer(selected, Date.now() - startTime);
  }

  const answers = question.answers as Answer[];

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-5">
        <SourceBadge source={question.source} communityScore={question.communityScore} />
        {isMultiple && (
          <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-lg">
            Select all that apply
          </span>
        )}
      </div>

      {/* Question */}
      <p className="text-gray-900 font-medium text-base leading-relaxed mb-6">
        {question.questionText}
      </p>

      {/* Answers */}
      <div className="space-y-3 mb-6">
        {answers.map((answer) => {
          const isSelected = selected.includes(answer.id);
          return (
            <button
              key={answer.id}
              onClick={() => toggleAnswer(answer.id)}
              disabled={disabled}
              className={`w-full text-left px-4 py-3.5 rounded-xl border-2 transition-all text-sm leading-relaxed
                ${isSelected
                  ? "border-[#0078D4] bg-blue-50 text-[#0078D4] font-medium"
                  : "border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700"
                }
                disabled:cursor-not-allowed`}
            >
              <span className="flex items-start gap-3">
                <span
                  className={`mt-0.5 w-5 h-5 shrink-0 rounded-full border-2 flex items-center justify-center
                  ${isSelected ? "border-[#0078D4] bg-[#0078D4]" : "border-gray-300"}`}
                >
                  {isSelected && (
                    <span className="w-2 h-2 rounded-full bg-white" />
                  )}
                </span>
                {answer.text}
              </span>
            </button>
          );
        })}
      </div>

      {/* Submit */}
      <Button
        onClick={handleSubmit}
        disabled={selected.length === 0 || disabled}
        className="w-full"
      >
        Submit Answer
      </Button>
    </div>
  );
}
