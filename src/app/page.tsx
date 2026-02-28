import Link from "next/link";
import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function LandingPage() {
  const session = await getSession();
  if (session) redirect("/dashboard");

  const certs = [
    { code: "AZ-900", name: "Azure Fundamentals", emoji: "☁️" },
    { code: "AZ-104", name: "Azure Administrator", emoji: "⚙️" },
    { code: "MD-102", name: "Endpoint Administrator", emoji: "💻" },
    { code: "MS-102", name: "Microsoft 365 Administrator", emoji: "🏢" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <header className="px-4 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#0078D4] flex items-center justify-center">
            <span className="text-white font-bold text-sm">C</span>
          </div>
          <span className="font-bold text-xl text-gray-900">CertDuo</span>
        </div>
        <Link
          href="/auth/signin"
          className="px-4 py-2 rounded-lg border border-[#0078D4] text-[#0078D4] font-medium hover:bg-blue-50 transition-colors"
        >
          Sign In
        </Link>
      </header>

      {/* Hero */}
      <main className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-100 text-[#0078D4] rounded-full px-4 py-1.5 text-sm font-medium mb-6">
          <span>✨</span>
          <span>Duolingo-style Microsoft certification prep</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
          Learn. Quiz. <span className="text-[#0078D4]">Certify.</span>
        </h1>

        <p className="text-lg md:text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
          Master Microsoft certifications with daily bite-sized lessons and spaced repetition quizzes.
          Track your progress, review weak areas, and ace the real exam.
        </p>

        <Link
          href="/auth/signin"
          className="inline-flex items-center gap-3 bg-[#0078D4] text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200"
        >
          <svg width="20" height="20" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="9" height="9" fill="#F25022"/>
            <rect x="11" y="1" width="9" height="9" fill="#7FBA00"/>
            <rect x="1" y="11" width="9" height="9" fill="#00A4EF"/>
            <rect x="11" y="11" width="9" height="9" fill="#FFB900"/>
          </svg>
          Sign in with Microsoft
        </Link>

        <p className="text-sm text-gray-400 mt-4">Free to get started. No credit card required.</p>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 text-left">
          {[
            {
              icon: "🧠",
              title: "Spaced Repetition",
              desc: "SM-2 algorithm schedules reviews at optimal times so you never forget what you learn.",
            },
            {
              icon: "📚",
              title: "Official + Community Questions",
              desc: "Questions sourced from Microsoft Learn practice assessments and ExamTopics community.",
            },
            {
              icon: "🔥",
              title: "Daily Streaks",
              desc: "Build a learning habit with daily reminders and streak tracking to stay motivated.",
            },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Certifications */}
        <div className="mt-20">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Available Certifications</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {certs.map((cert) => (
              <div key={cert.code} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
                <div className="text-4xl mb-3">{cert.emoji}</div>
                <div className="font-bold text-[#0078D4] text-sm mb-1">{cert.code}</div>
                <div className="text-gray-600 text-xs">{cert.name}</div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center text-gray-400 text-sm py-8 mt-16 border-t border-gray-100">
        <p>CertDuo is not affiliated with or endorsed by Microsoft Corporation.</p>
        <p className="mt-1">
          Microsoft, Azure, and related marks are trademarks of Microsoft Corporation.
        </p>
      </footer>
    </div>
  );
}
