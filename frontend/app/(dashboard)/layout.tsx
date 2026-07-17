"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  BrainCircuit,
  ChevronDown,
  Clock,
  GitPullRequest,
  LayoutDashboard,
  LogOut,
  Search,
  Settings,
  Zap,
} from "lucide-react";

const navItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard" },
  { icon: GitPullRequest, label: "Changes", href: "/dashboard/changes" },
  { icon: BookOpen, label: "Knowledge Base", href: "/dashboard/knowledge" },
  { icon: Clock, label: "Timeline", href: "/dashboard/timeline" },
  { icon: Search, label: "Search", href: "/dashboard/search" },
  { icon: BrainCircuit, label: "AI Advisor", href: "/dashboard/advisor" },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-white">
      {/* Sidebar */}
      <aside className="flex w-64 flex-shrink-0 flex-col border-r border-white/5 bg-slate-900/80 backdrop-blur-sm">
        {/* Logo */}
        <div className="flex h-16 items-center gap-3 border-b border-white/5 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-blue-500 shadow-lg shadow-violet-500/25">
            <Zap className="h-4 w-4 text-white" />
          </div>
          <span className="text-sm font-bold tracking-tight">
            Engineering Memory
          </span>
        </div>

        {/* Org switcher */}
        <div className="border-b border-white/5 px-3 py-3">
          <button
            id="org-switcher"
            className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition hover:bg-white/5"
          >
            <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-emerald-500 to-teal-500 text-xs font-bold text-white">
              A
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-white">
                Acme Corp
              </p>
              <p className="text-xs text-slate-500">Free plan</p>
            </div>
            <ChevronDown className="h-4 w-4 text-slate-400" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            Platform
          </p>
          <ul className="space-y-0.5">
            {navItems.map(({ icon: Icon, label, href }) => {
              const active = pathname === href;
              return (
                <li key={href}>
                  <Link
                    href={href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
                      active
                        ? "bg-violet-600/20 text-violet-300"
                        : "text-slate-400 hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    <Icon
                      className={`h-4 w-4 ${active ? "text-violet-400" : ""}`}
                    />
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Bottom actions */}
        <div className="space-y-0.5 border-t border-white/5 px-3 py-3">
          <Link
            href="/dashboard/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white"
          >
            <Settings className="h-4 w-4" />
            Settings
          </Link>
          <button
            id="logout-btn"
            onClick={() => {
              if (typeof window !== "undefined") {
                localStorage.removeItem("em_access_token");
                window.location.href = "/login";
              }
            }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-red-500/10 hover:text-red-400"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-16 flex-shrink-0 items-center justify-between border-b border-white/5 bg-slate-900/40 px-6 backdrop-blur-sm">
          <div className="relative w-72">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              id="global-search"
              type="text"
              placeholder="Search knowledge base…"
              className="w-full rounded-lg border border-white/10 bg-white/5 py-2 pl-9 pr-4 text-sm text-white placeholder-slate-500 outline-none transition focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30"
            />
          </div>

          {/* Avatar placeholder */}
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-blue-500 text-xs font-bold text-white">
            U
          </div>
        </header>

        {/* Page content */}
        <div className="flex-1 overflow-y-auto p-6">{children}</div>
      </main>
    </div>
  );
}
