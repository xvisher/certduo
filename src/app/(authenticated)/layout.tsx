import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { Navbar } from "@/components/layout/Navbar";

export default async function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();
  if (!session) redirect("/auth/signin");

  const user = await prisma.user.findUnique({
    where: { id: session.userId },
    select: { displayName: true, avatarUrl: true, streakCount: true },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user || undefined} />
      <main className="max-w-2xl mx-auto px-4 py-6 pb-24">
        {children}
      </main>
    </div>
  );
}
