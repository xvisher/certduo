import Link from "next/link";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { ProgressRing } from "@/components/progress/ProgressRing";
import { StreakBanner } from "@/components/progress/StreakBanner";
import { Badge } from "@/components/ui/badge";

export default async function ProgressPage() {
  const session = await getSession();
  if (!session) return null;

  const [user, enrollments] = await Promise.all([
    prisma.user.findUnique({
      where: { id: session.userId },
      select: { streakCount: true, lastActiveAt: true },
    }),
    prisma.userCertification.findMany({
      where: { userId: session.userId },
      include: { certification: true },
      orderBy: { startedAt: "desc" },
    }),
  ]);

  const certStats = await Promise.all(
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

      return {
        enrollment,
        total,
        mastered,
        reviewing,
        learning,
        unseen: total - seen,
        pendingDocs,
        percent: total > 0 ? Math.round((mastered / total) * 100) : 0,
        examReady: total - seen === 0 && pendingDocs === 0,
      };
    })
  );

  const totalMastered = certStats.reduce((s, c) => s + c.mastered, 0);
  const totalQuestions = certStats.reduce((s, c) => s + c.total, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Progress</h1>
        <p className="text-gray-500 mt-1 text-sm">Track your learning across all certifications.</p>
      </div>

      {/* Streak */}
      <StreakBanner streakCount={user?.streakCount || 0} lastActiveAt={user?.lastActiveAt} />

      {/* Global stats */}
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: "Questions Mastered", value: totalMastered, icon: "🎓" },
          { label: "Total Questions", value: totalQuestions, icon: "📚" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-2xl border border-gray-100 p-4 text-center">
            <div className="text-2xl mb-1">{stat.icon}</div>
            <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
            <div className="text-gray-400 text-xs mt-0.5">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Per-cert breakdown */}
      {certStats.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">📊</div>
          <p>No certifications enrolled yet.</p>
          <Link href="/certifications" className="text-[#0078D4] text-sm hover:underline mt-2 block">
            Browse certifications →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          <h2 className="font-semibold text-gray-900">By Certification</h2>
          {certStats.map((stat) => (
            <div key={stat.enrollment.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="font-bold text-[#0078D4] text-sm">{stat.enrollment.certification.code}</div>
                  <div className="font-semibold text-gray-900">{stat.enrollment.certification.name}</div>
                </div>
                <ProgressRing percent={stat.percent} size={64} strokeWidth={6} />
              </div>

              {/* Status breakdown */}
              <div className="grid grid-cols-4 gap-2 mb-4">
                {[
                  { label: "Mastered", count: stat.mastered, variant: "mastered" as const },
                  { label: "Review", count: stat.reviewing, variant: "review" as const },
                  { label: "Learning", count: stat.learning, variant: "learning" as const },
                  { label: "Unseen", count: stat.unseen, variant: "unseen" as const },
                ].map((s) => (
                  <div key={s.label} className="text-center">
                    <Badge variant={s.variant} className="text-xs mb-1">{s.count}</Badge>
                    <div className="text-xs text-gray-400">{s.label}</div>
                  </div>
                ))}
              </div>

              {/* Docs pending */}
              {stat.pendingDocs > 0 && (
                <div className="text-xs text-yellow-600 bg-yellow-50 rounded-xl px-3 py-2 mb-3">
                  📚 {stat.pendingDocs} documentation items pending review
                </div>
              )}

              {/* Exam readiness */}
              {stat.examReady && (
                <div className="flex items-center justify-between bg-green-50 rounded-xl px-3 py-2 mb-3">
                  <span className="text-green-700 text-sm font-medium">🎉 Ready for final exam!</span>
                  <Link
                    href={`/exam/${stat.enrollment.certification.code.toLowerCase()}`}
                    className="text-green-700 font-semibold text-sm hover:underline"
                  >
                    Take Exam →
                  </Link>
                </div>
              )}

              <Link
                href={`/learn/${stat.enrollment.certification.code.toLowerCase()}`}
                className="block w-full text-center border border-[#0078D4] text-[#0078D4] py-2 rounded-xl font-semibold text-sm hover:bg-blue-50 transition-colors"
              >
                Continue Learning
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
