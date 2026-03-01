import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { createSession, SESSION_COOKIE } from "@/lib/auth";

/**
 * GET /auth/callback
 *
 * OAuth2 Authorization Code Flow callback.
 * Microsoft redirects here with ?code=xxx&state=yyy after authentication.
 *
 * This handler:
 * 1. Validates the CSRF state against the oauth_state cookie
 * 2. Exchanges the authorization code for an access token (server-side, with client_secret)
 * 3. Fetches the user profile from Microsoft Graph
 * 4. Upserts the user in the database
 * 5. Creates a session JWT
 * 6. Sets the session cookie on a 302 redirect to /dashboard
 *
 * Because this is a real browser navigation (not a fetch() call),
 * the Set-Cookie header is guaranteed to be processed by the browser.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const error = searchParams.get("error");
  const errorDescription = searchParams.get("error_description");

  // Handle Microsoft returning an error (user denied consent, cancelled, etc.)
  if (error) {
    console.error("OAuth error:", error, errorDescription);
    const errorUrl = new URL("/auth/signin", request.url);
    errorUrl.searchParams.set("error", error);
    if (errorDescription) {
      errorUrl.searchParams.set("error_description", errorDescription.slice(0, 200));
    }
    return NextResponse.redirect(errorUrl);
  }

  if (!code || !state) {
    return NextResponse.redirect(new URL("/auth/signin?error=missing_params", request.url));
  }

  // CSRF: verify state matches the cookie set by /api/auth/login
  const storedState = request.cookies.get("oauth_state")?.value;
  if (!storedState || storedState !== state) {
    return NextResponse.redirect(new URL("/auth/signin?error=invalid_state", request.url));
  }

  try {
    // ─── Exchange authorization code for tokens ───
    const tenantId = process.env.MSAL_TENANT_ID || "common";
    const tokenUrl = `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`;

    const tokenBody = new URLSearchParams({
      client_id: process.env.MSAL_CLIENT_ID!,
      client_secret: process.env.MSAL_CLIENT_SECRET!,
      code,
      redirect_uri: process.env.MSAL_REDIRECT_URI!,
      grant_type: "authorization_code",
      scope: "openid profile email User.Read",
    });

    const tokenRes = await fetch(tokenUrl, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: tokenBody.toString(),
    });

    if (!tokenRes.ok) {
      const tokenError = await tokenRes.text();
      console.error("Token exchange failed:", tokenRes.status, tokenError);
      return NextResponse.redirect(new URL("/auth/signin?error=token_exchange_failed", request.url));
    }

    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;

    if (!accessToken) {
      return NextResponse.redirect(new URL("/auth/signin?error=no_access_token", request.url));
    }

    // ─── Fetch user profile from Microsoft Graph ───
    const graphRes = await fetch("https://graph.microsoft.com/v1.0/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!graphRes.ok) {
      console.error("Graph API error:", graphRes.status);
      return NextResponse.redirect(new URL("/auth/signin?error=graph_failed", request.url));
    }

    const profile = await graphRes.json();

    // ─── Fetch profile photo (optional) ───
    let avatarUrl: string | null = null;
    try {
      const photoRes = await fetch("https://graph.microsoft.com/v1.0/me/photo/$value", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (photoRes.ok) {
        const photoBuffer = await photoRes.arrayBuffer();
        const base64 = Buffer.from(photoBuffer).toString("base64");
        avatarUrl = `data:image/jpeg;base64,${base64}`;
      }
    } catch {
      // Photo is optional
    }

    // ─── Upsert user in database ───
    const user = await prisma.user.upsert({
      where: { microsoftId: profile.id },
      update: {
        email: profile.mail || profile.userPrincipalName,
        displayName: profile.displayName,
        ...(avatarUrl && { avatarUrl }),
        lastActiveAt: new Date(),
      },
      create: {
        microsoftId: profile.id,
        email: profile.mail || profile.userPrincipalName,
        displayName: profile.displayName,
        avatarUrl,
        lastActiveAt: new Date(),
      },
    });

    // ─── Create session ───
    const token = await createSession({
      userId: user.id,
      email: user.email,
      displayName: user.displayName,
    });

    // ─── Set cookie and redirect to dashboard ───
    const redirectUrl = new URL("/dashboard", request.url);
    const response = NextResponse.redirect(redirectUrl, 302);

    response.cookies.set(SESSION_COOKIE, token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
    });

    // Clear the oauth_state cookie
    response.cookies.delete("oauth_state");

    return response;
  } catch (err) {
    console.error("Auth callback error:", err);
    return NextResponse.redirect(new URL("/auth/signin?error=server_error", request.url));
  }
}
