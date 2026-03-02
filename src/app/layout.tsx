import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CertDuo — Microsoft Certification Prep",
  description: "Duolingo-style Microsoft Certification Preparation. AZ-900, AZ-104, MD-102, MS-102.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "CertDuo",
    startupImage: "/icons/apple-touch-icon.png",
  },
  icons: {
    apple: "/icons/apple-touch-icon.png",
    icon: "/icons/icon-192.png",
  },
  formatDetection: {
    telephone: false,
  },
  openGraph: {
    type: "website",
    title: "CertDuo",
    description: "Duolingo-style Microsoft Certification Prep",
  },
};

export const viewport: Viewport = {
  themeColor: "#0078D4",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-white`}>
        {children}
      </body>
    </html>
  );
}
