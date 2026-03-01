"use client";

import { useEffect, useState } from "react";
import { getMsalInstance } from "@/lib/auth-client";

interface DiagInfo {
  url: string;
  hasCode: boolean;
  hasState: boolean;
  msalKeyCount: number;
  msalResult: string;
  apiStatus?: number;
  apiBody?: string;
}

export default function CallbackPage() {
  const [status, setStatus] = useState("Processing sign-in...");
  const [error, setError] = useState<string | null>(null);
  const [diag, setDiag] = useState<DiagInfo | null>(null);

  useEffect(() => {
    handleCallback();
  }, []);

  async function handleCallback() {
    // Collect URL diagnostics immediately, before any MSAL calls
    const search = window.location.search;
    const hash = window.location.hash;
    const fullUrl = window.location.href;
    const params = new URLSearchParams(search || (hash.startsWith("#") ? hash.slice(1) : ""));
    const diagInfo: DiagInfo = {
      url: fullUrl,
      hasCode: params.has("code"),
      hasState: params.has("state"),
      msalKeyCount: Object.keys(sessionStorage).filter(k => k.startsWith("msal")).length,
      msalResult: "pending...",
    };
    setDiag({ ...diagInfo });

    try {
      setStatus("Initializing MSAL...");
      const msal = await getMsalInstance();

      setStatus("Calling handleRedirectPromise...");
      const result = await msal.handleRedirectPromise();

      if (result) {
        diagInfo.msalResult = `✅ Got result — accessToken: ${result.accessToken ? "YES" : "MISSING"}, account: ${result.account?.username ?? "none"}`;
      } else {
        diagInfo.msalResult = "❌ NULL — no pending redirect detected";
      }
      setDiag({ ...diagInfo });

      if (result?.accessToken) {
        setStatus("Calling /api/auth/callback...");
        const res = await fetch("/api/auth/callback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            accessToken: result.accessToken,
            idToken: result.idToken,
          }),
        });

        diagInfo.apiStatus = res.status;
        let bodyText = "";
        try { bodyText = await res.text(); } catch {}
        diagInfo.apiBody = bodyText;
        setDiag({ ...diagInfo });

        if (res.ok) {
          setStatus("✅ Success! Redirecting to dashboard...");
          const data = JSON.parse(bodyText);
          window.location.href = data.isNewUser
            ? "/dashboard?onboarding=true"
            : "/dashboard";
        } else {
          setError(`API error (${res.status}): ${bodyText}`);
        }
      } else {
        setError("handleRedirectPromise() returned null. See diagnostics below.");
      }
    } catch (err) {
      diagInfo.msalResult = `💥 THREW: ${err instanceof Error ? err.message : String(err)}`;
      setDiag({ ...diagInfo });
      setError(`Exception: ${err instanceof Error ? err.message : String(err)}`);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-start pt-8 px-4">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-[#0078D4] flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <div>
            <p className="font-bold text-gray-900">CertDuo Sign-In</p>
            <p className="text-xs text-gray-500">Auth Callback Page</p>
          </div>
        </div>

        {/* Status */}
        <div className="flex items-center gap-3 mb-4">
          {!error ? (
            <div className="w-5 h-5 border-2 border-[#0078D4] border-t-transparent rounded-full animate-spin flex-shrink-0" />
          ) : (
            <span className="text-red-500 text-xl">✗</span>
          )}
          <p className="text-gray-700 font-medium">{error ? "Sign-in failed" : status}</p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
            <p className="text-red-700 text-sm font-mono break-all">{error}</p>
          </div>
        )}

        {/* Diagnostics — always visible */}
        {diag && (
          <div className="bg-white border border-gray-200 rounded-xl p-4 mb-4">
            <p className="font-semibold text-gray-800 text-sm mb-3">Diagnostics</p>
            <div className="space-y-2 text-sm font-mono">
              <div className={diag.hasCode ? "text-green-700" : "text-red-700"}>
                code in URL: {diag.hasCode ? "✅ YES" : "❌ NO"}
              </div>
              <div className={diag.hasState ? "text-green-700" : "text-red-700"}>
                state in URL: {diag.hasState ? "✅ YES" : "❌ NO"}
              </div>
              <div className={diag.msalKeyCount > 0 ? "text-green-700" : "text-red-700"}>
                MSAL sessionStorage keys: {diag.msalKeyCount > 0 ? `✅ ${diag.msalKeyCount} found` : "❌ 0 (cleared between redirect?)"}
              </div>
              <div className={diag.msalResult.startsWith("✅") ? "text-green-700" : "text-red-700"}>
                MSAL result: {diag.msalResult}
              </div>
              {diag.apiStatus !== undefined && (
                <div className={diag.apiStatus < 300 ? "text-green-700" : "text-red-700"}>
                  API response: HTTP {diag.apiStatus} — {(diag.apiBody ?? "").substring(0, 150)}
                </div>
              )}
              <div className="text-gray-400 break-all text-xs mt-2 pt-2 border-t border-gray-100">
                Full URL: {diag.url}
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 flex-wrap">
          <a
            href="/auth/signin"
            className="px-4 py-2 bg-[#0078D4] text-white rounded-lg text-sm font-semibold hover:bg-blue-700"
          >
            ← Try Again
          </a>
          {diag && (
            <button
              onClick={() => {
                const text = `DIAG:\n${JSON.stringify(diag, null, 2)}\n\nERROR: ${error}`;
                navigator.clipboard?.writeText(text).catch(() => {});
                alert("Copied to clipboard!");
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-200"
            >
              📋 Copy Diagnostics
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
