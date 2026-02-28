import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const user = await prisma.user.findUnique({
    where: { id: session.userId },
    select: {
      timezone: true,
      preferredTime: true,
      tier: true,
      displayName: true,
      email: true,
      avatarUrl: true,
    },
  });

  return NextResponse.json(user);
}

export async function PATCH(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();
  const allowed = ["timezone", "preferredTime"];
  const updates: Record<string, string> = {};

  for (const key of allowed) {
    if (key in body) {
      updates[key] = body[key];
    }
  }

  const user = await prisma.user.update({
    where: { id: session.userId },
    data: updates,
    select: {
      timezone: true,
      preferredTime: true,
      tier: true,
      displayName: true,
      email: true,
    },
  });

  return NextResponse.json(user);
}
