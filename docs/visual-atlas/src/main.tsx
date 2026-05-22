import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Background,
  BackgroundVariant,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import ELK from "elkjs/lib/elk.bundled.js";
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronLeft,
  Code2,
  Copy,
  ExternalLink,
  FileCode2,
  Layers3,
  LockKeyhole,
  PanelRight,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";
import {
  atlasEdges,
  atlasNodes,
  drilldowns,
  gates,
  journeys,
  nodeKindLabels,
  type AtlasNode,
  type AtlasView,
} from "./atlas-data";
import "./styles.css";

type FlowNodeData = {
  atlas: AtlasNode;
  selected: boolean;
};

const elk = new ELK();

const viewLabels: Record<AtlasView, string> = {
  overview: "Como tudo se conecta",
  runtime: "Runtime",
  protected: "Dados protegidos",
  rag: "RAG",
  operations: "Operacao",
};

const readingModes = [
  {
    label: "Entender",
    kind: "Explicacao",
    detail: "Comece pelo macro e use o inspetor para entender por que cada parte existe.",
  },
  {
    label: "Operar",
    kind: "How-to",
    detail: "Use Operacao e gates quando a pergunta for como rodar, validar ou liberar.",
  },
  {
    label: "Consultar",
    kind: "Referencia",
    detail: "Use arquivos reais, guardrails e relacoes para chegar ao contrato no codigo.",
  },
  {
    label: "Aprender fluxo",
    kind: "Tutorial",
    detail: "Abra microfluxos para seguir um caminho completo, passo a passo.",
  },
];

function readInitialRoute() {
  const params = new URLSearchParams(window.location.hash.replace(/^#/, ""));
  const routeView = params.get("view") as AtlasView | null;
  const view = routeView && journeys.some((item) => item.id === routeView) ? routeView : "overview";
  const routeDrilldown = params.get("drill");
  return {
    view,
    drilldownId: routeDrilldown && drilldowns[routeDrilldown] ? routeDrilldown : null,
    query: params.get("q") ?? "",
    selectedId: params.get("node") ?? "",
  };
}

const kindTone: Record<string, string> = {
  channel: "tone-channel",
  service: "tone-service",
  runtime: "tone-runtime",
  endpoint: "tone-contract",
  contract: "tone-contract",
  data: "tone-data",
  policy: "tone-policy",
  pipeline: "tone-pipeline",
  document: "tone-document",
  gate: "tone-gate",
};

function AtlasNodeCard({ data }: NodeProps<Node<FlowNodeData>>) {
  const Icon = data.atlas.icon;
  return (
    <div className={`atlas-node ${kindTone[data.atlas.kind]} ${data.selected ? "is-selected" : ""}`}>
      <Handle type="target" position={Position.Left} className="node-handle" />
      <div className="node-topline">
        <span className="node-icon">
          <Icon size={15} strokeWidth={2.2} />
        </span>
        <span className="node-kind">{nodeKindLabels[data.atlas.kind]}</span>
      </div>
      <div className="node-label">{data.atlas.label}</div>
      <div className="node-summary">{data.atlas.summary}</div>
      <Handle type="source" position={Position.Right} className="node-handle" />
    </div>
  );
}

const nodeTypes = {
  atlas: AtlasNodeCard,
};

function visibleAtlas(view: AtlasView, query: string) {
  const normalizedQuery = query.trim().toLowerCase();
  const baseNodes = atlasNodes.filter((node) => node.viewTags.includes(view));
  const queryNodes = normalizedQuery
    ? baseNodes.filter((node) =>
        [
          node.label,
          node.summary,
          node.whyItMatters,
          node.kind,
          ...node.files,
          ...(node.safeguards ?? []),
        ]
          .join(" ")
          .toLowerCase()
          .includes(normalizedQuery),
      )
    : baseNodes;
  const visibleIds = new Set(queryNodes.map((node) => node.id));
  const baseEdges = atlasEdges.filter(
    (edge) =>
      edge.viewTags.includes(view) &&
      visibleIds.has(edge.source) &&
      visibleIds.has(edge.target),
  );
  return { nodes: queryNodes, edges: baseEdges };
}

function edgeClass(criticality: string) {
  if (criticality === "security") return "edge-security";
  if (criticality === "evidence") return "edge-evidence";
  if (criticality === "ops") return "edge-ops";
  return "edge-normal";
}

async function buildLayout(
  visibleNodes: AtlasNode[],
  graphEdges: typeof atlasEdges,
  selectedId: string,
): Promise<Node<FlowNodeData>[]> {
  const children = visibleNodes.map((node) => ({
    id: node.id,
    width: 244,
    height: 148,
  }));
  const relevantEdges = graphEdges.filter(
    (edge) =>
      visibleNodes.some((node) => node.id === edge.source) &&
      visibleNodes.some((node) => node.id === edge.target),
  );
  const graph = await elk.layout({
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": "RIGHT",
      "elk.spacing.nodeNode": "44",
      "elk.layered.spacing.nodeNodeBetweenLayers": "72",
      "elk.layered.nodePlacement.strategy": "BRANDES_KOEPF",
      "elk.edgeRouting": "SPLINES",
    },
    children,
    edges: relevantEdges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
    })),
  });

  const positions = new Map(
    (graph.children ?? []).map((child) => [child.id, { x: child.x ?? 0, y: child.y ?? 0 }]),
  );
  return visibleNodes.map((node) => ({
    id: node.id,
    type: "atlas",
    position: positions.get(node.id) ?? { x: 0, y: 0 },
    data: { atlas: node, selected: node.id === selectedId },
  }));
}

