"use client";

import Link from "next/link";
import { ProgressRing } from "@/components/progress/ProgressRing";
import { Badge } from "@/components/ui/badge";
import type { Certification } from "@/types";

const CERT_EMOJIS: Record<string, string> = {
  "AZ-900": "☁️",
  "AZ-104": "⚙️",
  "MD-102": "💻",
  "MS-102": "🏢",
};

const CERT_COLORS: Record<string, string> = {
  "AZ-900": "from-blue-50 to-sky-50",
  "AZ-104": "from-indigo-50 to-blue-50",
  "MD-102": "from-violet-50 to-purple-50",
  "MS-102": "from-teal-50 to-emerald-50",
};

interface CertificationCardProps {
  certification: Certification;
  enrollment?: {
    status: string;
    percentComplete: number;
    completedAt?: string | null;
  } | null;
  questionCount?: number;
  onEnroll?: () => void;
  enrolled?: boolean;
}

export function CertificationCard({
  certification,
  enrollment,
  questionCount,
  onEnroll,
  enrolled,
}: CertificationCardProps) {
  const emoji = CERT_EMOJIS[certification.code] || "📋";
  const gradient = CERT_COLORS[certification.code] || "from-gray-50 to-slate-50";
  const percent = enrollment?.percentComplete || 0;
  const isCompleted = enrollment?.status === "completed";

  return (
    <div className={`rounded-2xl bg-gradient-to-br ${gradient} border border-white/80 shadow-sm overflow-hidden`}>
      <div className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="text-3xl mb-2">{emoji}</div>
            <div className="font-bold text-[#0078D4] text-sm mb-0.5">{certification.code}</div>
            <div className="font-semibold text-gray-900 text-base leading-tight">
              {certification.name}
            </div>
          </div>
          {enrollment && (
            <ProgressRing percent={percent} size={64} strokeWidth={6} />
          )}
        </div>

        {certification.description && (
          <p className="text-gray-500 text-sm leading-relaxed mb-4 line-clamp-2">
            {certification.description}
          </p>
        )}

        <div className="flex items-center gap-2 mb-4">
          {questionCount !== undefined && (
            <Badge variant="default">{questionCount} questions</Badge>
          )}
          {isCompleted && <Badge variant="success">Completed ✓</Badge>}
          {enrollment && !isCompleted && <Badge variant="learning">In progress</Badge>}
        </div>

        {enrollment ? (
          <Link
            href={`/learn/${certification.code.toLowerCase()}`}
            className="block w-full text-center bg-[#0078D4] text-white py-2.5 rounded-xl font-semibold text-sm hover:bg-blue-700 transition-colors"
          >
            {isCompleted ? "Review" : "Continue Learning →"}
          </Link>
        ) : (
          <button
            onClick={onEnroll}
            className="w-full text-center border border-[#0078D4] text-[#0078D4] py-2.5 rounded-xl font-semibold text-sm hover:bg-blue-50 transition-colors"
          >
            Start Learning
          </button>
        )}
      </div>
    </div>
  );
}
