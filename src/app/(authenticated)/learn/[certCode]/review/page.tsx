"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { DocumentationList } from "@/components/documentation/DocumentationList";
import { Button } from "@/components/ui/button";

export default function ReviewPage() {
  const params = useParams();
  const certCode = params.certCode as string;

  const [docs, setDocs] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDocs = useCallback(async () => {
    setLoading(true);
    const res = await fetch(`/api/learn/${certCode}/review`);
    if (res.ok) {
      const data = await res.json();
      setDocs(data);
    }
    setLoading(false);
  }, [certCode]);

  useEffect(() => {
    loadDocs();
  }, [loadDocs]);

  async function handleConfirm(docId: string, action: "read" | "confirm") {
    const res = await fetch(`/api/learn/${certCode}/review/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ docId, action }),
    });
    if (res.ok) {
      await loadDocs();
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documentation Review</h1>
          <p className="text-gray-500 mt-1 text-sm">
            Read these docs to reinforce concepts from missed questions.
          </p>
        </div>
        <Link href={`/learn/${certCode}`}>
          <Button size="sm" variant="outline">Back to Learning</Button>
        </Link>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : (
        <DocumentationList docs={docs as Parameters<typeof DocumentationList>[0]["docs"]} onConfirm={handleConfirm} />
      )}
    </div>
  );
}
