"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="w-12 h-12 rounded-2xl border-[4px] border-slate-700 bg-slate-800 dark:bg-slate-800 shadow-[4px_4px_0_rgba(51,65,85,1)] flex items-center justify-center text-2xl transition-colors hover:-translate-y-0.5 active:translate-y-0.5 transform"
      title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
    >
      {isDark ? "☀️" : "🌙"}
    </button>
  );
}
