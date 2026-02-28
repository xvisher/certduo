import { NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const user = await prisma.user.findUnique({
    where: { id: session.userId },
    select: { streakCount: true, lastActiveAt: true },
  });

  // Get activity heatmap (last 90 days)
  const ninetyDaysAgo = new Date();
  ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);

  const activity = await prisma.userQuestionProgress.findMany({
    where: {
      userId: session.userId,
      lastAnsweredAt: { gte: ninetyDaysAgo },
    },
    select: { lastAnsweredAt: true },
  });

  // Group by date
  const heatmap: Record<string, number> = {};
  for (const record of activity) {
    if (record.lastAnsweredAt) {
      const date = record.lastAnsweredAt.toISOString().split("T")[0];
      heatmap[date] = (heatmap[date] || 0) + 1;
    }
  }

  return NextResponse.json({
    streakCount: user?.streakCount || 0,
    lastActiveAt: user?.lastActiveAt,
    heatmap,
  });
}
