import { NextResponse } from "next/server";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const enrollments = await prisma.userCertification.findMany({
    where: { userId: session.userId },
    include: { certification: true },
  });

  const progress = await Promise.all(
    enrollments.map(async (enrollment) => {
      const certId = enrollment.certificationId;

      const [total, byStatus, pendingDocs] = await Promise.all([
        prisma.question.count({ where: { certificationId: certId, isActive: true } }),
        prisma.userQuestionProgress.groupBy({
          by: ["status"],
          where: { userId: session.userId, question: { certificationId: certId } },
          _count: true,
        }),
        prisma.userDocumentation.count({
          where: {
            userId: session.userId,
            status: { not: "confirmed" },
            topic: { module: { certificationId: certId } },
          },
        }),
      ]);

      const statusMap = Object.fromEntries(byStatus.map((s) => [s.status, s._count]));

      const mastered = statusMap["mastered"] || 0;
      const reviewing = statusMap["review"] || 0;
      const learning = statusMap["learning"] || 0;
      const seen = mastered + reviewing + learning;
      const unseen = total - seen;

      const percentComplete = total > 0 ? Math.round((mastered / total) * 100) : 0;

      // Update percent complete
      await prisma.userCertification.update({
        where: { id: enrollment.id },
        data: { percentComplete },
      });

      return {
        certification: enrollment.certification,
        enrollment: { ...enrollment, percentComplete },
        totalQuestions: total,
        mastered,
        reviewing,
        learning,
        unseen,
        pendingDocs,
        examReady: unseen === 0 && pendingDocs === 0,
      };
    })
  );

  return NextResponse.json(progress);
}
