"use client";

import { memo } from "react";
import { Handle, Position, NodeProps, Node } from "@xyflow/react";
import {
  AlertTriangle,
  FileCode2,
  FolderTree,
  Github,
  Rocket,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

// Helper for handles
const Handles = () => (
  <>
    <Handle
      type="target"
      position={Position.Top}
      className="h-2 w-2 !border-slate-800 !bg-slate-600"
    />
    <Handle
      type="source"
      position={Position.Bottom}
      className="h-2 w-2 !border-slate-800 !bg-slate-600"
    />
  </>
);

export interface TimelineNodeData extends Record<string, unknown> {
  label: string;
  avatar?: string;
  repo?: string;
  url?: string;
  description?: string;
}

export const AuthorNode = memo(({ data }: NodeProps<Node<TimelineNodeData>>) => {
  return (
    <div className="flex items-center gap-3 rounded-full border border-white/10 bg-slate-900/80 p-2 pr-4 shadow-lg backdrop-blur-xl">
      <Handles />
      <Avatar className="h-8 w-8 border border-white/10">
        <AvatarFallback className="bg-gradient-to-br from-violet-500 to-purple-500 text-xs font-bold text-white">
          {data.avatar}
        </AvatarFallback>
      </Avatar>
      <div className="flex flex-col">
        <span className="text-xs font-medium text-slate-400">Author</span>
        <span className="text-sm font-semibold text-slate-200">
          {data.label}
        </span>
      </div>
    </div>
  );
});
AuthorNode.displayName = "AuthorNode";

export const PRNode = memo(({ data }: NodeProps<Node<TimelineNodeData>>) => {
  return (
    <div
      className="group flex cursor-pointer flex-col gap-2 rounded-xl border border-white/10 bg-slate-900/80 p-4 shadow-lg backdrop-blur-xl transition hover:border-violet-500/50 hover:bg-slate-800/80"
      onClick={() => window.open(data.url, "_blank")}
    >
      <Handles />
      <div className="flex items-center gap-2">
        <Github className="h-4 w-4 text-slate-400 group-hover:text-violet-400" />
        <span className="text-xs font-medium text-slate-400">{data.repo}</span>
      </div>
      <span className="text-sm font-semibold text-slate-200">{data.label}</span>
    </div>
  );
});
PRNode.displayName = "PRNode";

export const FileNode = memo(({ data }: NodeProps<Node<TimelineNodeData>>) => {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-slate-900/80 px-3 py-2 shadow-lg backdrop-blur-xl">
      <Handles />
      <FileCode2 className="h-4 w-4 text-blue-400" />
      <span className="text-xs font-medium text-slate-300">{data.label}</span>
    </div>
  );
});
FileNode.displayName = "FileNode";

export const ModuleNode = memo(({ data }: NodeProps<Node<TimelineNodeData>>) => {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-l-4 border-white/10 border-l-emerald-500 bg-slate-900/80 px-4 py-2 shadow-lg backdrop-blur-xl">
      <Handles />
      <FolderTree className="h-4 w-4 text-emerald-400" />
      <span className="text-xs font-semibold text-emerald-100">
        {data.label}
      </span>
    </div>
  );
});
ModuleNode.displayName = "ModuleNode";

export const RiskNode = memo(({ data }: NodeProps<Node<TimelineNodeData>>) => {
  const isHigh = data.label?.includes("High");
  return (
    <div
      className={`flex flex-col gap-1 rounded-lg border px-3 py-2 shadow-lg backdrop-blur-xl ${isHigh ? "border-rose-500/30 bg-rose-500/10" : "border-amber-500/30 bg-amber-500/10"}`}
    >
      <Handles />
      <div className="flex items-center gap-2">
        <AlertTriangle
          className={`h-4 w-4 ${isHigh ? "text-rose-400" : "text-amber-400"}`}
        />
        <span
          className={`text-xs font-bold ${isHigh ? "text-rose-400" : "text-amber-400"}`}
        >
          {data.label}
        </span>
      </div>
      <span
        className={`text-[10px] ${isHigh ? "text-rose-300/70" : "text-amber-300/70"}`}
      >
        {data.description}
      </span>
    </div>
  );
});
RiskNode.displayName = "RiskNode";

export const DeployNode = memo(({ data }: NodeProps<Node<TimelineNodeData>>) => {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 shadow-lg backdrop-blur-xl">
      <Handles />
      <Rocket className="h-4 w-4 text-cyan-400" />
      <span className="text-xs font-bold text-cyan-400">{data.label}</span>
    </div>
  );
});
DeployNode.displayName = "DeployNode";
