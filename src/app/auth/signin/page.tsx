"use client";

import { useState } from "react";
import { getMsalInstance, clearMsalState, loginRequest } from "@/lib/auth-client";

export default function SignInPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSignIn() {
    setLoading(true);
    setError(null);
    try {
      const msal = await getMsalInstance();

      // Clear any stale interaction state from previous failed redirect attempts
      // before calling loginPopup, otherwise MSAL throws interaction_in_progress
      try {
        await msal.handleRedirectPromise();
      } catch {
        // ignore — just draining any pending redirect state
      }

      // Use popup — no page navigation, no redirect issues, no service worker interference
      const result = await msal.loginPopup({
        ...loginRequest,
        // Popup uses the same redirectUri but handles it internally
        redirectUri: `${window.location.origin}/auth/callback`,
      });

      if (!result?.accessToken) {
        setError("No access token received. Please try again.");
        setLoading(false);
        return;
      }

      // Exchange the token for a session cookie
      const res = await fetch("/api/auth/callback", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          accessToken: result.accessToken,
          idToken: result.idToken,
        }),
      });

      if (res.ok) {
        // Redirect to dashboard — cookie is already set
        window.location.href = "/dashboard";
      } else {
        const body = await res.text().catch(() => "unknown error");
        setError(`Sign-in failed (${res.status}): ${body}`);
        setLoading(false);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("interaction_in_progress")) {
        // Stale MSAL state — wipe it and retry once automatically
        clearMsalState();
        setLoading(false);
        setError(null);
        // Small delay then retry
        setTimeout(() => handleSignIn(), 300);
        return;
      } else if (msg.includes("user_cancelled") || msg.includes("popup_window_error") || msg.includes("access_denied")) {
        // User closed the popup — not an error
        setError(null);
      } else if (msg.includes("popup_blocked")) {
        setError("Popup was blocked. Please allow popups for certduo.vercel.app and try again.");
      } else {
        setError(`Sign-in error: ${msg}`);
      }
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-[#0078D4] flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">C</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome to CertDuo</h1>
          <p className="text-gray-500 text-sm mt-2">Sign in to start your certification journey</p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-600 rounded-xl p-3 text-sm mb-4">
            {error}
          </div>
        )}

        {/* Sign in button */}
        <button
          onClick={handleSignIn}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 bg-[#0078D4] text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <svg width="20" height="20" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
              <rect x="1" y="1" width="9" height="9" fill="#F25022"/>
              <rect x="11" y="1" width="9" height="9" fill="#7FBA00"/>
              <rect x="1" y="11" width="9" height="9" fill="#00A4EF"/>
              <rect x="11" y="11" width="9" height="9" fill="#FFB900"/>
            </svg>
          )}
          {loading ? "Signing in..." : "Sign in with Microsoft"}
        </button>

        <p className="text-center text-xs text-gray-400 mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>

        <div className="mt-4 text-center">
          <a href="/" className="text-sm text-[#0078D4] hover:underline">← Back to home</a>
        </div>
      </div>
    </div>
  );
}
