"use client";

import { useState } from "react";
import { Search, Loader2, AlertTriangle, GitPullRequest } from "lucide-react";
import { searchApi, type SearchResult } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

const RISK_COLORS: Record<string, string> = {
  High: "bg-red-500/20 text-red-300 border-red-500/30",
  Medium: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  Low: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  Unknown: "bg-slate-500/20 text-slate-300 border-slate-500/30",
};

const EXAMPLES = [
  "Who modified authentication last month?",
  "Show Redis migrations",
  "What changed yesterday?",
  "Which PR increased deployment risk?",
  "Security changes in the API module",
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (q: string) => {
    if (!q.trim()) return;
    setQuery(q);
    setLoading(true);
    setSearched(true);
    try {
      const data = await searchApi.search(q.trim());
      setResults(data.results ?? []);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(query);
  };

  return (
    <div className="flex h-full flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Hybrid Search</h1>
        <p className="text-slate-400">
          Natural language + vector similarity. Combines SQL filters with semantic search.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search engineering knowledge…"
            className="pl-9 bg-slate-900 border-white/10 text-white placeholder:text-slate-500 focus:border-violet-500"
          />
        </div>
        <Button type="submit" disabled={loading} className="bg-violet-600 hover:bg-violet-700">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Search"}
        </Button>
      </form>

      {!searched ? (
        <div className="flex flex-col items-center gap-6 py-10">
          <p className="text-sm font-medium text-slate-400">Try one of these:</p>
          <div className="flex flex-wrap justify-center gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => handleSearch(ex)}
                className="rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      ) : loading ? (
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-violet-500" />
        </div>
      ) : results.length === 0 ? (
        <div className="flex h-64 flex-col items-center justify-center gap-3 text-slate-500">
          <AlertTriangle className="h-8 w-8 opacity-40" />
          <p className="text-sm">No results. Try different terms or connect a GitHub repo first.</p>
        </div>
      ) : (
        <ScrollArea className="flex-1">
          <div className="space-y-3 pr-2">
            {results.map((r) => (
              <Card key={r.id} className="border-white/10 bg-slate-900/50 hover:bg-slate-800/60 transition">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-4">
                    <CardTitle className="flex items-center gap-2 text-sm font-semibold text-white">
                      <GitPullRequest className="h-4 w-4 shrink-0 text-violet-400" />
                      #{r.pr_number} — {r.title}
                    </CardTitle>
                    <Badge className={`shrink-0 border text-xs ${RISK_COLORS[r.risk_level]}`}>
                      {r.risk_level} Risk
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-2">
                  {r.summary && <p className="text-xs text-slate-400 line-clamp-2">{r.summary}</p>}
                  {r.engineering_impact && (
                    <p className="text-xs text-slate-500 line-clamp-1">Impact: {r.engineering_impact}</p>
                  )}
                  <div className="flex gap-4 text-xs text-slate-500">
                    <span>@{r.author}</span>
                    <span>{r.repository}</span>
                    {r.merged_at && <span>{new Date(r.merged_at).toLocaleDateString()}</span>}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      )}
    </div>
  );
}
