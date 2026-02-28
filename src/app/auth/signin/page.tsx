"use client";

import { useEffect, useState } from "react";
import { getMsalInstance, clearMsalState, loginRequest } from "@/lib/auth-client";

export default function SignInPage() {
  const [loading, setLoading] = useState(true); // start true while we process any pending redirect
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Always handle any pending redirect promise on mount.
    // This clears MSAL's in-progress flag and processes the return from Microsoft login.
    async function init() {
      try {
        const msal = await getMsalInstance();
        const result = await msal.handleRedirectPromise();
        if (result?.accessToken) {
          await exchangeTokenForSession(result.accessToken);
          return;
        }
      } catch (err) {
        console.error("MSAL init error:", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  async function exchangeTokenForSession(accessToken: string) {
    const res = await fetch("/api/auth/callback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ accessToken }),
    });

    if (res.ok) {
      window.location.href = "/dashboard";
    } else {
      setError("Failed to create session. Please try again.");
    }
  }

  async function handleSignIn() {
    setLoading(true);
    setError(null);
    try {
      const msal = await getMsalInstance();
      await msal.loginRedirect(loginRequest);
      // browser redirects away here — code below won't run
    } catch (err: unknown) {
      console.error(err);
      const msg = err instanceof Error ? err.message : "";
      if (msg.includes("interaction_in_progress")) {
        // Stale MSAL state — clear and let the user try once more
        clearMsalState();
        setError("Previous sign-in was interrupted. Please try again.");
      } else {
        setError("Sign in failed. Please try again.");
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
