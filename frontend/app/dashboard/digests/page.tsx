"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

import { Download, FileText, Loader2, FileDown } from "lucide-react";
import { digestApi, DigestResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function DigestsPage() {
  const [digests, setDigests] = useState<DigestResponse[]>([]);
  const [activeDigest, setActiveDigest] = useState<DigestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState<"daily" | "weekly" | null>(null);
  
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchDigests();
  }, []);

  const fetchDigests = async () => {
    try {
      const data = await digestApi.list();
      setDigests(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async (type: "daily" | "weekly") => {
    setGenerating(type);
    try {
      const newDigest = await digestApi.generate(type);
      await fetchDigests();
      handleView(newDigest.id);
    } catch (err) {
      console.error("Failed to generate digest", err);
      alert("Generation failed. See console for details.");
    } finally {
      setGenerating(null);
    }
  };

  const handleView = async (id: string) => {
    setLoading(true);
    try {
      const data = await digestApi.get(id);
      setActiveDigest(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const exportMarkdown = () => {
    if (!activeDigest?.markdown_content) return;
    const blob = new Blob([activeDigest.markdown_content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `engineering-digest-${activeDigest.digest_type}-${activeDigest.id.slice(0, 8)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportPdf = async () => {
    if (!contentRef.current || !activeDigest) return;
    const html2pdf = (await import("html2pdf.js")).default;
    const opt = {
      margin: 10,
      filename: `engineering-digest-${activeDigest.digest_type}-${activeDigest.id.slice(0, 8)}.pdf`,
      image: { type: 'jpeg' as const, quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0f172a' },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' as const }
    };

    html2pdf().set(opt).from(contentRef.current).save();
  };

  return (
    <div className="flex h-full flex-col gap-6 lg:flex-row">
      <div className="flex w-full flex-col gap-4 lg:w-1/3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Engineering Digests</h1>
          <p className="text-slate-400">AI-generated summaries of merged PRs and engineering impact.</p>
        </div>
        
        <div className="flex gap-2">
          <Button 
            className="w-full bg-violet-600 hover:bg-violet-700" 
            onClick={() => handleGenerate("daily")}
            disabled={!!generating}
          >
            {generating === "daily" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
            Daily
          </Button>
          <Button 
            className="w-full bg-purple-600 hover:bg-purple-700"
            onClick={() => handleGenerate("weekly")}
            disabled={!!generating}
          >
            {generating === "weekly" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
            Weekly
          </Button>
        </div>

        <Card className="flex-1 overflow-hidden border-white/10 bg-slate-900/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-300">Recent Digests</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[calc(100vh-280px)]">
              <div className="flex flex-col">
                {digests.map((d) => (
                  <button
                    key={d.id}
                    onClick={() => handleView(d.id)}
                    className={`flex flex-col items-start gap-1 border-b border-white/5 p-4 text-left transition hover:bg-white/5 ${activeDigest?.id === d.id ? 'bg-white/5 border-l-2 border-l-violet-500' : ''}`}
                  >
                    <div className="flex w-full items-center justify-between">
                      <span className="font-semibold text-slate-200 capitalize">{d.digest_type} Digest</span>
                    </div>
                    <span className="text-xs text-slate-400">
                      {new Date(d.period_start).toLocaleDateString()} - {new Date(d.period_end).toLocaleDateString()}
                    </span>
                  </button>
                ))}
                {digests.length === 0 && (
                  <div className="p-4 text-center text-sm text-slate-500">No digests generated yet.</div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <div className="flex-1 rounded-xl border border-white/10 bg-slate-900/50 p-6 shadow-xl relative overflow-hidden flex flex-col">
        {loading ? (
          <div className="flex h-full items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-violet-500" />
          </div>
        ) : activeDigest ? (
          <>
            <div className="mb-6 flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <h2 className="text-xl font-bold text-white capitalize">{activeDigest.digest_type} Digest</h2>
                <p className="text-xs text-slate-400">
                  {new Date(activeDigest.period_start).toLocaleDateString()} to {new Date(activeDigest.period_end).toLocaleDateString()}
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={exportMarkdown} className="border-white/10 text-slate-300 hover:bg-white/10">
                  <FileDown className="mr-2 h-4 w-4" />
                  Markdown
                </Button>
                <Button variant="outline" size="sm" onClick={exportPdf} className="border-white/10 text-slate-300 hover:bg-white/10">
                  <Download className="mr-2 h-4 w-4" />
                  PDF
                </Button>
              </div>
            </div>
            
            <ScrollArea className="flex-1 pr-4">
              <div ref={contentRef} className="prose prose-invert prose-violet max-w-none text-slate-300">
                <ReactMarkdown>{activeDigest.markdown_content || "*No content*"}</ReactMarkdown>
              </div>
            </ScrollArea>
          </>
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            Select a digest to view its contents, or generate a new one.
          </div>
        )}
      </div>
    </div>
  );
}
