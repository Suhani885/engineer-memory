"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

import { Download, FileText, Loader2, FileDown, Plus } from "lucide-react";
import { releaseApi, ReleaseResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";

export default function ReleasesPage() {
  const [releases, setReleases] = useState<ReleaseResponse[]>([]);
  const [activeRelease, setActiveRelease] = useState<ReleaseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  
  const [startTag, setStartTag] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endTag, setEndTag] = useState("");
  const [endDate, setEndDate] = useState("");

  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchReleases();
  }, []);

  const fetchReleases = async () => {
    try {
      const data = await releaseApi.list();
      setReleases(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!startTag || !startDate || !endTag || !endDate) return;
    
    setGenerating(true);
    try {
      const newRelease = await releaseApi.generate({
        start_tag_name: startTag,
        end_tag_name: endTag,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
      });
      await fetchReleases();
      handleView(newRelease.id);
      setShowForm(false);
    } catch (err) {
      console.error("Failed to generate release notes", err);
      alert("Generation failed. Check console for details.");
    } finally {
      setGenerating(false);
    }
  };

  const handleView = async (id: string) => {
    setLoading(true);
    setShowForm(false);
    try {
      const data = await releaseApi.get(id);
      setActiveRelease(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const exportMarkdown = () => {
    if (!activeRelease?.markdown_content) return;
    const blob = new Blob([activeRelease.markdown_content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `release-notes-${activeRelease.end_tag_name}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportPdf = async () => {
    if (!contentRef.current || !activeRelease) return;
    const html2pdf = (await import("html2pdf.js")).default;
    const opt = {
      margin: 10,
      filename: `release-notes-${activeRelease.end_tag_name}.pdf`,
      image: { type: 'jpeg' as const, quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0f172a' },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' as const }
    };

    html2pdf().set(opt).from(contentRef.current).save();
  };

  return (
    <div className="flex h-full flex-col gap-6 lg:flex-row">
      <div className="flex w-full flex-col gap-4 lg:w-1/3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Release Notes</h1>
            <p className="text-slate-400">Generate notes between Git tags.</p>
          </div>
          <Button 
            size="icon"
            className="bg-emerald-600 hover:bg-emerald-700" 
            onClick={() => setShowForm(true)}
          >
            <Plus className="h-5 w-5" />
          </Button>
        </div>

        <Card className="flex-1 overflow-hidden border-white/10 bg-slate-900/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-300">Generated Releases</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[calc(100vh-220px)]">
              <div className="flex flex-col">
                {releases.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => handleView(r.id)}
                    className={`flex flex-col items-start gap-1 border-b border-white/5 p-4 text-left transition hover:bg-white/5 ${activeRelease?.id === r.id && !showForm ? 'bg-white/5 border-l-2 border-l-emerald-500' : ''}`}
                  >
                    <div className="flex w-full items-center justify-between">
                      <span className="font-semibold text-emerald-400">{r.start_tag_name} ➔ {r.end_tag_name}</span>
                    </div>
                    <span className="text-xs text-slate-400">
                      {new Date(r.created_at).toLocaleDateString()}
                    </span>
                  </button>
                ))}
                {releases.length === 0 && (
                  <div className="p-4 text-center text-sm text-slate-500">No release notes yet.</div>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <div className="flex-1 rounded-xl border border-white/10 bg-slate-900/50 p-6 shadow-xl relative overflow-hidden flex flex-col">
        {showForm ? (
          <div className="mx-auto w-full max-w-md pt-10">
            <h2 className="mb-6 text-2xl font-bold text-white">Generate Release Notes</h2>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Start Tag</label>
                  <Input required placeholder="v1.0.0" value={startTag} onChange={(e) => setStartTag(e.target.value)} className="bg-slate-800 border-white/10 text-white" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">Start Date</label>
                  <Input required type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="bg-slate-800 border-white/10 text-white [color-scheme:dark]" />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">End Tag</label>
                  <Input required placeholder="v1.1.0" value={endTag} onChange={(e) => setEndTag(e.target.value)} className="bg-slate-800 border-white/10 text-white" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">End Date</label>
                  <Input required type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="bg-slate-800 border-white/10 text-white [color-scheme:dark]" />
                </div>
              </div>

              <Button type="submit" disabled={generating} className="w-full bg-emerald-600 hover:bg-emerald-700 mt-4">
                {generating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
                {generating ? "Generating Notes..." : "Generate Notes"}
              </Button>
            </form>
          </div>
        ) : loading ? (
          <div className="flex h-full items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
          </div>
        ) : activeRelease ? (
          <>
            <div className="mb-6 flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <h2 className="text-xl font-bold text-white">Release {activeRelease.end_tag_name}</h2>
                <p className="text-xs text-slate-400">
                  Compared against {activeRelease.start_tag_name}
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
              <div ref={contentRef} className="prose prose-invert prose-emerald max-w-none text-slate-300">
                <ReactMarkdown>{activeRelease.markdown_content || "*No content*"}</ReactMarkdown>
              </div>
            </ScrollArea>
          </>
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            Select a release to view its contents, or click + to generate a new one.
          </div>
        )}
      </div>
    </div>
  );
}
