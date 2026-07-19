"use client";

import { useMemo, useState, useEffect } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Edge,
  Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";
import { Search } from "lucide-react";

import { mockTimelineNodes, mockTimelineEdges } from "@/lib/mock-data";
import {
  AuthorNode,
  PRNode,
  FileNode,
  ModuleNode,
  RiskNode,
  DeployNode,
} from "@/components/timeline-nodes";

const nodeTypes = {
  author: AuthorNode,
  pr: PRNode,
  file: FileNode,
  module: ModuleNode,
  risk: RiskNode,
  deploy: DeployNode,
};

// Dagre setup for auto layout
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 220;
const nodeHeight = 80;

const getLayoutedElements = (
  nodes: Node[],
  edges: Edge[],
  direction = "LR",
) => {
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: newNodes, edges };
};

export default function TimelinePage() {
  const [search, setSearch] = useState("");
  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(
    () => getLayoutedElements(mockTimelineNodes, mockTimelineEdges),
    [],
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, , onEdgesChange] = useEdgesState(layoutedEdges);

  // Apply search filter
  useEffect(() => {
    if (!search.trim()) {
      setNodes((nds) => nds.map((n) => ({ ...n, style: { opacity: 1 } })));
      return;
    }

    const query = search.toLowerCase();
    setNodes((nds) =>
      nds.map((n) => {
        const matches =
          (n.data?.label as string)?.toLowerCase().includes(query) ||
          (n.data?.repo as string)?.toLowerCase().includes(query) ||
          (n.data?.description as string)?.toLowerCase().includes(query);
        return {
          ...n,
          style: { opacity: matches ? 1 : 0.2, transition: "opacity 0.2s" },
        };
      }),
    );
  }, [search, setNodes]);

  return (
    <div className="flex h-full flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Engineering Timeline
        </h1>
        <p className="text-slate-400">
          Trace the lifecycle of changes from code to deployment.
        </p>
      </div>

      <div className="relative w-full max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by author, PR, or module..."
          className="w-full rounded-lg border border-white/10 bg-white/5 py-2 pl-9 pr-4 text-sm text-white placeholder-slate-500 outline-none transition focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30"
        />
      </div>

      <div className="relative flex-1 overflow-hidden rounded-xl border border-white/5 bg-slate-900/50 shadow-inner">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          className="dark"
        >
          <Background color="#334155" gap={24} size={2} />
          <Controls className="!border-white/10 !bg-slate-800 !fill-white" />
        </ReactFlow>
      </div>
    </div>
  );
}
