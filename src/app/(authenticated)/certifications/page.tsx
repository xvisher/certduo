"use client";

import { useEffect, useState } from "react";
import { CertificationCard } from "@/components/certification/CertificationCard";
import type { Certification } from "@/types";

interface CertWithEnrollment extends Certification {
  questionCount: number;
  enrollment: {
    status: string;
    percentComplete: number;
    completedAt?: string | null;
  } | null;
}

export default function CertificationsPage() {
  const [certs, setCerts] = useState<CertWithEnrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/certifications")
      .then((r) => r.json())
      .then(setCerts)
      .finally(() => setLoading(false));
  }, []);

  async function handleEnroll(certId: string, code: string) {
    setEnrolling(certId);
    const res = await fetch(`/api/certifications/${code}/enroll`, { method: "POST" });
    if (res.ok) {
      // Refresh list
      const updated = await fetch("/api/certifications").then((r) => r.json());
      setCerts(updated);
    } else {
      const data = await res.json();
      alert(data.error || "Failed to enroll");
    }
    setEnrolling(null);
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 bg-gray-200 rounded-xl animate-pulse" />
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-48 bg-gray-200 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Certifications</h1>
        <p className="text-gray-500 mt-1">Choose a certification to start preparing for.</p>
      </div>

      {certs.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-3">📭</div>
          <p>No certifications available yet.</p>
          <p className="text-sm">Questions are being loaded into the database.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {certs.map((cert) => (
            <CertificationCard
              key={cert.id}
              certification={cert}
              enrollment={cert.enrollment}
              questionCount={cert.questionCount}
              onEnroll={() => handleEnroll(cert.id, cert.code)}
              enrolled={!!cert.enrollment}
            />
          ))}
        </div>
      )}
    </div>
  );
}
