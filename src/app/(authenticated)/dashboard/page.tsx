import Link from "next/link";
import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { ProgressRing } from "@/components/progress/ProgressRing";
import { StreakBanner } from "@/components/progress/StreakBanner";

export default async function DashboardPage() {
  const session = await getSession();
  if (!session) redirect("/auth/signin");

  const [user, enrollments, pendingDocCount] = await Promise.all([
    prisma.user.findUnique({
      where: { id: session.userId },
      select: { displayName: true, streakCount: true, lastActiveAt: true, tier: true },
    }),
    prisma.userCertification.findMany({
      where: { userId: session.userId, status: "active" },
      include: { certification: true },
      orderBy: { startedAt: "desc" },
    }),
    prisma.userDocumentation.count({
      where: { userId: session.userId, status: { not: "confirmed" } },
    }),
  ]);

  // Compute per-cert stats
  const certStats = await Promise.all(
    enrollments.map(async (enrollment) => {
      const [total, byStatus] = await Promise.all([
        prisma.question.count({
          where: { certificationId: enrollment.certificationId, isActive: true },
        }),
        prisma.userQuestionProgress.groupBy({
          by: ["status"],
          where: { userId: session.userId, question: { certificationId: enrollment.certificationId } },
          _count: true,
        }),
      ]);

      const statusMap = Object.fromEntries(byStatus.map((s) => [s.status, s._count]));
      const mastered = statusMap["mastered"] || 0;
      const percent = total > 0 ? Math.round((mastered / total) * 100) : 0;

      const reviewDue = await prisma.userQuestionProgress.count({
        where: {
          userId: session.userId,
          question: { certificationId: enrollment.certificationId },
          status: { in: ["learning", "review"] },
          nextReviewDate: { lte: new Date() },
        },
      });

      return { enrollment, total, percent, reviewDue };
    })
  );

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.displayName?.split(" ")[0]}! 👋
        </h1>
        <p className="text-gray-500 mt-1">
          {enrollments.length === 0
            ? "Choose a certification to start learning."
            : "Keep up the great work!"}
        </p>
      </div>

      {/* Streak */}
      {(user?.streakCount ?? 0) > 0 && (
        <StreakBanner
          streakCount={user?.streakCount || 0}
          lastActiveAt={user?.lastActiveAt}
        />
      )}

      {/* Pending docs alert */}
      {pendingDocCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <div className="font-semibold text-yellow-800">📚 {pendingDocCount} docs to review</div>
            <div className="text-yellow-600 text-sm">Reading these helps reinforce weak areas</div>
          </div>
          <Link
            href="/progress"
            className="text-yellow-800 font-semibold text-sm hover:underline"
          >
            Review →
          </Link>
        </div>
      )}

      {/* Active certifications */}
      {certStats.length > 0 ? (
        <div className="space-y-4">
          <h2 className="font-semibold text-gray-900">Your Certifications</h2>
          {certStats.map(({ enrollment, total, percent, reviewDue }) => (
            <div
              key={enrollment.id}
              className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="font-bold text-[#0078D4] text-sm">
                    {enrollment.certification.code}
                  </div>
                  <div className="font-semibold text-gray-900">
                    {enrollment.certification.name}
                  </div>
                </div>
                <ProgressRing percent={percent} size={56} strokeWidth={5} />
              </div>

              {reviewDue > 0 && (
                <div className="text-sm text-blue-600 bg-blue-50 rounded-xl px-3 py-2 mb-3">
                  🔄 {reviewDue} questions due for review
                </div>
              )}

              <Link
                href={`/learn/${enrollment.certification.code.toLowerCase()}`}
                className="block w-full text-center bg-[#0078D4] text-white py-2.5 rounded-xl font-semibold text-sm hover:bg-blue-700 transition-colors"
              >
                {reviewDue > 0 ? "Review Now →" : "Continue Learning →"}
              </Link>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 text-center">
          <div className="text-4xl mb-3">📋</div>
          <h3 className="font-semibold text-gray-900 mb-2">No certifications yet</h3>
          <p className="text-gray-500 text-sm mb-4">
            Choose a Microsoft certification to start your learning journey.
          </p>
          <Link
            href="/certifications"
            className="inline-flex items-center gap-2 bg-[#0078D4] text-white px-6 py-2.5 rounded-xl font-semibold text-sm hover:bg-blue-700 transition-colors"
          >
            Browse Certifications →
          </Link>
        </div>
      )}

      {/* Quick links */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          href="/progress"
          className="bg-white rounded-2xl border border-gray-100 p-4 text-center hover:shadow-sm transition-shadow"
        >
          <div className="text-2xl mb-1">📊</div>
          <div className="font-medium text-gray-900 text-sm">Progress</div>
        </Link>
        <Link
          href="/certifications"
          className="bg-white rounded-2xl border border-gray-100 p-4 text-center hover:shadow-sm transition-shadow"
        >
          <div className="text-2xl mb-1">🎯</div>
          <div className="font-medium text-gray-900 text-sm">All Certs</div>
        </Link>
      </div>
    </div>
  );
}
