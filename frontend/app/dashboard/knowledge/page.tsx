"use client";

import { BookOpen, GitPullRequest, BrainCircuit, Layers } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function KnowledgePage() {
  const topics = [
    {
      icon: GitPullRequest,
      title: "Pull Request Analysis",
      description:
        "Every merged PR is automatically analyzed using AI to extract risk levels, affected modules, breaking changes, deployment notes, and more.",
      color: "text-violet-400",
    },
    {
      icon: BrainCircuit,
      title: "Engineering Advisor",
      description:
        "The AI Advisor reviews each PR for missing tests, edge cases, security issues, and performance concerns before it goes to production.",
      color: "text-blue-400",
    },
    {
      icon: Layers,
      title: "Semantic Embeddings",
      description:
        "Summaries and engineering impact are embedded as vectors in PostgreSQL (pgvector) enabling fast semantic search across your entire engineering history.",
      color: "text-emerald-400",
    },
    {
      icon: BookOpen,
      title: "Hybrid Search",
      description:
        "The search engine combines natural language intent parsing with SQL filters and vector cosine similarity to surface the most relevant PRs.",
      color: "text-amber-400",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Knowledge Base</h1>
        <p className="text-slate-400">
          How Engineering Memory captures and organizes your team&apos;s knowledge.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {topics.map(({ icon: Icon, title, description, color }) => (
          <Card key={title} className="border-white/10 bg-slate-900/50">
            <CardHeader className="pb-3">
              <CardTitle className={`flex items-center gap-2 text-base ${color}`}>
                <Icon className="h-5 w-5" />
                {title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-white/10 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="text-base text-white">How to connect your GitHub repository</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-400 leading-relaxed">
          <p>
            Engineering Memory ingests data via a GitHub App webhook. Every time a PR is merged, GitHub
            sends a webhook event to <code className="text-violet-400">/github/webhook</code>, which triggers
            the background worker pipeline:
          </p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li>Fetch full PR details, files, commits and reviews from GitHub API</li>
            <li>Parse structural changes (functions, APIs, modules)</li>
            <li>Run AI analysis via OpenAI Structured Outputs</li>
            <li>Generate embeddings and store in pgvector</li>
            <li>Make data available in search and assistant</li>
          </ol>
          <p>
            To set up: create a GitHub App, set the webhook URL, add <code className="text-violet-400">GITHUB_APP_ID</code>,{" "}
            <code className="text-violet-400">GITHUB_APP_PRIVATE_KEY</code> and{" "}
            <code className="text-violet-400">GITHUB_WEBHOOK_SECRET</code> in your <code className="text-violet-400">.env</code> file, then install
            the app on your repositories.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
