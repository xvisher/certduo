import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET(
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
    include: {
      modules: {
        orderBy: { orderIndex: "asc" },
        include: {
          topics: { orderBy: { orderIndex: "asc" } },
          _count: { select: { questions: true } },
        },
      },
    },
  });

  if (!cert) {
    return NextResponse.json({ error: "Certification not found" }, { status: 404 });
  }

  const enrollment = await prisma.userCertification.findUnique({
    where: {
      userId_certificationId: {
        userId: session.userId,
        certificationId: cert.id,
      },
    },
  });

  return NextResponse.json({ ...cert, enrollment });
}
