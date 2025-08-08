import React, { useEffect, useMemo, useState } from "react";

type Category = { trade: string; amount: number };
type ProjectLike = {
  project_name?: string;
  description?: string;
  project_type?: string;
  project_classification?: string;
  square_footage?: number;
  location?: string;
  occupancy_type?: string;
  total_cost?: number;
  categories?: Category[];
  request_data?: any;
  [key: string]: any;
};

type DNA = {
  fingerprint: { component: string; percent: number; color: string }[];
  special_factors: { name: string; detected: boolean; impact: "low"|"medium"|"high" }[];
  multipliers: { label: string; value: number; reason: string }[];
  confidence: { score: number; explanation: string };
  why_this_price: {
    base_cost: number;
    assumptions: Record<string, any>;
    applied_multipliers: { label: string; value: number; reason: string }[];
    notes?: string;
  };
};

interface Props {
  projectData: ProjectLike;
  tryApi?: boolean;
  apiBase?: string;
}

const TRADE_COLORS: Record<string, string> = {
  Structural: "#4F81BD",
  Mechanical: "#9BBB59",
  Electrical: "#8064A2",
  Plumbing: "#C0504D",
  "General Conditions": "#F79646",
};

const REGIONAL_INDEX: Record<string, number> = {
  "Nashville, TN": 1.08,
  Tennessee: 1.08,
  Default: 1.00,
};

const deriveLocalDNA = (p: ProjectLike): DNA => {
  const total = p.total_cost ?? 0;
  const cats = Array.isArray(p.categories) ? p.categories : [];
  const sum = cats.reduce((acc, c) => acc + (c.amount || 0), 0) || total;

  const orderedTrades = ["Structural", "Mechanical", "Electrical", "Plumbing", "General Conditions"];
  const fingerprint = orderedTrades.map(trade => {
    const cat = cats.find(c => c.trade === trade);
    const percent = sum > 0 ? (cat?.amount || 0) / sum : 0;
    return { component: trade, percent, color: TRADE_COLORS[trade] || "#ccc" };
  });

  const text = `${p.description || ""} ${p.occupancy_type || ""}`.toLowerCase();
  const special_factors = [
    text.includes("surgical") || text.includes("operating room") || text.includes("healthcare")
      ? { name: "OSHPD/Healthcare Compliance", detected: true, impact: "high" as const }
      : null,
    text.includes("medical gas")
      ? { name: "Medical Gas", detected: true, impact: "medium" as const }
      : null,
  ].filter(Boolean) as DNA["special_factors"];

  let regionMult = REGIONAL_INDEX.Default;
  const loc = p.location || p.request_data?.location || "";
  if (REGIONAL_INDEX[loc]) {
    regionMult = REGIONAL_INDEX[loc];
  } else {
    const stateKey = Object.keys(REGIONAL_INDEX).find(k => loc.includes(k));
    if (stateKey) regionMult = REGIONAL_INDEX[stateKey];
  }

  const multipliers: DNA["multipliers"] = [];
  if (regionMult !== 1.00) multipliers.push({ label: `Region (${loc || "Unknown"})`, value: regionMult, reason: "Regional cost index" });
  if ((p.occupancy_type || "").toLowerCase().includes("health"))
    multipliers.push({ label: "Healthcare Complexity", value: 1.15, reason: "Code & compliance burden" });
  if (!multipliers.length)
    multipliers.push({ label: "Baseline", value: 1.00, reason: "No special multipliers detected" });

  const hasOcc = !!p.occupancy_type;
  const hasLoc = !!loc;
  const hasCats = cats.length > 0;
  const hasSf = !!p.square_footage;
  const score = Math.min(0.95, 0.55 + (hasOcc ? 0.15 : 0) + (hasLoc ? 0.10 : 0) + (hasCats ? 0.10 : 0) + (hasSf ? 0.05 : 0));
  const explanation = [
    hasOcc ? "clear occupancy type" : null,
    hasLoc ? "known region" : null,
    hasCats ? "trade-level breakdown" : null,
    hasSf ? "square footage" : null,
  ].filter(Boolean).join(", ") || "limited signals";

  return {
    fingerprint,
    special_factors,
    multipliers,
    confidence: { score, explanation: `Confidence based on ${explanation}.` },
    why_this_price: {
      base_cost: total,
      assumptions: {
        square_footage: p.square_footage || 0,
        occupancy_type: p.occupancy_type || "",
        classification: p.project_classification || "ground_up",
        location: loc,
      },
      applied_multipliers: multipliers,
      notes: "Derived locally from project data; server analysis will override when available.",
    },
  };
};

