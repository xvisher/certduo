"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface User {
  id: string;
  displayName: string;
  email: string;
  tier: "free" | "pro";
  createdAt: string;
  lastActiveAt: string | null;
}

export default function AdminPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    fetch("/api/admin/users")
      .then((r) => {
        if (r.status === 403) { setForbidden(true); setLoading(false); return null; }
        return r.json();
      })
      .then((data) => {
        if (data) { setUsers(data); setLoading(false); }
      });
  }, []);

  async function setTier(userId: string, tier: "free" | "pro") {
    setUpdating(userId);
    const res = await fetch("/api/admin/users", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, tier }),
    });
    if (res.ok) {
      const updated: User = await res.json();
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? { ...u, tier: updated.tier } : u)));
    }
    setUpdating(null);
  }

  if (forbidden) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="text-center">
          <div className="text-4xl mb-3">🚫</div>
          <h1 className="text-xl font-bold text-gray-900">Access Denied</h1>
          <p className="text-gray-500 text-sm mt-1">Admin panel is only available to Pro users.</p>
          <button onClick={() => router.push("/dashboard")} className="mt-4 text-sm text-[#0078D4] hover:underline">
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-200 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  const proCount = users.filter((u) => u.tier === "pro").length;
  const freeCount = users.filter((u) => u.tier === "free").length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin — Users</h1>
        <p className="text-gray-500 mt-1 text-sm">
          {users.length} total · {proCount} pro · {freeCount} free
        </p>
      </div>

      <div className="space-y-3">
        {users.map((user) => (
          <div
            key={user.id}
            className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 flex items-center justify-between gap-4"
          >
            <div className="min-w-0">
              <div className="font-semibold text-gray-900 truncate">{user.displayName}</div>
              <div className="text-gray-500 text-sm truncate">{user.email}</div>
              <div className="text-gray-400 text-xs mt-0.5">
                Joined {new Date(user.createdAt).toLocaleDateString()}
                {user.lastActiveAt && (
                  <> · Last active {new Date(user.lastActiveAt).toLocaleDateString()}</>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                user.tier === "pro"
                  ? "bg-yellow-100 text-yellow-700"
                  : "bg-gray-100 text-gray-500"
              }`}>
                {user.tier === "pro" ? "⭐ Pro" : "Free"}
              </span>

              <button
                onClick={() => setTier(user.id, user.tier === "pro" ? "free" : "pro")}
                disabled={updating === user.id}
                className={`text-xs px-3 py-1.5 rounded-xl font-semibold transition-colors disabled:opacity-50 ${
                  user.tier === "pro"
                    ? "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    : "bg-[#0078D4] text-white hover:bg-blue-700"
                }`}
              >
                {updating === user.id
                  ? "..."
                  : user.tier === "pro"
                  ? "Downgrade"
                  : "Upgrade"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
