"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [show, setShow] = useState(false);

  useEffect(() => {
    function handler(e: Event) {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShow(true);
    }
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  async function install() {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") setShow(false);
    setDeferredPrompt(null);
  }

  if (!show) return null;

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-[#0078D4] flex items-center justify-center shrink-0">
          <span className="text-white font-bold text-lg">C</span>
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1">Install CertDuo</h3>
          <p className="text-gray-500 text-sm mb-3">
            Add to your home screen for a better experience and faster access.
          </p>
          <div className="flex gap-2">
            <Button size="sm" onClick={install}>
              Install App
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setShow(false)}>
              Dismiss
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
