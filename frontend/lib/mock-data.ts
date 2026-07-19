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

export const mockTimelineNodes = [
  {
    id: "author-1",
    type: "author",
    position: { x: 0, y: 0 },
    data: { label: "Suhani", avatar: "SU" },
  },
  {
    id: "pr-1",
    type: "pr",
    position: { x: 0, y: 0 },
    data: {
      label: "PR #42: Hybrid Search",
      repo: "engineer-memory",
      url: "https://github.com/suhani/engineer-memory/pull/42",
    },
  },
  {
    id: "file-1",
    type: "file",
    position: { x: 0, y: 0 },
    data: { label: "search.py" },
  },
  {
    id: "file-2",
    type: "file",
    position: { x: 0, y: 0 },
    data: { label: "assistant.py" },
  },
  {
    id: "module-1",
    type: "module",
    position: { x: 0, y: 0 },
    data: { label: "Backend API" },
  },
  {
    id: "risk-1",
    type: "risk",
    position: { x: 0, y: 0 },
    data: { label: "High Risk", description: "Direct DB Access" },
  },
  {
    id: "deploy-1",
    type: "deploy",
    position: { x: 0, y: 0 },
    data: { label: "Production", status: "Success" },
  },

  {
    id: "author-2",
    type: "author",
    position: { x: 0, y: 0 },
    data: { label: "Alex", avatar: "AL" },
  },
  {
    id: "pr-2",
    type: "pr",
    position: { x: 0, y: 0 },
    data: {
      label: "PR #105: Layout fix",
      repo: "frontend-core",
      url: "https://github.com/suhani/engineer-memory/pull/105",
    },
  },
  {
    id: "file-3",
    type: "file",
    position: { x: 0, y: 0 },
    data: { label: "page.tsx" },
  },
  {
    id: "module-2",
    type: "module",
    position: { x: 0, y: 0 },
    data: { label: "Frontend" },
  },
  {
    id: "risk-2",
    type: "risk",
    position: { x: 0, y: 0 },
    data: { label: "Low Risk", description: "CSS Changes" },
  },
  {
    id: "deploy-2",
    type: "deploy",
    position: { x: 0, y: 0 },
    data: { label: "Preview", status: "Success" },
  },
];

export const mockTimelineEdges = [
  { id: "e1", source: "author-1", target: "pr-1" },
  { id: "e2", source: "pr-1", target: "file-1" },
  { id: "e3", source: "pr-1", target: "file-2" },
  { id: "e4", source: "file-1", target: "module-1" },
  { id: "e5", source: "file-2", target: "module-1" },
  { id: "e6", source: "module-1", target: "risk-1" },
  { id: "e7", source: "risk-1", target: "deploy-1" },

  { id: "e8", source: "author-2", target: "pr-2" },
  { id: "e9", source: "pr-2", target: "file-3" },
  { id: "e10", source: "file-3", target: "module-2" },
  { id: "e11", source: "module-2", target: "risk-2" },
  { id: "e12", source: "risk-2", target: "deploy-2" },
];
