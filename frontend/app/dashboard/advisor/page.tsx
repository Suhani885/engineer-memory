"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Send, BrainCircuit, Loader2, Bot } from "lucide-react";
import { assistantApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const EXAMPLE_QUESTIONS = [
  "Who last modified the authentication module?",
  "What changed yesterday with high deployment risk?",
  "Show me all Redis-related migrations",
  "Which PRs introduced breaking API changes?",
  "What are the most common security findings?",
];

export default function AdvisorPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (question: string) => {
    if (!question.trim() || loading) return;
    const userMsg: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await assistantApi.ask(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Error: " + (err instanceof Error ? err.message : "Unknown error"),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="flex h-full flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">AI Engineering Advisor</h1>
        <p className="text-slate-400">Ask questions about your codebase, PRs, and engineering history.</p>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-white/10 bg-slate-900/50">
        <ScrollArea className="flex-1 p-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center gap-8 py-10">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 to-blue-500 shadow-lg shadow-violet-500/25">
                <BrainCircuit className="h-8 w-8 text-white" />
              </div>
              <div className="text-center">
                <h2 className="text-lg font-semibold text-white">Engineering Memory Assistant</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Powered by your PR history and AI analysis. Never hallucinates — always cites PRs.
                </p>
              </div>
              <div className="grid w-full max-w-xl gap-2">
                {EXAMPLE_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-left text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
                >
                  <div
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                      msg.role === "user"
                        ? "bg-violet-600"
                        : "bg-slate-700"
                    }`}
                  >
                    {msg.role === "user" ? (
                      <span className="text-xs font-bold text-white">U</span>
                    ) : (
                      <Bot className="h-4 w-4 text-slate-300" />
                    )}
                  </div>
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                      msg.role === "user"
                        ? "bg-violet-600 text-white rounded-tr-sm"
                        : "bg-slate-800 text-slate-200 rounded-tl-sm"
                    }`}
                  >
                    {msg.role === "assistant" ? (
                      <div className="prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    ) : (
                      msg.content
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-700">
                    <Bot className="h-4 w-4 text-slate-300" />
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm bg-slate-800 px-4 py-3 text-sm text-slate-400">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Thinking…
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </ScrollArea>

        <div className="border-t border-white/10 p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your engineering history…"
              disabled={loading}
              className="flex-1 bg-slate-800 border-white/10 text-white placeholder:text-slate-500 focus:border-violet-500"
            />
            <Button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-violet-600 hover:bg-violet-700"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
