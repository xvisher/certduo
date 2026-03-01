"use client";

// This page is used as the redirect target for MSAL popup auth.
// MSAL handles the popup callback automatically — this page just needs to exist.
// It also handles direct navigation gracefully.

import { useEffect } from "react";

export default function CallbackPage() {
  useEffect(() => {
    // If this page is loaded outside of a popup (e.g., direct navigation),
    // redirect to sign-in.
    // When loaded inside an MSAL popup, MSAL will close the popup automatically
    // before this redirect can execute.
    const isInPopup = window.opener && window.opener !== window;
    if (!isInPopup) {
      // Give MSAL a moment to process if needed, then redirect
      setTimeout(() => {
        window.location.href = "/auth/signin";
      }, 2000);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl bg-[#0078D4] flex items-center justify-center mx-auto mb-6">
          <span className="text-white font-bold text-2xl">C</span>
        </div>
        <div className="w-8 h-8 border-2 border-[#0078D4] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-600 font-medium">Completing sign-in...</p>
      </div>
    </div>
  );
}
