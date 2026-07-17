"use client";

import {
  AlertTriangle,
  GitPullRequest,
  Search,
  Activity,
  Github,
  CalendarDays,
  FileText,
  User,
} from "lucide-react";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  mockChangedModules,
  mockDailyDigest,
  mockHighRiskChanges,
  mockRecentPRs,
  mockRepositories,
  mockTopContributors,
  mockWeeklyDigest,
} from "@/lib/mock-data";

export default function DashboardPage() {
  return (
    <div className="flex flex-col space-y-8 p-4 md:p-8">
      {/* Header & Search */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Dashboard
          </h1>
          <p className="text-slate-400">Your engineering memory at a glance.</p>
        </div>
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search natural language (e.g. 'Who modified auth?')"
            className="w-full border-white/10 bg-slate-900/50 pl-10 text-white ring-offset-slate-950 placeholder:text-slate-500 focus-visible:ring-violet-500"
          />
        </div>
      </div>

      {/* Digests & High Risk Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Daily Digest */}
        <Card className="border-white/5 bg-white/[2%] backdrop-blur">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              Daily Digest
            </CardTitle>
            <CalendarDays className="h-4 w-4 text-violet-400" />
          </CardHeader>
          <CardContent>
            <p className="text-xs leading-relaxed text-slate-400">
              {mockDailyDigest}
            </p>
          </CardContent>
        </Card>

        {/* Weekly Digest */}
        <Card className="border-white/5 bg-white/[2%] backdrop-blur">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              Weekly Digest
            </CardTitle>
            <FileText className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <p className="text-xs leading-relaxed text-slate-400">
              {mockWeeklyDigest}
            </p>
          </CardContent>
        </Card>

        {/* High Risk Changes */}
        <Card className="border-rose-500/20 bg-rose-500/5 backdrop-blur">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-rose-400">
              High Risk Active PRs
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-rose-500" />
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[120px]">
              <div className="space-y-4">
                {mockHighRiskChanges.map((change) => (
                  <div key={change.id} className="flex flex-col space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-200">
                        {change.repository} #{change.pr_number}
                      </span>
                      <Badge
                        variant="destructive"
                        className="border-none bg-rose-500/20 text-rose-300 hover:bg-rose-500/30"
                      >
                        Risk
                      </Badge>
                    </div>
                    <p className="text-xs text-rose-200/70">
                      {change.risk_reason}
                    </p>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Top Contributors Bar Chart */}
        <Card className="border-white/5 bg-white/[2%] backdrop-blur lg:col-span-4">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-300">
              Top Contributors
            </CardTitle>
          </CardHeader>
          <CardContent className="pl-2">
            <ChartContainer
              config={{
                changes: {
                  label: "Changes",
                  color: "hsl(var(--chart-1))",
                },
              }}
              className="h-[300px] w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockTopContributors}>
                  <XAxis
                    dataKey="name"
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}`}
                  />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar
                    dataKey="changes"
                    fill="var(--color-changes)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Most Changed Modules Pie Chart */}
        <Card className="border-white/5 bg-white/[2%] backdrop-blur lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-300">
              Most Changed Modules
            </CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ChartContainer
              config={{
                value: {
                  label: "Changes",
                },
              }}
              className="h-[300px] w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Pie
                    data={mockChangedModules}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {mockChangedModules.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Grid: Repositories & Recent PRs */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Repositories */}
        <Card className="border-white/5 bg-white/[2%] backdrop-blur">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-slate-300">
              <Github className="h-4 w-4" />
              Connected Repositories
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockRepositories.map((repo) => (
                <div
                  key={repo.name}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center space-x-2">
                    <Activity
                      className={`h-4 w-4 ${repo.status === "active" ? "text-emerald-400" : "text-slate-500"}`}
                    />
                    <span className="text-sm font-medium text-slate-200">
                      {repo.name}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500">
                    {repo.lastSync}
                  </span>
                </div>
              ))}
            </div>
            <Button
              variant="outline"
              className="mt-6 w-full border-white/10 bg-transparent text-slate-300 hover:bg-white/5"
            >
              Add Repository
            </Button>
          </CardContent>
        </Card>

        {/* Recent PRs Table */}
        <Card className="border-white/5 bg-white/[2%] backdrop-blur lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-slate-300">
              <GitPullRequest className="h-4 w-4" />
              Recent Pull Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="border-white/5 hover:bg-transparent">
                  <TableHead className="text-slate-400">Repository</TableHead>
                  <TableHead className="text-slate-400">PR</TableHead>
                  <TableHead className="text-slate-400">Author</TableHead>
                  <TableHead className="text-slate-400">Risk</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockRecentPRs.map((pr) => (
                  <TableRow
                    key={pr.id}
                    className="border-white/5 transition-colors hover:bg-white/5"
                  >
                    <TableCell className="font-medium text-slate-300">
                      {pr.repository}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="text-sm text-slate-200">
                          {pr.title}
                        </span>
                        <span className="text-xs text-slate-500">
                          #{pr.pr_number}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Avatar className="h-6 w-6 border border-white/10">
                          <AvatarFallback className="bg-slate-800 text-xs">
                            {pr.author.substring(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-sm text-slate-300">
                          {pr.author}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          pr.risk_level === "High"
                            ? "destructive"
                            : pr.risk_level === "Medium"
                              ? "secondary"
                              : "default"
                        }
                        className={` ${pr.risk_level === "High" ? "border-none bg-rose-500/20 text-rose-300 hover:bg-rose-500/30" : ""} ${pr.risk_level === "Medium" ? "border-none bg-amber-500/20 text-amber-300 hover:bg-amber-500/30" : ""} ${pr.risk_level === "Low" ? "border-none bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30" : ""} `}
                      >
                        {pr.risk_level}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
