import { NextRequest, NextResponse } from "next/server";
import { verifySession, SESSION_COOKIE } from "@/lib/auth";

/**
 * POST /api/auth/establish-session
 *
 * This endpoint exists because browsers do NOT reliably store Set-Cookie
 * headers from fetch() responses (especially with service workers in play).
 *
 * Instead, the sign-in page does a real form POST here after popup auth.
 * A real navigation means the browser WILL process the Set-Cookie header,
 * and the 302 redirect takes the user to the dashboard.
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const token = formData.get("token") as string;

    if (!token) {
      return NextResponse.redirect(new URL("/auth/signin?error=no_token", request.url));
    }

    // Verify the token is valid before setting it as a cookie
    const session = await verifySession(token);
    if (!session) {
      return NextResponse.redirect(new URL("/auth/signin?error=invalid_token", request.url));
    }

    // 302 redirect to dashboard, setting the session cookie on the response
    const redirectUrl = new URL("/dashboard", request.url);
    const response = NextResponse.redirect(redirectUrl, 302);

    response.cookies.set(SESSION_COOKIE, token, {
      httpOnly: true,
      secure: true,
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
    });

    return response;
  } catch (error) {
    console.error("Establish session error:", error);
    return NextResponse.redirect(new URL("/auth/signin?error=session_failed", request.url));
  }
}
