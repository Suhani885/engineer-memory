"use client";

import { useState } from "react";
import { GitPullRequest, AlertTriangle, Search, X } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { searchApi, type SearchResult } from "@/lib/api";

const RISK_COLORS: Record<string, string> = {
  High: "bg-red-500/20 text-red-300 border-red-500/30",
  Medium: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  Low: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  Unknown: "bg-slate-500/20 text-slate-300 border-slate-500/30",
};

export default function ChangesPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const data = await searchApi.search(query.trim());
      setResults(data.results ?? []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setQuery("");
    setResults([]);
    setSearched(false);
  };

  return (
    <div className="flex h-full flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Recent Changes</h1>
        <p className="text-slate-400">Search merged pull requests and their AI analysis.</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder='Try "auth changes", "redis migrations", "high risk PRs last week"…'
            className="pl-9 bg-slate-900 border-white/10 text-white placeholder:text-slate-500 focus:border-violet-500"
          />
        </div>
        <Button type="submit" disabled={loading} className="bg-violet-600 hover:bg-violet-700">
          {loading ? "Searching…" : "Search"}
        </Button>
        {searched && (
          <Button type="button" variant="ghost" onClick={clearSearch} className="text-slate-400 hover:text-white">
            <X className="h-4 w-4" />
          </Button>
        )}
      </form>

      {!searched ? (
        <div className="flex h-64 flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-white/10 text-slate-500">
          <GitPullRequest className="h-10 w-10 opacity-30" />
          <p className="text-sm">Use natural language to search your engineering history</p>
          <p className="text-xs opacity-60">e.g. "Who changed the auth module?" or "What was deployed last Friday?"</p>
        </div>
      ) : loading ? (
        <div className="flex h-64 items-center justify-center text-slate-500">Searching…</div>
      ) : results.length === 0 ? (
        <div className="flex h-64 flex-col items-center justify-center gap-2 text-slate-500">
          <AlertTriangle className="h-8 w-8 opacity-40" />
          <p className="text-sm">No results found. Try a different query or connect a GitHub repo first.</p>
        </div>
      ) : (
        <ScrollArea className="flex-1">
          <div className="space-y-3 pr-2">
            {results.map((pr) => (
              <Card key={pr.id} className="border-white/10 bg-slate-900/50 hover:bg-slate-800/60 transition">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-4">
                    <CardTitle className="flex items-center gap-2 text-sm font-semibold text-white">
                      <GitPullRequest className="h-4 w-4 shrink-0 text-violet-400" />
                      #{pr.pr_number} — {pr.title}
                    </CardTitle>
                    <Badge className={`shrink-0 border text-xs ${RISK_COLORS[pr.risk_level ?? "Unknown"]}`}>
                      {pr.risk_level ?? "Unknown"} Risk
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-2">
                  {pr.summary && <p className="text-xs text-slate-400 line-clamp-2">{pr.summary}</p>}
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
                    <span>@{pr.author}</span>
                    <span>{pr.repository}</span>
                    {pr.merged_at && <span>{new Date(pr.merged_at).toLocaleDateString()}</span>}
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
