import Link from "next/link";
import { notFound } from "next/navigation";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { ProgressRing } from "@/components/progress/ProgressRing";
import { Badge } from "@/components/ui/badge";

export default async function CertificationDetailPage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  const session = await getSession();
  if (!session) return null;

  const { code } = await params;

  const cert = await prisma.certification.findUnique({
    where: { code: code.toUpperCase() },
    include: {
      modules: {
        orderBy: { orderIndex: "asc" },
        include: { topics: { orderBy: { orderIndex: "asc" } } },
      },
    },
  });

  if (!cert) notFound();

  const enrollment = await prisma.userCertification.findUnique({
    where: {
      userId_certificationId: { userId: session.userId, certificationId: cert.id },
    },
  });

  const [totalQ, progressByStatus] = await Promise.all([
    prisma.question.count({ where: { certificationId: cert.id, isActive: true } }),
    prisma.userQuestionProgress.groupBy({
      by: ["status"],
      where: { userId: session.userId, question: { certificationId: cert.id } },
      _count: true,
    }),
  ]);

  const statusMap = Object.fromEntries(progressByStatus.map((s) => [s.status, s._count]));
  const mastered = statusMap["mastered"] || 0;
  const percent = totalQ > 0 ? Math.round((mastered / totalQ) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="font-bold text-[#0078D4] text-sm mb-1">{cert.code}</div>
            <h1 className="text-xl font-bold text-gray-900">{cert.name}</h1>
          </div>
          {enrollment && <ProgressRing percent={percent} size={72} />}
        </div>

        {cert.description && (
          <p className="text-gray-500 text-sm leading-relaxed mb-4">{cert.description}</p>
        )}

        <div className="flex gap-2 mb-4">
          <Badge variant="default">{totalQ} questions</Badge>
          <Badge variant="default">{cert.modules.length} modules</Badge>
          {enrollment?.status === "completed" && <Badge variant="success">Completed ✓</Badge>}
        </div>

        {enrollment ? (
          <Link
            href={`/learn/${code}`}
            className="block w-full text-center bg-[#0078D4] text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
          >
            Continue Learning →
          </Link>
        ) : (
          <form action={`/api/certifications/${code}/enroll`} method="POST">
            <Link
              href="/certifications"
              className="block w-full text-center border border-[#0078D4] text-[#0078D4] py-3 rounded-xl font-semibold hover:bg-blue-50 transition-colors"
            >
              Enroll to Start Learning
            </Link>
          </form>
        )}
      </div>

      {/* Modules */}
      <div>
        <h2 className="font-semibold text-gray-900 mb-3">Learning Modules</h2>
        <div className="space-y-3">
          {cert.modules.map((module, i) => (
            <div key={module.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-[#0078D4] flex items-center justify-center font-bold text-sm shrink-0">
                  {i + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-sm">{module.title}</h3>
                  {module.description && (
                    <p className="text-gray-500 text-xs mt-1">{module.description}</p>
                  )}
                  {module.topics.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {module.topics.map((topic) => (
                        <span
                          key={topic.id}
                          className="text-xs bg-gray-50 text-gray-500 rounded-lg px-2 py-0.5"
                        >
                          {topic.title}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
