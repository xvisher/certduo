import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function DELETE(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { endpoint } = await request.json();

  await prisma.pushSubscription.deleteMany({
    where: { userId: session.userId, endpoint },
  });

  return NextResponse.json({ success: true });
}
