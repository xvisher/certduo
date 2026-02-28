import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function POST(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { endpoint, p256dh, auth } = await request.json();

  if (!endpoint || !p256dh || !auth) {
    return NextResponse.json({ error: "Missing subscription data" }, { status: 400 });
  }

  await prisma.pushSubscription.upsert({
    where: { id: session.userId + endpoint },
    update: { p256dh, auth },
    create: {
      id: session.userId + endpoint,
      userId: session.userId,
      endpoint,
      p256dh,
      auth,
    },
  });

  return NextResponse.json({ success: true });
}