function toFlowEdges(graphEdges: typeof atlasEdges, visibleIds: Set<string>): Edge[] {
  return graphEdges
    .filter(
      (edge) =>
        visibleIds.has(edge.source) &&
        visibleIds.has(edge.target),
    )
    .map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      className: edgeClass(edge.criticality),
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 16,
        height: 16,
      },
      style: {
        strokeWidth: edge.criticality === "security" ? 2.4 : 1.8,
      },
    }));
}

function App() {
  const initialRoute = useMemo(() => readInitialRoute(), []);
  const [view, setView] = useState<AtlasView>(initialRoute.view);
  const [query, setQuery] = useState(initialRoute.query);
  const [drilldownId, setDrilldownId] = useState<string | null>(initialRoute.drilldownId);
  const [copiedLink, setCopiedLink] = useState(false);
  const journey = journeys.find((item) => item.id === view) ?? journeys[0];
  const activeDrilldown = drilldownId ? drilldowns[drilldownId] : undefined;
  const { nodes: visibleNodes, edges: visibleEdges } = useMemo(() => {
    if (activeDrilldown) {
      const normalizedQuery = query.trim().toLowerCase();
      const nodes = normalizedQuery
        ? activeDrilldown.nodes.filter((node) =>
            [node.label, node.summary, node.whyItMatters, ...node.files]
              .join(" ")
              .toLowerCase()
              .includes(normalizedQuery),
          )
        : activeDrilldown.nodes;
      const ids = new Set(nodes.map((node) => node.id));
      return {
        nodes,
        edges: activeDrilldown.edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target)),
      };
    }
    return visibleAtlas(view, query);
  }, [activeDrilldown, query, view]);
  const defaultSelected = journey.focusNodes.find((id) =>
    visibleNodes.some((node) => node.id === id),
  );
  const [selectedId, setSelectedId] = useState(
    initialRoute.selectedId || defaultSelected || visibleNodes[0]?.id || "",
  );
  const [flowNodes, setFlowNodes, onNodesChange] = useNodesState<Node<FlowNodeData>>([]);
  const [flowEdges, setFlowEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const selectedNode =
    [...atlasNodes, ...(activeDrilldown?.nodes ?? [])].find((node) => node.id === selectedId) ??
    visibleNodes[0] ??
    atlasNodes[0];
  const graphEdges = activeDrilldown ? activeDrilldown.edges : visibleEdges;
  const relatedEdges = graphEdges.filter(
    (edge) => edge.source === selectedNode.id || edge.target === selectedNode.id,
  );
  const visibleIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);
  const selectedDrilldown = drilldowns[selectedNode.id];
  const currentDepth = activeDrilldown ? "Componente" : "Sistema";
  const showReadingModes = view === "overview" && !activeDrilldown;
  const showGateStrip = view === "operations" && !activeDrilldown;
  const evidenceChips = [
    { label: "Nivel", value: currentDepth },
    { label: "Arquivos", value: String(selectedNode.files.length) },
    { label: "Guardrails", value: String(selectedNode.safeguards?.length ?? 0) },
    { label: "Microfluxo", value: selectedDrilldown ? "sim" : "nao" },
  ];

  const relayout = useCallback(async () => {
    const selected = visibleIds.has(selectedId) ? selectedId : defaultSelected ?? visibleNodes[0]?.id ?? "";
    if (selected !== selectedId) {
      setSelectedId(selected);
    }
    const nodes = await buildLayout(visibleNodes, graphEdges, selected);
    setFlowNodes(nodes);
    setFlowEdges(toFlowEdges(graphEdges, visibleIds));
  }, [defaultSelected, graphEdges, selectedId, setFlowEdges, setFlowNodes, visibleIds, visibleNodes]);

  useEffect(() => {
    void relayout();
  }, [relayout]);

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("view", view);
    if (drilldownId) params.set("drill", drilldownId);
    if (selectedNode.id) params.set("node", selectedNode.id);
    if (query.trim()) params.set("q", query.trim());
    window.history.replaceState(null, "", `#${params.toString()}`);
  }, [drilldownId, query, selectedNode.id, view]);

  useEffect(() => {
    setFlowNodes((current) =>
      current.map((node) => ({
        ...node,
        data: { ...node.data, selected: node.id === selectedId },
      })),
    );
  }, [selectedId, setFlowNodes]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node<FlowNodeData>) => {
    setSelectedId(node.id);
  }, []);

  const copyCurrentLink = useCallback(async () => {
    await navigator.clipboard?.writeText(window.location.href);
    setCopiedLink(true);
    window.setTimeout(() => setCopiedLink(false), 1400);
  }, []);

  return (
    <main className="app-shell">
      <aside className="side-rail">
        <div className="brand">
          <div className="brand-mark">
            <Sparkles size={18} strokeWidth={2.4} />
          </div>
          <div>
            <h1>EduAssist Visual Atlas</h1>
            <p>Documentacao visual curada pelo Codex</p>
          </div>
        </div>

        <section className="rail-section">
          <div className="intro-card">
            <h2>Uma pergunta, quatro lentes</h2>
            <p>
              As trilhas nao sao partes separadas. O Runtime entende e executa; Dados
              Protegidos decide acesso; RAG busca evidencia documental; Operacao mede,
              audita e devolve feedback.
            </p>
          </div>

          <div className="lens-legend">
            <div><span className="lens-dot runtime-dot" />Runtime = caminho</div>
            <div><span className="lens-dot protected-dot" />Dados = permissao</div>
            <div><span className="lens-dot rag-dot" />RAG = evidencia</div>
            <div><span className="lens-dot ops-dot" />Operacao = prova</div>
          </div>

          <h2>
            <Layers3 size={14} />
            Trilhas
          </h2>
          <div className="journey-list">
            {journeys.map((item) => (
              <button
                key={item.id}
                className={`journey-button ${item.id === view ? "active" : ""}`}
                onClick={() => {
                  setView(item.id);
                  setDrilldownId(null);
                  setQuery("");
                  setSelectedId(item.focusNodes[0]);
                }}
              >
                <span>{item.label}</span>
                <small>{item.promise}</small>
              </button>
            ))}
          </div>
        </section>

        <section className="rail-section read-order">
          <h2>
            <BookOpen size={14} />
            Leia nesta ordem
          </h2>
          <ol>
            {(activeDrilldown?.readOrder ?? journey.readOrder).map((path) => (
              <li key={path}>{path}</li>
            ))}
          </ol>
        </section>
      </aside>

      <section className="atlas-main">
        <header className="top-bar">
          <div>
            <p className="section-label">Mapa ativo</p>
            <h2>{activeDrilldown?.title ?? viewLabels[view]}</h2>
            <span>{activeDrilldown?.subtitle ?? journey.promise}</span>
            <div className="level-ladder" aria-label="Profundidade do atlas">
              <span className={!activeDrilldown ? "active" : ""}>Sistema</span>
              <span className={activeDrilldown ? "active" : ""}>Componente</span>
              <span>Codigo por arquivo</span>
            </div>
          </div>
          <div className="toolbar">
            {activeDrilldown && (
              <button
                className="tool-button secondary"
                onClick={() => {
                  setDrilldownId(null);
                  setSelectedId(activeDrilldown.parentNodeId);
                }}
              >
                <ChevronLeft size={15} />
                Macro
              </button>
            )}
            <label className="search-box">
              <Search size={15} />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Buscar servico, arquivo, regra..."
              />
            </label>
            <button className="tool-button" onClick={() => void relayout()} title="Reorganizar grafo">
              <RefreshCw size={15} />
              Reorganizar
            </button>
            <button className="tool-button secondary" onClick={() => void copyCurrentLink()} title="Copiar link desta visao">
              <Copy size={15} />
              {copiedLink ? "Copiado" : "Link"}
            </button>
          </div>
        </header>

        <div className="graph-frame">
          {activeDrilldown && (
            <div className="drilldown-banner">
              <span>Nivel micro</span>
              <strong>{activeDrilldown.title}</strong>
              <small>{activeDrilldown.nodes.length} partes perto do codigo</small>
            </div>
          )}
          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            fitViewOptions={{ padding: 0.24 }}
            minZoom={0.35}
            maxZoom={1.4}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#d8e4e7" gap={24} size={1} variant={BackgroundVariant.Dots} />
            <MiniMap
              pannable
              zoomable
              maskColor="rgba(7, 17, 18, 0.62)"
              nodeStrokeColor="#0f1d20"
              style={{ width: 168, height: 108, background: "#0b191b", border: "1px solid #24383b" }}
              nodeColor={(node) => {
                const kind = (node.data as FlowNodeData).atlas.kind;
                if (kind === "policy") return "#d97706";
                if (kind === "data") return "#0f766e";
                if (kind === "runtime") return "#2563eb";
                if (kind === "gate") return "#7c2d12";
                return "#0f766e";
              }}
            />
            <Controls position="bottom-left" />
          </ReactFlow>
        </div>

        {showReadingModes && (
          <section className="context-strip">
            <div className="gate-strip-title">
              <BookOpen size={16} />
              Como ler este atlas
            </div>
            <div className="reading-modes overview-reading-modes">
              {readingModes.map((mode) => (
                <article key={mode.label} className="reading-mode-card">
                  <span>{mode.kind}</span>
                  <strong>{mode.label}</strong>
                  <small>{mode.detail}</small>
                </article>
              ))}
            </div>
          </section>
        )}

        {showGateStrip && (
          <section className="gate-strip">
            <div className="gate-strip-title">
              <ShieldCheck size={16} />
              Gates que sustentam a operacao
            </div>
            <div className="gate-list">
              {gates.map((gate) => (
                <article key={gate.label} className={`gate-card ${gate.status}`}>
                  <div>
                    <span>{gate.label}</span>
                    <code>{gate.command}</code>
                  </div>
                  <p>{gate.protects}</p>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>

      <aside className="inspector">
        <div className="inspector-title">
          <PanelRight size={17} />
          Evidencia do no
        </div>
        <div className="inspector-card">
          <div className={`inspector-kind ${kindTone[selectedNode.kind]}`}>
            {nodeKindLabels[selectedNode.kind]}
          </div>
          <h2>{selectedNode.label}</h2>
          <p className="inspector-summary">{selectedNode.summary}</p>
          <div className="why-box">
            <CheckCircle2 size={16} />
            <span>{selectedNode.whyItMatters}</span>
          </div>
          <div className="evidence-grid">
            {evidenceChips.map((chip) => (
              <div key={chip.label}>
                <span>{chip.label}</span>
                <strong>{chip.value}</strong>
              </div>
            ))}
          </div>
        </div>

        {selectedDrilldown && !activeDrilldown && (
          <button
            className="drill-button"
            onClick={() => {
              setDrilldownId(selectedDrilldown.id);
              setQuery("");
              setSelectedId(selectedDrilldown.nodes[0]?.id ?? selectedNode.id);
            }}
          >
            <Workflow size={15} />
            Abrir microfluxo
            <span>{selectedDrilldown.nodes.length} partes</span>
          </button>
        )}

        <section className="inspector-section">
          <h3>
            <FileCode2 size={14} />
            Arquivos reais
          </h3>
          <div className="file-list">
            {selectedNode.files.map((file) => (
              <a key={file} href={`../../${file}`} title={file}>
                <Code2 size={13} />
                <span>{file}</span>
                <ExternalLink size={12} />
              </a>
            ))}
          </div>
        </section>

        {selectedNode.safeguards && (
          <section className="inspector-section">
            <h3>
              <LockKeyhole size={14} />
              Guardrails
            </h3>
            <ul className="chip-list">
              {selectedNode.safeguards.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
        )}

        <section className="inspector-section">
          <h3>
            <ArrowRight size={14} />
            Relacoes
          </h3>
          <div className="relation-list">
            {relatedEdges.slice(0, 8).map((edge) => {
              const otherId = edge.source === selectedNode.id ? edge.target : edge.source;
              const other = [...atlasNodes, ...(activeDrilldown?.nodes ?? [])].find(
                (node) => node.id === otherId,
              );
              return (
                <button key={edge.id} onClick={() => setSelectedId(otherId)}>
                  <span>{edge.source === selectedNode.id ? "sai para" : "vem de"}</span>
                  <strong>{other?.label ?? otherId}</strong>
                  <small>{edge.label}</small>
                </button>
              );
            })}
          </div>
        </section>
      </aside>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
