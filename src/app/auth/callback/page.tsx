"use client";

import { useEffect, useState } from "react";
import { getMsalInstance } from "@/lib/auth-client";

export default function CallbackPage() {
  const [status, setStatus] = useState("Processing sign-in...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    handleCallback();
  }, []);

  async function handleCallback() {
    try {
      setStatus("Initializing...");
      const msal = await getMsalInstance();

      setStatus("Completing sign-in with Microsoft...");
      const result = await msal.handleRedirectPromise();

      if (result?.accessToken) {
        setStatus("Verifying your account...");
        const res = await fetch("/api/auth/callback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            accessToken: result.accessToken,
            idToken: result.idToken,
          }),
        });

        if (res.ok) {
          setStatus("Success! Redirecting...");
          const data = await res.json();
          window.location.href = data.isNewUser
            ? "/dashboard?onboarding=true"
            : "/dashboard";
        } else {
          let detail = `Server error (${res.status})`;
          try {
            const json = await res.json();
            detail = json.error || detail;
          } catch {}
          setError(`Authentication failed: ${detail}`);
        }
      } else {
        // handleRedirectPromise returned null — no pending auth redirect found
        setError(
          "No sign-in data found. This can happen if the session expired or the page was refreshed mid-login. Please try signing in again."
        );
      }
    } catch (err) {
      console.error("Callback error:", err);
      const msg = err instanceof Error ? err.message : String(err);
      setError(`Sign-in error: ${msg}`);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="text-center max-w-sm w-full">
        <div className="w-16 h-16 rounded-2xl bg-[#0078D4] flex items-center justify-center mx-auto mb-6">
          <span className="text-white font-bold text-2xl">C</span>
        </div>

        {error ? (
          <div>
            <div className="bg-red-50 border border-red-200 rounded-2xl p-4 mb-6 text-left">
              <p className="text-red-700 text-sm font-medium mb-1">Sign-in failed</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
            <a
              href="/auth/signin"
              className="inline-block bg-[#0078D4] text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
            >
              Try Again
            </a>
          </div>
        ) : (
          <div>
            <div className="w-8 h-8 border-2 border-[#0078D4] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-600 font-medium">{status}</p>
          </div>
        )}
      </div>
    </div>
  );
}
