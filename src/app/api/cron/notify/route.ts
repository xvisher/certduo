import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { sendPushNotification } from "@/lib/push";

// Called daily at 9am UTC by Vercel Cron.
// Notifies all users who have push subscriptions and an active certification.

export async function GET(request: Request) {
  // Vercel automatically sets CRON_SECRET and passes it in the Authorization header.
  const authHeader = request.headers.get("authorization");
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const now = new Date();

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
    const cert = user.certifications[0]?.certification;
    if (!cert) continue;

    const reviewCount = await prisma.userQuestionProgress.count({
      where: {
        userId: user.id,
        status: { in: ["learning", "review"] },
        nextReviewDate: { lte: now },
      },
    });

    const title = reviewCount > 0
      ? `🔄 Review time: ${cert.code}`
      : `☁️ Let's learn: ${cert.code}`;
    const body = reviewCount > 0
      ? `You have ${reviewCount} questions due for review`
      : `Keep your streak going — continue learning today`;

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
