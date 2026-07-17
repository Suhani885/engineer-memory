export const mockRepositories = [
  { name: "engineer-memory", status: "active", lastSync: "2 mins ago" },
  { name: "frontend-core", status: "active", lastSync: "1 hour ago" },
  { name: "legacy-api", status: "inactive", lastSync: "2 days ago" },
];

export const mockRecentPRs = [
  {
    id: "1",
    repository: "engineer-memory",
    pr_number: 42,
    title: "feat: Add hybrid search and RAG assistant",
    author: "suhani",
    merged_at: "2026-07-17T08:10:00Z",
    risk_level: "High",
  },
  {
    id: "2",
    repository: "frontend-core",
    pr_number: 105,
    title: "fix: Dashboard layout shift on mobile",
    author: "alex",
    merged_at: "2026-07-16T14:20:00Z",
    risk_level: "Low",
  },
  {
    id: "3",
    repository: "engineer-memory",
    pr_number: 41,
    title: "chore: Bump pgvector dependency",
    author: "suhani",
    merged_at: "2026-07-16T11:00:00Z",
    risk_level: "Low",
  },
  {
    id: "4",
    repository: "legacy-api",
    pr_number: 899,
    title: "refactor: Migrate auth tokens to JWT",
    author: "sarah",
    merged_at: "2026-07-15T09:30:00Z",
    risk_level: "Medium",
  },
];

export const mockHighRiskChanges = [
  {
    id: "1",
    title: "feat: Add hybrid search and RAG assistant",
    repository: "engineer-memory",
    pr_number: 42,
    risk_reason: "Introduces new LLM prompt pipeline and direct DB access.",
    author: "suhani",
  },
];

export const mockDailyDigest = `Yesterday, the team focused heavily on search and AI infrastructure. \`engineer-memory\` saw major updates including the introduction of a new hybrid search endpoint and a RAG-powered engineering assistant. \`frontend-core\` had minor bug fixes related to responsive design.`;

export const mockWeeklyDigest = `This week marked a significant architectural shift. We integrated OpenAI Structured Outputs and pgvector natively into our PostgreSQL database, completely bypassing third-party vector stores. The engineering parser was fully deployed, tracking structural changes across 3 repositories. Overall risk has been moderate, but PR #42 in \`engineer-memory\` requires close monitoring post-deployment.`;

export const mockTopContributors = [
  { name: "suhani", changes: 45, prs: 12 },
  { name: "alex", changes: 30, prs: 8 },
  { name: "sarah", changes: 25, prs: 5 },
  { name: "mike", changes: 15, prs: 3 },
];

export const mockChangedModules = [
  { name: "app/api", value: 35, fill: "hsl(var(--chart-1))" },
  { name: "app/models", value: 25, fill: "hsl(var(--chart-2))" },
  { name: "app/services", value: 20, fill: "hsl(var(--chart-3))" },
  { name: "frontend/components", value: 15, fill: "hsl(var(--chart-4))" },
  { name: "infra/db", value: 5, fill: "hsl(var(--chart-5))" },
];
