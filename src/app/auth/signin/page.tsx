/**
 * Sign-in page — server component, no client-side JavaScript needed.
 *
 * The "Sign in with Microsoft" button is a plain <a> link that navigates
 * to /api/auth/login, which redirects to Microsoft's authorize endpoint.
 * After authentication, Microsoft redirects to /auth/callback which
 * sets the session cookie and redirects to /dashboard.
 */
export default async function SignInPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string; error_description?: string }>;
}) {
  const params = await searchParams;
  const error = params.error;
  const errorDescription = params.error_description;

  // Map OAuth error codes to user-friendly messages
  let errorMessage: string | null = null;
  if (error === "access_denied") {
    errorMessage = "Sign-in was cancelled. Please try again.";
  } else if (error === "invalid_state") {
    errorMessage = "Security validation failed. Please try signing in again.";
  } else if (error === "token_exchange_failed") {
    errorMessage = "Something went wrong during sign-in. Please try again.";
  } else if (error === "graph_failed") {
    errorMessage = "Could not retrieve your profile. Please try again.";
  } else if (error === "missing_params" || error === "no_access_token") {
    errorMessage = "Sign-in was incomplete. Please try again.";
  } else if (error === "server_error") {
    errorMessage = "A server error occurred. Please try again later.";
  } else if (error) {
    errorMessage = errorDescription || "An unexpected error occurred. Please try again.";
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-3xl shadow-xl p-8 w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <img src="/logo.png" alt="CertDuo" className="h-24 w-auto mx-auto mb-4 object-contain" />
          <p className="text-gray-500 text-sm mt-2">Sign in to start your certification journey</p>
        </div>

        {/* Error display */}
        {errorMessage && (
          <div className="bg-red-50 text-red-600 rounded-xl p-3 text-sm mb-4">
            {errorMessage}
          </div>
        )}

        {/* Sign in button — plain link, full page navigation, no JS */}
        <a
          href="/api/auth/login"
          className="w-full flex items-center justify-center gap-3 bg-[#0078D4] text-white py-3.5 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
        >
          <svg width="20" height="20" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="9" height="9" fill="#F25022"/>
            <rect x="11" y="1" width="9" height="9" fill="#7FBA00"/>
            <rect x="1" y="11" width="9" height="9" fill="#00A4EF"/>
            <rect x="11" y="11" width="9" height="9" fill="#FFB900"/>
          </svg>
          Sign in with Microsoft
        </a>

        <p className="text-center text-xs text-gray-400 mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>

        <div className="mt-4 text-center">
          <a href="/" className="text-sm text-[#0078D4] hover:underline">&larr; Back to home</a>
        </div>
      </div>
    </div>
  );
}
