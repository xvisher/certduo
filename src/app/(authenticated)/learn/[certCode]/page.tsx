"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { QuestionCard } from "@/components/question/QuestionCard";
import { AnswerFeedback } from "@/components/question/AnswerFeedback";
import { SimpleMarkdown } from "@/components/SimpleMarkdown";
import { Button } from "@/components/ui/button";
import type { Question, Topic, AnswerResult } from "@/types";

// ─── Types ───────────────────────────────────────────────────────────────────

type Phase = "loading" | "setup" | "reading" | "quiz" | "feedback" | "complete" | "empty";

interface SessionData {
  topic: Topic | null;
  questions: Question[];
  reviewCount: number;
  questionCount: number;
}

interface TimeOption {
  minutes: number;
  questions: number;
  label: string;
  emoji: string;
  description: string;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const TIME_OPTIONS: TimeOption[] = [
  {
    minutes: 5,
    questions: 2,
    label: "Quick Session",
    emoji: "⚡",
    description: "Fast review of key concepts",
  },
  {
    minutes: 10,
    questions: 3,
    label: "Standard",
    emoji: "📚",
    description: "Balanced reading + practice",
  },
  {
    minutes: 15,
    questions: 5,
    label: "Deep Dive",
    emoji: "🎯",
    description: "Thorough study with more questions",
  },
];

// ─── Component ───────────────────────────────────────────────────────────────

export default function LearnPage() {
  const params = useParams();
  const certCode = params.certCode as string;

  const [phase, setPhase] = useState<Phase>("loading");
  const [session, setSession] = useState<SessionData | null>(null);
  const [selectedTime, setSelectedTime] = useState<TimeOption | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [sessionStats, setSessionStats] = useState({ answered: 0, correct: 0 });
  const [error, setError] = useState<string | null>(null);

  // Countdown timer
  const [timeRemaining, setTimeRemaining] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Initial load: get topic info for setup screen ─────────────────────────
  const loadSession = useCallback(async () => {
    setPhase("loading");
    try {
      const res = await fetch(`/api/learn/${certCode}/session?questionCount=2`);
      if (!res.ok) {
        const data = await res.json();
        setError(data.error || "Failed to load session");
        setPhase("empty");
        return;
      }
      const data: SessionData = await res.json();
      setSession(data);
      setPhase("setup");
    } catch {
      setError("Failed to load learning session");
      setPhase("empty");
    }
  }, [certCode]);

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  // ── Time option selected → fetch questions + start reading ────────────────
  async function handleTimeSelect(option: TimeOption) {
    setSelectedTime(option);
    setPhase("loading");

    try {
      const res = await fetch(
        `/api/learn/${certCode}/session?questionCount=${option.questions}`
      );
      if (!res.ok) {
        setError("Failed to load questions");
        setPhase("empty");
        return;
      }
      const data: SessionData = await res.json();

      if (!data.questions || data.questions.length === 0) {
        setPhase("empty");
        return;
      }

      setSession(data);
      setCurrentIndex(0);
      setTimeRemaining(option.minutes * 60);
      setPhase(data.topic?.content ? "reading" : "quiz");
    } catch {
      setError("Failed to load session");
      setPhase("empty");
    }
  }

  // ── Countdown timer ───────────────────────────────────────────────────────
  useEffect(() => {
    if (phase === "reading" && timeRemaining > 0) {
      timerRef.current = setInterval(() => {
        setTimeRemaining((t) => {
          if (t <= 1) {
            clearInterval(timerRef.current!);
            return 0;
          }
          return t - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase]);

  function formatTime(seconds: number) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  function startQuiz() {
    if (timerRef.current) clearInterval(timerRef.current);
    setPhase("quiz");
  }

  // ── Answer submission ─────────────────────────────────────────────────────
  async function handleAnswer(selectedAnswerIds: string[], timeElapsedMs: number) {
    if (!session) return;
    const question = session.questions[currentIndex];

    try {
      const res = await fetch(`/api/learn/${certCode}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ questionId: question.id, selectedAnswerIds, timeElapsedMs }),
      });
      const data: AnswerResult = await res.json();
      setResult(data);
      setSessionStats((prev) => ({
        answered: prev.answered + 1,
        correct: prev.correct + (data.correct ? 1 : 0),
      }));
      setPhase("feedback");
    } catch {
      setError("Failed to submit answer");
    }
  }

  function handleContinue() {
    if (!session) return;
    const nextIndex = currentIndex + 1;
    if (nextIndex >= session.questions.length) {
      setPhase("complete");
    } else {
      setCurrentIndex(nextIndex);
      setResult(null);
      setPhase("quiz");
    }
  }

  const currentQuestion = session?.questions[currentIndex];
  const progress = session
    ? Math.round(
        ((currentIndex + (phase === "complete" ? 1 : 0)) /
          session.questions.length) *
          100
      )
    : 0;

  // ─── LOADING ─────────────────────────────────────────────────────────────
  if (phase === "loading") {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-[#0078D4] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // ─── EMPTY / ERROR ────────────────────────────────────────────────────────
  if (phase === "empty") {
    return (
      <div className="text-center py-16">
        <div className="text-5xl mb-4">🎉</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          {error ? "Session Error" : "All caught up!"}
        </h2>
        <p className="text-gray-500 mb-6">
          {error ||
            "No questions due for review. Come back tomorrow to continue your streak!"}
        </p>
        <Link href="/dashboard">
          <Button>Back to Dashboard</Button>
        </Link>
      </div>
    );
  }

  // ─── SETUP ───────────────────────────────────────────────────────────────
  if (phase === "setup") {
    const topicTitle = session?.topic?.title ?? certCode.toUpperCase();
    return (
      <div className="max-w-lg mx-auto space-y-6 py-4">
        <div className="text-center">
          <div className="text-sm font-semibold text-[#0078D4] uppercase tracking-wide mb-1">
            {certCode.toUpperCase()} · Ready to learn?
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{topicTitle}</h1>
          <p className="text-gray-500 text-sm mt-2">
            Choose how long you want to study today
          </p>
        </div>

        <div className="grid gap-4">
          {TIME_OPTIONS.map((option) => (
            <button
              key={option.minutes}
              onClick={() => handleTimeSelect(option)}
              className="group w-full bg-white border-2 border-gray-100 hover:border-[#0078D4] rounded-2xl p-5 text-left transition-all duration-200 hover:shadow-md active:scale-[0.99]"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{option.emoji}</span>
                  <div>
                    <div className="font-semibold text-gray-900 group-hover:text-[#0078D4] transition-colors">
                      {option.label}
                    </div>
                    <div className="text-gray-500 text-sm">{option.description}</div>
                  </div>
                </div>
                <div className="text-right shrink-0 ml-4">
                  <div className="text-[#0078D4] font-bold text-lg">
                    {option.minutes} min
                  </div>
                  <div className="text-gray-400 text-xs">
                    {option.questions} question{option.questions > 1 ? "s" : ""}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
                <span className="flex items-center gap-1">📖 Read in-app content</span>
                <span className="flex items-center gap-1">
                  ❓ {option.questions} quiz question{option.questions > 1 ? "s" : ""}
                </span>
                <span className="flex items-center gap-1">🧠 SM-2 review</span>
              </div>
            </button>
          ))}
        </div>

        <div className="text-center">
          <Link href="/dashboard" className="text-sm text-gray-400 hover:text-gray-600">
            ← Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  // ─── COMPLETE ────────────────────────────────────────────────────────────
  if (phase === "complete") {
    const accuracy =
      sessionStats.answered > 0
        ? Math.round((sessionStats.correct / sessionStats.answered) * 100)
        : 0;

    return (
      <div className="text-center py-8 max-w-sm mx-auto">
        <div className="text-5xl mb-4">
          {accuracy >= 80 ? "⭐" : accuracy >= 50 ? "💪" : "📖"}
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-1">Session Complete!</h2>
        <p className="text-gray-500 text-sm mb-6">
          {selectedTime?.label} · {selectedTime?.minutes} min session
        </p>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6 text-left">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {sessionStats.answered}
              </div>
              <div className="text-gray-500 text-xs">Questions</div>
            </div>
            <div>
              <div
                className="text-2xl font-bold"
                style={{
                  color:
                    accuracy >= 70
                      ? "#107C10"
                      : accuracy >= 50
                      ? "#FF8C00"
                      : "#D13438",
                }}
              >
                {accuracy}%
              </div>
              <div className="text-gray-500 text-xs">Accuracy</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-500">🔥</div>
              <div className="text-gray-500 text-xs">Streak</div>
            </div>
          </div>
        </div>

        <div className="flex gap-3 justify-center flex-wrap">
          <Link href={`/learn/${certCode}/review`}>
            <Button variant="outline">Review Docs</Button>
          </Link>
          <button
            onClick={() => {
              setPhase("setup");
              setSessionStats({ answered: 0, correct: 0 });
              setCurrentIndex(0);
            }}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium text-sm transition-colors"
          >
            Another Session
          </button>
          <Link href="/dashboard">
            <Button>See Progress →</Button>
          </Link>
        </div>
      </div>
    );
  }

  // ─── READING + QUIZ + FEEDBACK ────────────────────────────────────────────
  return (
    <div className="space-y-5 max-w-2xl mx-auto">
      {/* Progress bar */}
      <div>
        <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
          <span className="font-medium text-[#0078D4]">
            {certCode.toUpperCase()} · {selectedTime?.label}
          </span>
          {phase !== "reading" && (
            <span>
              {currentIndex + 1}/{session?.questions.length}
            </span>
          )}
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-[#0078D4] rounded-full transition-all duration-500"
            style={{ width: phase === "reading" ? "2%" : `${progress}%` }}
          />
        </div>
      </div>

      {/* ── READING ────────────────────────────────────────────────────── */}
      {phase === "reading" && session?.topic && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50">
            <div>
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                📖 Reading
              </div>
              <h2 className="text-lg font-bold text-gray-900 mt-0.5">
                {session.topic.title}
              </h2>
            </div>
            {/* Timer */}
            <div
              className={`flex flex-col items-center px-4 py-2 rounded-xl min-w-[64px] ${
                timeRemaining === 0
                  ? "bg-green-100 text-green-700"
                  : timeRemaining < 60
                  ? "bg-orange-100 text-orange-700"
                  : "bg-blue-50 text-[#0078D4]"
              }`}
            >
              <span className="text-xl font-bold font-mono leading-none">
                {timeRemaining === 0 ? "✓" : formatTime(timeRemaining)}
              </span>
              <span className="text-[10px] opacity-60 mt-0.5">
                {timeRemaining === 0 ? "ready!" : "left"}
              </span>
            </div>
          </div>

          {/* Scrollable article */}
          <div className="px-6 py-5 max-h-[58vh] overflow-y-auto">
            {session.topic.content ? (
              <SimpleMarkdown content={session.topic.content} />
            ) : (
              <p className="text-gray-500 italic">
                No in-app content for this topic yet.{" "}
                {session.topic.msLearnUrl && (
                  <a
                    href={session.topic.msLearnUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#0078D4] underline"
                  >
                    Read on Microsoft Learn →
                  </a>
                )}
              </p>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-between gap-3 flex-wrap">
            <div className="text-xs text-gray-400">
              After reading:{" "}
              <strong>
                {selectedTime?.questions} question
                {(selectedTime?.questions ?? 0) > 1 ? "s" : ""}
              </strong>
            </div>
            <div className="flex items-center gap-3">
              {session.topic.msLearnUrl && (
                <a
                  href={session.topic.msLearnUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-gray-400 hover:text-[#0078D4] transition-colors"
                >
                  Open on MS Learn ↗
                </a>
              )}
              <Button onClick={startQuiz}>
                {timeRemaining > 0
                  ? `I've finished reading →`
                  : `Start Quiz (${selectedTime?.questions}q) →`}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* ── QUIZ ───────────────────────────────────────────────────────── */}
      {phase === "quiz" && currentQuestion && (
        <QuestionCard
          question={currentQuestion}
          onAnswer={handleAnswer}
          disabled={false}
        />
      )}

      {/* ── FEEDBACK ───────────────────────────────────────────────────── */}
      {phase === "feedback" && result && currentQuestion && (
        <>
          <QuestionCard
            question={currentQuestion}
            onAnswer={handleAnswer}
            disabled={true}
          />
          <AnswerFeedback
            result={result}
            question={currentQuestion}
            onContinue={handleContinue}
          />
        </>
      )}
    </div>
  );
}
