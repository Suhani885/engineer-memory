import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  Clock,
  GitPullRequest,
  Search,
  Zap,
} from "lucide-react";
import Link from "next/link";

const features = [
  {
    icon: GitPullRequest,
    title: "GitHub Integration",
    description: "Connect repositories and automatically capture every PR, commit, and deployment.",
    href: "/dashboard/changes",
    color: "from-orange-500 to-amber-500",
    badge: "Coming soon",
  },
  {
    icon: BrainCircuit,
    title: "AI Change Understanding",
    description: "Automatically summarise what changed, why it changed, and what it affects.",
    href: "/dashboard/advisor",
    color: "from-violet-500 to-purple-500",
    badge: "Coming soon",
  },
  {
    icon: BookOpen,
    title: "Knowledge Base",
    description: "Auto-generated, searchable documentation built from your engineering activity.",
    href: "/dashboard/knowledge",
    color: "from-blue-500 to-cyan-500",
    badge: "Coming soon",
  },
  {
    icon: Search,
    title: "Natural Language Search",
    description: "Ask questions in plain English and get answers grounded in your team's history.",
    href: "/dashboard/search",
    color: "from-emerald-500 to-teal-500",
    badge: "Coming soon",
  },
  {
    icon: Clock,
    title: "Engineering Timeline",
    description: "A chronological view of every engineering decision, deployment, and incident.",
    href: "/dashboard/timeline",
    color: "from-rose-500 to-pink-500",
    badge: "Coming soon",
  },
  {
    icon: Zap,
    title: "AI Engineering Advisor",
    description: "Chat with your engineering history to understand patterns, risk, and impact.",
    href: "/dashboard/advisor",
    color: "from-yellow-500 to-orange-500",
    badge: "Coming soon",
  },
];

const stats = [
  { label: "Repositories", value: "0" },
  { label: "Changes indexed", value: "0" },
  { label: "Knowledge entries", value: "0" },
  { label: "Team members", value: "1" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-600/20 via-blue-600/10 to-transparent p-6 ring-1 ring-white/10">
        <div className="absolute right-4 top-4 h-32 w-32 rounded-full bg-violet-500/10 blur-2xl" />
        <div className="relative">
          <p className="text-sm font-medium text-violet-400">Welcome to</p>
          <h1 className="mt-1 text-2xl font-bold text-white">Engineering Memory</h1>
          <p className="mt-2 max-w-lg text-sm text-slate-400">
            Your workspace is ready. Connect your first GitHub repository to start capturing your
            engineering knowledge automatically.
          </p>
          <Link
            href="/dashboard/changes"
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-violet-600/25 transition hover:bg-violet-500"
          >
            Connect GitHub
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map(({ label, value }) => (
          <div
            key={label}
            className="rounded-xl border border-white/5 bg-white/[3%] p-4 ring-1 ring-white/5"
          >
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="mt-1 text-xs text-slate-500">{label}</p>
          </div>
        ))}
      </div>

      {/* Feature cards */}
      <div>
        <h2 className="mb-4 text-base font-semibold text-white">Platform Features</h2>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {features.map(({ icon: Icon, title, description, href, color, badge }) => (
            <Link
              key={title}
              href={href}
              className="group relative overflow-hidden rounded-xl border border-white/5 bg-white/[3%] p-5 ring-1 ring-white/5 transition hover:border-white/10 hover:bg-white/5"
            >
              <div
                className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${color} shadow-lg`}
              >
                <Icon className="h-5 w-5 text-white" />
              </div>
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-sm font-semibold text-white">{title}</h3>
                {badge && (
                  <span className="flex-shrink-0 rounded-md bg-slate-700 px-2 py-0.5 text-[10px] font-medium text-slate-400">
                    {badge}
                  </span>
                )}
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-slate-400">{description}</p>
              <ArrowRight className="absolute bottom-4 right-4 h-4 w-4 text-slate-600 transition group-hover:translate-x-1 group-hover:text-slate-400" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
