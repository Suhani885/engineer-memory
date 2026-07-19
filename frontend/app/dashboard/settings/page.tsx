"use client";

import { useState, useEffect } from "react";
import { Settings, User, Key, Github, Server } from "lucide-react";
import { authApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const [user, setUser] = useState<{ email: string; full_name: string | null } | null>(null);

  useEffect(() => {
    authApi.me().then(setUser).catch(console.error);
  }, []);

  const envVars = [
    { key: "OPENAI_API_KEY", desc: "Required for AI summaries, advisor, embeddings, search and digests." },
    { key: "GITHUB_APP_ID", desc: "Your GitHub App ID for webhook ingestion." },
    { key: "GITHUB_APP_PRIVATE_KEY", desc: "Private key PEM for GitHub App authentication." },
    { key: "GITHUB_WEBHOOK_SECRET", desc: "Shared secret to validate incoming webhook payloads." },
  ];

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Settings</h1>
        <p className="text-slate-400">Manage your account and configuration.</p>
      </div>

      <Card className="border-white/10 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <User className="h-4 w-4 text-violet-400" /> Account
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {user ? (
            <>
              <div className="space-y-1">
                <p className="text-xs text-slate-500">Email</p>
                <Input value={user.email} readOnly className="bg-slate-800 border-white/10 text-white" />
              </div>
              {user.full_name && (
                <div className="space-y-1">
                  <p className="text-xs text-slate-500">Full Name</p>
                  <Input value={user.full_name} readOnly className="bg-slate-800 border-white/10 text-white" />
                </div>
              )}
            </>
          ) : (
            <p className="text-sm text-slate-500">Loading account details…</p>
          )}
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Key className="h-4 w-4 text-amber-400" /> Environment Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-xs text-slate-400">
            These values are configured in your <code className="text-violet-400">.env</code> file at the project root. Restart the containers after any changes.
          </p>
          <div className="space-y-3">
            {envVars.map(({ key, desc }) => (
              <div key={key} className="rounded-lg border border-white/10 bg-slate-800/60 p-3">
                <p className="text-xs font-mono font-bold text-violet-300">{key}</p>
                <p className="mt-0.5 text-xs text-slate-400">{desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-slate-900/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Github className="h-4 w-4 text-slate-300" /> GitHub Integration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-400">
          <ol className="list-decimal list-inside space-y-2">
            <li>Go to <strong className="text-white">GitHub → Settings → Developer Settings → GitHub Apps</strong></li>
            <li>Create a new GitHub App with <strong className="text-white">Pull Request</strong> read permissions and webhook events for <code className="text-violet-400">pull_request</code></li>
            <li>Set the webhook URL to <code className="text-violet-400">https://your-domain/github/webhook</code></li>
            <li>Copy the App ID and private key into your <code className="text-violet-400">.env</code> file</li>
            <li>Install the app on your repositories</li>
            <li>Run <code className="text-violet-400">docker compose up -d</code> to restart with new credentials</li>
          </ol>
          <Button variant="outline" className="w-full border-white/10 text-slate-300 hover:bg-white/10 mt-2" onClick={() => window.open("https://github.com/settings/apps/new", "_blank")}>
            <Github className="mr-2 h-4 w-4" /> Create GitHub App
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
