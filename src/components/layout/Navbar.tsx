"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface NavbarProps {
  user?: {
    displayName: string;
    avatarUrl?: string | null;
    streakCount: number;
  };
}

const NAV_LINKS = [
  { href: "/dashboard", label: "Home", icon: "/icons/icon-home.svg" },
  { href: "/certifications", label: "Certs", icon: "/icons/icon-certs.svg" },
  { href: "/progress", label: "Progress", icon: "/icons/icon-progress.svg" },
  { href: "/settings", label: "Settings", icon: "/icons/icon-settings.svg" },
];

export function Navbar({ user }: NavbarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Top header */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-100 px-4 py-3">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <Image src="/icon-mark.png" alt="CertDuo" width={32} height={32} className="h-8 w-auto object-contain" />
            <span className="font-bold text-gray-900">CertDuo</span>
          </Link>

          {user && (
            <div className="flex items-center gap-3">
              {user.streakCount > 0 && (
                <div className="flex items-center gap-1 text-orange-500 font-semibold text-sm">
                  <span>🔥</span>
                  <span>{user.streakCount}</span>
                </div>
              )}
              <div className="w-8 h-8 rounded-full bg-[#0078D4] flex items-center justify-center text-white text-sm font-semibold">
                {user.displayName.charAt(0).toUpperCase()}
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Bottom mobile nav */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-100 px-4 py-2 safe-area-inset-bottom">
        <div className="max-w-2xl mx-auto flex items-center justify-around">
          {NAV_LINKS.map((link) => {
            const active = pathname === link.href || pathname.startsWith(link.href + "/");
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex flex-col items-center gap-0.5 px-4 py-1.5 rounded-xl transition-colors",
                  active ? "text-[#0078D4]" : "text-gray-400"
                )}
              >
                <Image
                  src={link.icon}
                  alt={link.label}
                  width={24}
                  height={24}
                  className={cn(
                    "transition-all",
                    active
                      ? "[filter:invert(29%)_sepia(89%)_saturate(1200%)_hue-rotate(190deg)_brightness(95%)]"
                      : "opacity-40"
                  )}
                />
                <span className="text-xs font-medium">{link.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
