import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ certCode: string }> }
) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { certCode } = await params;

  const cert = await prisma.certification.findUnique({
    where: { code: certCode.toUpperCase() },
  });
  if (!cert) {
    return NextResponse.json({ error: "Certification not found" }, { status: 404 });
  }

  const docs = await prisma.userDocumentation.findMany({
    where: {
      userId: session.userId,
      status: { not: "confirmed" },
      topic: { module: { certificationId: cert.id } },
    },
    include: {
      topic: {
        include: {
          module: { select: { title: true } },
        },
      },
    },
    orderBy: { assignedAt: "desc" },
  });

  // Get linked questions for context
  const result = await Promise.all(
    docs.map(async (doc) => {
      const linkedQuestion = doc.linkedQuestionId
        ? await prisma.question.findUnique({
            where: { id: doc.linkedQuestionId },
            select: { questionText: true, id: true },
          })
        : null;

      return { ...doc, linkedQuestion };
    })
  );

  return NextResponse.json(result);
}
