"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { NotificationPrompt } from "@/components/notifications/NotificationPrompt";
import { InstallPrompt } from "@/components/notifications/InstallPrompt";

const TIMEZONES = [
  "UTC", "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
  "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Tokyo", "Asia/Singapore",
  "Australia/Sydney",
];

export default function SettingsPage() {
  const [settings, setSettings] = useState({ timezone: "UTC", preferredTime: "08:00" });
  const [user, setUser] = useState<{ displayName: string; email: string; tier: string; avatarUrl?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showNotifPrompt, setShowNotifPrompt] = useState(false);

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((data) => {
        setSettings({ timezone: data.timezone || "UTC", preferredTime: data.preferredTime || "08:00" });
        setUser(data);
        setLoading(false);
      });
  }, []);

  async function saveSettings() {
    setSaving(true);
    await fetch("/api/settings", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  async function signOut() {
    await fetch("/api/auth/signout", { method: "POST" });
    window.location.href = "/";
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-200 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1 text-sm">Manage your preferences and account.</p>
      </div>

      {/* Profile */}
      {user && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-[#0078D4] flex items-center justify-center text-white font-bold text-lg">
              {user.displayName.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="font-semibold text-gray-900">{user.displayName}</div>
              <div className="text-gray-500 text-sm">{user.email}</div>
              <div className="mt-1">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                  user.tier === "pro"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-gray-100 text-gray-500"
                }`}>
                  {user.tier === "pro" ? "⭐ Pro" : "Free"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notification settings */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
        <h2 className="font-semibold text-gray-900 mb-4">Notifications</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Preferred learning time
            </label>
            <input
              type="time"
              value={settings.preferredTime}
              onChange={(e) => setSettings((s) => ({ ...s, preferredTime: e.target.value }))}
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-[#0078D4]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Timezone
            </label>
            <select
              value={settings.timezone}
              onChange={(e) => setSettings((s) => ({ ...s, timezone: e.target.value }))}
              className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-[#0078D4] bg-white"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>{tz}</option>
              ))}
            </select>
          </div>

          <Button
            onClick={saveSettings}
            disabled={saving}
            className="w-full"
          >
            {saving ? "Saving..." : saved ? "Saved ✓" : "Save Settings"}
          </Button>
        </div>
      </div>

      {/* Push notifications */}
      {showNotifPrompt ? (
        <NotificationPrompt onDismiss={() => setShowNotifPrompt(false)} />
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="font-semibold text-gray-900 mb-2">Push Notifications</h2>
          <p className="text-gray-500 text-sm mb-3">
            Enable browser push notifications for daily learning reminders.
          </p>
          <Button variant="outline" onClick={() => setShowNotifPrompt(true)}>
            Set up notifications
          </Button>
        </div>
      )}

      {/* Install PWA */}
      <InstallPrompt />

      {/* Admin panel link — pro users only */}
      {user?.tier === "pro" && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="font-semibold text-gray-900 mb-2">Admin</h2>
          <p className="text-gray-500 text-sm mb-3">
            Manage users and upgrade or downgrade their tier.
          </p>
          <Button variant="outline" onClick={() => { window.location.href = "/admin"; }} className="w-full">
            Open User Admin →
          </Button>
        </div>
      )}

      {/* Sign out */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
        <h2 className="font-semibold text-gray-900 mb-2">Account</h2>
        <p className="text-gray-500 text-sm mb-3">
          Free tier: 1 active certification, 10 questions/day.
        </p>
        <Button variant="destructive" onClick={signOut} className="w-full">
          Sign Out
        </Button>
      </div>
    </div>
  );
}
