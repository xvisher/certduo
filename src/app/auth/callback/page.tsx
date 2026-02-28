"use client";

import { useEffect, useState } from "react";
import { getMsalInstance } from "@/lib/auth-client";

export default function CallbackPage() {
  const [status, setStatus] = useState("Processing...");

  useEffect(() => {
    handleCallback();
  }, []);

  async function handleCallback() {
    try {
      const msal = await getMsalInstance();
      const result = await msal.handleRedirectPromise();

      if (result?.accessToken) {
        const res = await fetch("/api/auth/callback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            accessToken: result.accessToken,
            idToken: result.idToken,
          }),
        });

        if (res.ok) {
          const data = await res.json();
          window.location.href = data.isNewUser
            ? "/dashboard?onboarding=true"
            : "/dashboard";
        } else {
          setStatus("Authentication failed. Redirecting...");
          setTimeout(() => {
            window.location.href = "/auth/signin?error=callback_failed";
          }, 2000);
        }
      } else {
        // No result — likely a direct visit; send back to sign in
        window.location.href = "/auth/signin";
      }
    } catch (err) {
      console.error("Callback error:", err);
      setStatus("Something went wrong. Redirecting...");
      setTimeout(() => {
        window.location.href = "/auth/signin?error=unknown";
      }, 2000);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-[#0078D4] flex items-center justify-center mx-auto mb-6">
          <span className="text-white font-bold text-2xl">C</span>
        </div>
        <div className="w-8 h-8 border-2 border-[#0078D4] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-600 font-medium">{status}</p>
      </div>
    </div>
  );
}
