import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { createSession, SESSION_COOKIE } from "@/lib/auth";

export async function POST(request: NextRequest) {
  try {
    const { accessToken } = await request.json();

    if (!accessToken) {
      return NextResponse.json({ error: "No access token provided" }, { status: 400 });
    }

    // Fetch user profile from Microsoft Graph
    const graphRes = await fetch("https://graph.microsoft.com/v1.0/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!graphRes.ok) {
      return NextResponse.json({ error: "Failed to fetch user profile" }, { status: 401 });
    }

    const profile = await graphRes.json();

    // Fetch profile photo (optional)
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

    // Upsert user in database
    const isNewUser = !(await prisma.user.findUnique({
      where: { microsoftId: profile.id },
    }));

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

    // Create session
    const token = await createSession({
      userId: user.id,
      email: user.email,
      displayName: user.displayName,
    });

    // Return the session token so the client can use /api/auth/establish-session
    // to set the cookie via a real browser navigation (more reliable than fetch Set-Cookie)
    const response = NextResponse.json({ success: true, isNewUser, sessionToken: token });
    response.cookies.set(SESSION_COOKIE, token, {
      httpOnly: true,
      secure: true,
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
    });

    return response;
  } catch (error) {
    console.error("Auth callback error:", error);
    return NextResponse.json({ error: "Authentication failed" }, { status: 500 });
  }
}