const CostDNADisplay: React.FC<Props> = ({ projectData, tryApi = false, apiBase }) => {
  const [dna, setDna] = useState<DNA | null>(null);
  const [error, setError] = useState<string | null>(null);
  const localDNA = useMemo(() => deriveLocalDNA(projectData), [projectData]);

  useEffect(() => {
    let cancelled = false;
    setDna(localDNA);
    if (!tryApi) return;

    const base = apiBase || (import.meta as any).env?.VITE_API_BASE_URL || (window as any).__API_BASE_URL__ || "";
    const run = async () => {
      try {
        const resp = await fetch(`${base}/api/v1/cost-dna/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(projectData),
        });
        if (!resp.ok) {
          const text = await resp.text();
          throw new Error(`API ${resp.status}: ${text || "(no body)"}`);
        }
        const json = await resp.json();
        if (!cancelled && json) setDna(json);
      } catch (e: any) {
        if (!cancelled) setError(e?.message || "Cost DNA API unavailable; showing local analysis.");
      }
    };
    run();
    return () => { cancelled = true; };
  }, [projectData, tryApi, apiBase, localDNA]);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-semibold">🧬 Cost DNA Analysis</h3>
        {error && <div className="text-sm text-red-600 mt-1">API fallback: {error}</div>}
      </div>
      <div className="card-body">

        {/* Fingerprint bar */}
        <div className="mb-4">
          <div className="text-sm opacity-70 mb-1">Cost Fingerprint</div>
          <div className="w-full h-3 flex rounded overflow-hidden border">
            {dna?.fingerprint.map((f, i) => (
              <div key={i} title={`${f.component}: ${(f.percent*100).toFixed(1)}%`} style={{ width: `${f.percent*100}%`, backgroundColor: f.color }} className="h-full" />
            ))}
          </div>
          <div className="flex flex-wrap gap-3 mt-2 text-sm">
            {dna?.fingerprint.map((f, i) => (
              <span key={i} className="opacity-80">
                <span style={{ backgroundColor: f.color, display: "inline-block", width: "10px", height: "10px", marginRight: "4px" }}></span>
                {f.component}: {(f.percent*100).toFixed(1)}%
              </span>
            ))}
          </div>
        </div>

        {/* Special factors */}
        <div className="mb-4">
          <div className="font-medium mb-1">Detected Special Factors</div>
          {dna?.special_factors?.length ? (
            <ul className="list-disc pl-5">
              {dna.special_factors.map((s, i) => (
                <li key={i}>{s.name} — <span className="opacity-70">impact: {s.impact}</span></li>
              ))}
            </ul>
          ) : (
            <div className="opacity-70 text-sm">None detected</div>
          )}
        </div>

        {/* Multipliers */}
        <div className="mb-4">
          <div className="font-medium mb-1">Transparent Multipliers</div>
          <ul className="list-disc pl-5">
            {dna?.multipliers.map((m, i) => (
              <li key={i}>{m.label}: ×{m.value.toFixed(2)} — <span className="opacity-70">{m.reason}</span></li>
            ))}
          </ul>
        </div>

        {/* Confidence */}
        <div className="mb-4">
          <div className="font-medium mb-1">Confidence: {(dna?.confidence.score! * 100).toFixed(0)}%</div>
          <div className="opacity-70 text-sm">{dna?.confidence.explanation}</div>
        </div>

        {/* Why this price */}
        <details className="mt-2">
          <summary className="cursor-pointer select-none">Why this price?</summary>
          <div className="mt-2 text-sm">
            <div>Base Cost: ${dna?.why_this_price.base_cost.toLocaleString()}</div>
            <div className="mt-1 opacity-70">Assumptions:</div>
            <pre className="bg-gray-50 p-2 rounded overflow-x-auto">{JSON.stringify(dna?.why_this_price.assumptions, null, 2)}</pre>
            <div className="mt-1 opacity-70">Applied Multipliers:</div>
            <pre className="bg-gray-50 p-2 rounded overflow-x-auto">{JSON.stringify(dna?.why_this_price.applied_multipliers, null, 2)}</pre>
            {dna?.why_this_price.notes && <div className="mt-1 opacity-70">{dna.why_this_price.notes}</div>}
          </div>
        </details>
      </div>
    </div>
  );
};

export default CostDNADisplay;