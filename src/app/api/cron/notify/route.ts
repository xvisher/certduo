import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { sendPushNotification } from "@/lib/push";

// This endpoint is called by a cron job every 15 minutes
// Vercel Cron: add to vercel.json

export async function GET(request: Request) {
  // Verify cron secret
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const now = new Date();
  const currentHour = now.getUTCHours().toString().padStart(2, "0");
  const currentMinute = now.getUTCMinutes();

  // Find users whose preferred notification time falls in this 15-min window
  // preferredTime is stored as "HH:mm" in user's local timezone
  // For simplicity, we match on UTC hour (production would need timezone conversion)
  const windowStart = currentMinute - 15;
  const windowEnd = currentMinute;

  const users = await prisma.user.findMany({
    where: {
      pushSubscriptions: { some: {} },
    },
    include: {
      pushSubscriptions: true,
      certifications: {
        where: { status: "active" },
        include: { certification: true },
      },
    },
  });

  let notified = 0;

  for (const user of users) {
    // Check if this is their preferred notification window
    const [prefHour, prefMinute] = (user.preferredTime || "08:00").split(":").map(Number);
    const prefMinNum = prefMinute || 0;

    const inWindow =
      prefHour === parseInt(currentHour) &&
      prefMinNum >= windowStart &&
      prefMinNum < windowEnd;

    if (!inWindow) continue;

    // Find questions due for review
    const now2 = new Date();
    const reviewCount = await prisma.userQuestionProgress.count({
      where: {
        userId: user.id,
        status: { in: ["learning", "review"] },
        nextReviewDate: { lte: now2 },
      },
    });

    const cert = user.certifications[0]?.certification;
    if (!cert) continue;

    const title = reviewCount > 0
      ? `🔄 Review time: ${cert.code}`
      : `☁️ Let's learn: ${cert.code}`;
    const body = reviewCount > 0
      ? `You have ${reviewCount} questions to review today`
      : `Continue your learning streak today`;

    for (const sub of user.pushSubscriptions) {
      await sendPushNotification(
        { endpoint: sub.endpoint, p256dh: sub.p256dh, auth: sub.auth },
        { title, body, url: `/learn/${cert.code.toLowerCase()}` }
      );
      notified++;
    }
  }

  return NextResponse.json({ success: true, notified });
}
