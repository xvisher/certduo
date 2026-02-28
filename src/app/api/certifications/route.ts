import { NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const [certifications, enrollments] = await Promise.all([
    prisma.certification.findMany({
      orderBy: { code: "asc" },
      include: {
        _count: { select: { questions: { where: { isActive: true } } } },
      },
    }),
    prisma.userCertification.findMany({
      where: { userId: session.userId },
    }),
  ]);

  const enrollmentMap = new Map(enrollments.map((e) => [e.certificationId, e]));

  const result = certifications.map((cert) => ({
    ...cert,
    questionCount: cert._count.questions,
    enrollment: enrollmentMap.get(cert.id) || null,
  }));

  return NextResponse.json(result);
}
