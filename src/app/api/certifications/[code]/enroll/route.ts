import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ code: string }> }
) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { code } = await params;

  // Check free tier limit
  const user = await prisma.user.findUnique({ where: { id: session.userId } });
  if (user?.tier === "free") {
    const activeCount = await prisma.userCertification.count({
      where: { userId: session.userId, status: "active" },
    });
    if (activeCount >= 1) {
      return NextResponse.json(
        { error: "Free tier is limited to 1 active certification. Upgrade to Pro for unlimited access." },
        { status: 403 }
      );
    }
  }

  const cert = await prisma.certification.findUnique({
    where: { code: code.toUpperCase() },
  });

  if (!cert) {
    return NextResponse.json({ error: "Certification not found" }, { status: 404 });
  }

  const enrollment = await prisma.userCertification.upsert({
    where: {
      userId_certificationId: {
        userId: session.userId,
        certificationId: cert.id,
      },
    },
    update: { status: "active" },
    create: {
      userId: session.userId,
      certificationId: cert.id,
      status: "active",
    },
  });

  return NextResponse.json(enrollment);
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ code: string }> }
) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { code } = await params;

  const cert = await prisma.certification.findUnique({
    where: { code: code.toUpperCase() },
  });

  if (!cert) {
    return NextResponse.json({ error: "Certification not found" }, { status: 404 });
  }

  await prisma.userCertification.deleteMany({
    where: { userId: session.userId, certificationId: cert.id },
  });

  return NextResponse.json({ success: true });
}
