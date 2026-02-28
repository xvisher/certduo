import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function POST(
  request: NextRequest,
  { params: _params }: { params: Promise<{ certCode: string }> }
) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { docId, action } = await request.json();
  if (!docId) {
    return NextResponse.json({ error: "Missing docId" }, { status: 400 });
  }

  // action: "read" or "confirm"
  const status = action === "confirm" ? "confirmed" : "read";
  const updateData =
    status === "confirmed"
      ? { status, confirmedAt: new Date(), readAt: new Date() }
      : { status, readAt: new Date() };

  const doc = await prisma.userDocumentation.updateMany({
    where: { id: docId, userId: session.userId },
    data: updateData,
  });

  if (doc.count === 0) {
    return NextResponse.json({ error: "Documentation not found" }, { status: 404 });
  }

  return NextResponse.json({ success: true, status });
}
