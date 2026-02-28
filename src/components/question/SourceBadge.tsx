import { cn } from "@/lib/utils";
import type { QuestionSource } from "@/types";

interface SourceBadgeProps {
  source: QuestionSource;
  communityScore?: number | null;
  className?: string;
}

export function SourceBadge({ source, communityScore, className }: SourceBadgeProps) {
  if (source === "MICROSOFT") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 bg-[#0078D4] text-white rounded-lg px-2.5 py-1 text-xs font-semibold",
          className
        )}
      >
        <span className="font-bold">M</span>
        <span>Microsoft</span>
      </span>
    );
  }

  if (source === "EXAMTOPICS") {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 bg-gray-700 text-white rounded-lg px-2.5 py-1 text-xs font-semibold",
          className
        )}
      >
        <span>🌐</span>
        <span>ExamTopics</span>
        {communityScore != null && (
          <span className="bg-white/20 rounded px-1">{Math.round(communityScore)}% agree</span>
        )}
      </span>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 bg-purple-600 text-white rounded-lg px-2.5 py-1 text-xs font-semibold",
        className
      )}
    >
      <span>👥</span>
      <span>Community</span>
    </span>
  );
}
