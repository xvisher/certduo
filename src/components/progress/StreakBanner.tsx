"use client";

import { formatRelativeDate } from "@/lib/utils";

interface StreakBannerProps {
  streakCount: number;
  lastActiveAt?: string | Date | null;
}

export function StreakBanner({ streakCount, lastActiveAt }: StreakBannerProps) {
  return (
    <div className="flex items-center gap-3 bg-orange-50 border border-orange-100 rounded-2xl px-5 py-4">
      <span className="text-3xl streak-fire">🔥</span>
      <div>
        <div className="font-bold text-orange-700 text-xl">{streakCount} day streak</div>
        {lastActiveAt && (
          <div className="text-orange-500 text-sm">
            Last active: {formatRelativeDate(lastActiveAt)}
          </div>
        )}
      </div>
    </div>
  );
}
