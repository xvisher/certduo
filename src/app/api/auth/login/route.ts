import { NextResponse } from "next/server";
import crypto from "crypto";

/**
 * GET /api/auth/login
 *
 * OAuth2 Authorization Code Flow entry point.
 * Generates a CSRF state token, stores it in a cookie,
 * and redirects the user to Microsoft's authorize endpoint.
 */
export async function GET() {
  const state = crypto.randomBytes(32).toString("hex");

  const tenantId = process.env.MSAL_TENANT_ID || "common";
  const clientId = process.env.MSAL_CLIENT_ID!;
  const redirectUri = process.env.MSAL_REDIRECT_URI!;

  const params = new URLSearchParams({
    client_id: clientId,
    response_type: "code",
    redirect_uri: redirectUri,
    scope: "openid profile email User.Read",
    state,
    response_mode: "query",
    prompt: "select_account",
  });

  const authorizeUrl = `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/authorize?${params}`;

  const response = NextResponse.redirect(authorizeUrl);

  // Store state in httpOnly cookie for CSRF verification on callback.
  // sameSite must be "lax" so the cookie is sent on the cross-site redirect
  // back from Microsoft.
  response.cookies.set("oauth_state", state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 600, // 10 minutes
    path: "/",
  });

  return response;
}
