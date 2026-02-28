import { PublicClientApplication } from "@azure/msal-browser";
import type { Configuration, RedirectRequest } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_MSAL_CLIENT_ID || "",
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_MSAL_TENANT_ID || "common"}`,
    redirectUri: process.env.NEXT_PUBLIC_MSAL_REDIRECT_URI || "http://localhost:3000/auth/callback",
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
};

export const loginRequest: RedirectRequest = {
  scopes: ["User.Read", "openid", "profile", "email"],
};

// Singleton — one instance for the entire browser session
let _msalInstance: PublicClientApplication | null = null;
let _initPromise: Promise<PublicClientApplication> | null = null;

export async function getMsalInstance(): Promise<PublicClientApplication> {
  if (_msalInstance) return _msalInstance;

  // Prevent double-initialization if called concurrently
  if (_initPromise) return _initPromise;

  _initPromise = (async () => {
    const instance = new PublicClientApplication(msalConfig);
    await instance.initialize();
    _msalInstance = instance;
    return instance;
  })();

  return _initPromise;
}

/** Clear all MSAL session state — call this when stuck in interaction_in_progress */
export function clearMsalState() {
  Object.keys(sessionStorage)
    .filter((k) => k.startsWith("msal."))
    .forEach((k) => sessionStorage.removeItem(k));
  _msalInstance = null;
  _initPromise = null;
}
