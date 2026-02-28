"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

interface NotificationPromptProps {
  onDismiss: () => void;
}

export function NotificationPrompt({ onDismiss }: NotificationPromptProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function requestPermission() {
    setLoading(true);
    setError(null);

    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setError("Notification permission denied. You can enable this in your browser settings.");
        setLoading(false);
        return;
      }

      // Register service worker and subscribe
      const registration = await navigator.serviceWorker.ready;
      const vapidKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
      if (!vapidKey) {
        onDismiss();
        return;
      }

      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidKey).buffer as ArrayBuffer,
      });

      const sub = subscription.toJSON();
      await fetch("/api/push/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          endpoint: sub.endpoint,
          p256dh: sub.keys?.p256dh,
          auth: sub.keys?.auth,
        }),
      });

      onDismiss();
    } catch (err) {
      console.error(err);
      setError("Failed to set up notifications.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-start gap-4">
        <div className="text-3xl">🔔</div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1">Enable daily reminders?</h3>
          <p className="text-gray-500 text-sm mb-3">
            Get a push notification at your preferred time to keep your streak going.
          </p>
          {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
          <div className="flex gap-2">
            <Button size="sm" onClick={requestPermission} disabled={loading}>
              {loading ? "Setting up..." : "Enable notifications"}
            </Button>
            <Button size="sm" variant="ghost" onClick={onDismiss}>
              Not now
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}
