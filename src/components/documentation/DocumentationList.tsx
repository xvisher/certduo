"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

interface DocItem {
  id: string;
  docUrl: string;
  status: string;
  linkedQuestion?: { questionText: string; id: string } | null;
  topic?: { title: string; module?: { title: string } };
}

interface DocumentationListProps {
  docs: DocItem[];
  onConfirm: (docId: string, action: "read" | "confirm") => Promise<void>;
}

export function DocumentationList({ docs, onConfirm }: DocumentationListProps) {
  const [loading, setLoading] = useState<string | null>(null);

  async function handle(docId: string, action: "read" | "confirm") {
    setLoading(docId + action);
    await onConfirm(docId, action);
    setLoading(null);
  }

  if (docs.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="text-4xl mb-3">📚</div>
        <p className="font-medium">All caught up!</p>
        <p className="text-sm">No documentation pending review.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {docs.map((doc) => (
        <div
          key={doc.id}
          className={`rounded-2xl border p-5 ${
            doc.status === "confirmed"
              ? "border-green-200 bg-green-50"
              : doc.status === "read"
              ? "border-yellow-200 bg-yellow-50"
              : "border-gray-200 bg-white"
          }`}
        >
          {/* Topic breadcrumb */}
          {doc.topic && (
            <div className="text-xs text-gray-400 mb-2">
              {doc.topic.module?.title && `${doc.topic.module.title} › `}
              {doc.topic.title}
            </div>
          )}

          {/* Doc link */}
          <Link
            href={doc.docUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-[#0078D4] hover:underline text-sm block mb-3"
          >
            {doc.docUrl.split("/").slice(-2).join(" › ")}
            <span className="ml-1 text-gray-400 text-xs">→ Microsoft Learn</span>
          </Link>

          {/* Linked question */}
          {doc.linkedQuestion && (
            <div className="bg-gray-50 rounded-xl p-3 mb-3 text-xs text-gray-600">
              <span className="font-semibold">Question: </span>
              {doc.linkedQuestion.questionText.slice(0, 120)}
              {doc.linkedQuestion.questionText.length > 120 && "..."}
            </div>
          )}

          {/* Actions */}
          {doc.status !== "confirmed" && (
            <div className="flex gap-2">
              {doc.status === "unread" && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handle(doc.id, "read")}
                  disabled={loading === doc.id + "read"}
                >
                  Mark as Read
                </Button>
              )}
              <Button
                size="sm"
                variant="success"
                onClick={() => handle(doc.id, "confirm")}
                disabled={loading === doc.id + "confirm"}
              >
                I understand this ✓
              </Button>
            </div>
          )}

          {doc.status === "confirmed" && (
            <span className="text-xs text-green-600 font-medium">✓ Confirmed</span>
          )}
        </div>
      ))}
    </div>
  );
}
