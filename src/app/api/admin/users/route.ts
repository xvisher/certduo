import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

// Only pro-tier users can access admin endpoints
async function requireAdmin() {
  const session = await getSession();
  if (!session) return null;
  const user = await prisma.user.findUnique({
    where: { id: session.userId },
    select: { id: true, tier: true },
  });
  if (!user || user.tier !== "pro") return null;
  return user;
}

// GET /api/admin/users — list all users
export async function GET() {
  const admin = await requireAdmin();
  if (!admin) return NextResponse.json({ error: "Forbidden" }, { status: 403 });

  const users = await prisma.user.findMany({
    select: {
      id: true,
      displayName: true,
      email: true,
      tier: true,
      createdAt: true,
      lastActiveAt: true,
    },
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(users);
}

// PATCH /api/admin/users — update a user's tier
// Body: { userId: string, tier: "free" | "pro" }
export async function PATCH(request: NextRequest) {
  const admin = await requireAdmin();
  if (!admin) return NextResponse.json({ error: "Forbidden" }, { status: 403 });

  const body = await request.json();
  const { userId, tier } = body;

  if (!userId || !["free", "pro"].includes(tier)) {
    return NextResponse.json({ error: "Invalid userId or tier" }, { status: 400 });
  }

  const updated = await prisma.user.update({
    where: { id: userId },
    data: { tier },
    select: { id: true, displayName: true, email: true, tier: true },
  });

  return NextResponse.json(updated);
}
