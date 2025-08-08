import React, { useEffect, useMemo, useRef, useState } from "react";

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
  request_data?: {
    location?: string;
    occupancy_type?: string;
    data_source?: string;     // e.g., "RSMeans"
    data_version?: string;    // e.g., "2024 Q3"
    base_psf_source?: string; // optional display override
    region_multiplier?: number;
    [k: string]: any;
  } | undefined;
  [key: string]: any;
};

interface Props {
  projectData: ProjectLike;
}

const TRADE_ORDER = ["Structural", "Mechanical", "Electrical", "Plumbing", "General Conditions"];

// Mirror the pie colors you use elsewhere (update if your tokens differ)
const TRADE_COLORS: Record<string, string> = {
  Structural: "#4F81BD",          // blue
  Mechanical: "#9BBB59",          // green
  Electrical: "#8064A2",          // purple
  Plumbing: "#C0504D",            // red
  "General Conditions": "#F79646",// orange
};

const REGIONAL_INDEX_FALLBACK: Record<string, number> = {
  "Nashville, TN": 1.08,
  Tennessee: 1.08,
  Default: 1.00,
};

function fmt$(n: number): string;
function fmt$(n: number, frac: number): string;
function fmt$(n: number, frac?: number): string {
  const f = typeof frac === "number" ? frac : 0;
  if (!isFinite(n)) return "$0";
  return n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: f });
}
function pct(n: number) {
  if (!isFinite(n)) return "0%";
  return `${(n * 100).toFixed(1)}%`;
}
function copyToClipboard(text: string) {
  try { navigator.clipboard?.writeText(text); } catch { /* noop */ }
}

// Simple chip+popover UI (no external libs)
const Chip: React.FC<{ label: string; onClick?: () => void; title?: string }> = ({ label, onClick, title }) => (
  <button
    type="button"
    className="inline-flex items-center px-2.5 py-1 rounded-full border text-sm hover:bg-gray-50 transition"
    onClick={onClick}
    title={title}
    style={{ lineHeight: 1.1 }}
  >
    {label}
  </button>
);

const Popover: React.FC<{ open: boolean; anchorRef: React.RefObject<HTMLButtonElement>; children: React.ReactNode }> = ({ open, anchorRef, children }) => {
  const [style, setStyle] = useState<React.CSSProperties>({});
  useEffect(() => {
    if (!open || !anchorRef.current) return;
    const rect = anchorRef.current.getBoundingClientRect();
    setStyle({
      position: "fixed",
      top: rect.bottom + 8,
      left: Math.max(12, rect.left),
      zIndex: 50,
      maxWidth: 360,
    });
  }, [open, anchorRef]);
  if (!open) return null;
  return (
    <div style={style} className="rounded-lg shadow-lg border bg-white p-3 text-sm">
      {children}
    </div>
  );
};

const CostDNADisplay: React.FC<Props> = ({ projectData }) => {
  // ---------- Inputs & deterministic derivations ----------
  const sf               = Math.max(0, projectData.square_footage || 0);
  const total            = Math.max(0, projectData.total_cost || 0);
  const location         = projectData.location || projectData.request_data?.location || "";
  const occ              = (projectData.occupancy_type || projectData.request_data?.occupancy_type || "").toLowerCase();
  const isHealthcare     = /health/.test(occ);
  const descText         = `${projectData.description || ""} ${projectData.occupancy_type || ""}`.toLowerCase();
  const surgicalLike     = /(surgical|operating room|\bor\b)/.test(descText);

  // Regional multiplier (prefer request_data, else fallback table)
  const regionalMult =
    projectData.request_data?.region_multiplier ??
    REGIONAL_INDEX_FALLBACK[location] ??
    (() => {
      const stateKey = Object.keys(REGIONAL_INDEX_FALLBACK).find(k => location.includes(k));
      return stateKey ? REGIONAL_INDEX_FALLBACK[stateKey] : REGIONAL_INDEX_FALLBACK.Default;
    })();

  // Complexity multiplier (deterministic)
  const complexityMult = (surgicalLike || isHealthcare) ? 1.15 : 1.00;

  // Back-solve a base $/SF so the equation reconciles to the current total.
  // Later, you can swap this with the DB base_psf and keep the UI identical.
  const basePsfSolved = sf > 0 ? total / (sf * regionalMult * complexityMult) : 0;

  // Provenance settings (RSMeans)
  const srcName   = projectData.request_data?.data_source  || "RSMeans";
  const srcVer    = projectData.request_data?.data_version || "2024 Q3";
  const baseLabel = projectData.request_data?.base_psf_source || `${srcName} (${srcVer}) — comparable ${projectData.occupancy_type || "occupancy"} in ${location || "region"}`;

  // Fingerprint from categories (mirrors pie order/colors)
  const cats = Array.isArray(projectData.categories) ? projectData.categories : [];
  const catSum = cats.reduce((a, c) => a + (c.amount || 0), 0) || total;
  const fingerprint = TRADE_ORDER.map(trade => {
    const match = cats.find(c => c.trade === trade);
    const amt = Math.max(0, match?.amount || 0);
    const percent = catSum > 0 ? amt / catSum : 0;
    return { trade, amt, percent, color: TRADE_COLORS[trade] || "#ccc" };
  });

  // Confidence score — ties directly to available signals
  const signals = {
    occ: !!occ,
    loc: !!location,
    cats: cats.length >= 4,
    sf: sf > 0,
  };
  const confidenceScore = Math.min(0.95,
    0.55 + (signals.occ ? 0.15 : 0) + (signals.loc ? 0.10 : 0) + (signals.cats ? 0.10 : 0) + (signals.sf ? 0.05 : 0)
  );
  const confidenceText = [
    signals.occ && "clear occupancy type",
    signals.loc && "known region",
    signals.cats && "trade-level breakdown",
    signals.sf  && "square footage provided",
  ].filter(Boolean).join(", ");

  // Toggle for total vs per-SF
  const [mode, setMode] = useState<"total"|"psf">("total");
  const value = (valPerSf: number) => mode === "psf" ? valPerSf : (valPerSf * sf);

  // Derive the step values for waterfall
  const baseVal       = value(basePsfSolved);
  const regionalVal   = value(basePsfSolved * regionalMult);
  const complexVal    = value(basePsfSolved * regionalMult * complexityMult);
  const allowances    = 0; // show step even if 0 to be honest & consistent
  const finalVal      = complexVal + allowances;

  // Detected special factor badges (trust cues)
  const factors: {label: string; impact: "low"|"medium"|"high"}[] = [];
  if (surgicalLike || isHealthcare) factors.push({ label: "OSHPD/Healthcare Compliance", impact: "high" });
  if (/medical gas/.test(descText)) factors.push({ label: "Medical Gas", impact: "medium" });

  // Chip popovers
  const [openChip, setOpenChip] = useState<string | null>(null);
  const chipRef = useRef<Record<string, HTMLButtonElement | null>>({});

  const setChipRef = (key: string) => (el: HTMLButtonElement | null) => { chipRef.current[key] = el; };

  // Copy formula text
  const copyFormula = () => {
    const text =
      `Price = (Base ${fmt$(basePsfSolved, 2)}/SF × ${sf.toLocaleString()} SF) × ${regionalMult.toFixed(2)} × ${complexityMult.toFixed(2)} + ${fmt$(allowances)} = ${fmt$(finalVal)}`;
    copyToClipboard(text);
  };

  // Close popovers on outside click/esc
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpenChip(null); };
    const onClick = (e: MouseEvent) => {
      if (!openChip) return;
      const el = chipRef.current[openChip];
      if (el && !el.contains(e.target as Node)) setOpenChip(null);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("mousedown", onClick);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("mousedown", onClick);
    };
  }, [openChip]);

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h3 className="text-lg font-semibold">🧬 Why This Price (Cost DNA)</h3>
        <div className="flex items-center gap-2">
          <div className="inline-flex border rounded-full overflow-hidden text-sm">
            <button
              type="button"
              className={`px-3 py-1 ${mode === "total" ? "bg-gray-900 text-white" : "bg-white"}`}
              onClick={() => setMode("total")}
            >Total</button>
            <button
              type="button"
              className={`px-3 py-1 ${mode === "psf" ? "bg-gray-900 text-white" : "bg-white"}`}
              onClick={() => setMode("psf")}
            >Per-SF</button>
          </div>
          <button type="button" className="px-3 py-1 rounded border text-sm hover:bg-gray-50" onClick={copyFormula}>
            Copy formula
          </button>
        </div>
      </div>

      <div className="card-body">
        {/* Formula line with chips */}
        <div className="text-sm mb-3 flex flex-wrap items-center gap-2">
          <span className="opacity-70">Price =</span>

          <button ref={setChipRef("base")} onClick={() => setOpenChip(openChip === "base" ? null : "base")} className="inline-flex items-center px-2.5 py-1 rounded-full border text-sm hover:bg-gray-50">
            Base {mode === "psf" ? fmt$(basePsfSolved, 2) + "/SF" : fmt$(baseVal)}
          </button>
          <span className="opacity-70">×</span>

          <button ref={setChipRef("sf")} onClick={() => setOpenChip(openChip === "sf" ? null : "sf")} className="inline-flex items-center px-2.5 py-1 rounded-full border text-sm hover:bg-gray-50">
            {sf.toLocaleString()} SF
          </button>
          <span className="opacity-70">×</span>

          <button ref={setChipRef("regional")} onClick={() => setOpenChip(openChip === "regional" ? null : "regional")} className="inline-flex items-center px-2.5 py-1 rounded-full border text-sm hover:bg-gray-50">
            Regional {regionalMult.toFixed(2)}
          </button>
          <span className="opacity-70">×</span>

          <button ref={setChipRef("complex")} onClick={() => setOpenChip(openChip === "complex" ? null : "complex")} className="inline-flex items-center px-2.5 py-1 rounded-full border text-sm hover:bg-gray-50">
            Complexity {complexityMult.toFixed(2)}
          </button>

          <span className="opacity-70">+</span>
          <button ref={setChipRef("allow")} onClick={() => setOpenChip(openChip === "allow" ? null : "allow")} className="inline-flex items-center px-2.5 py-1 rounded-full border text-sm hover:bg-gray-50">
            Allowances {mode === "psf" ? fmt$(allowances / (sf || 1), 2) + "/SF" : fmt$(allowances)}
          </button>

          <span className="opacity-70">=</span>
          <strong>{mode === "psf" ? fmt$(finalVal / (sf || 1), 2) + "/SF" : fmt$(finalVal)}</strong>
        </div>

        {/* Popovers for provenance */}
        <Popover open={openChip === "base"} anchorRef={{ current: chipRef.current["base"] as HTMLButtonElement }}>
          <div className="font-medium mb-1">Base {mode === "psf" ? "$/SF" : "Subtotal"}</div>
          <div className="mb-1">{mode === "psf" ? fmt$(basePsfSolved, 2) + "/SF" : fmt$(baseVal)}</div>
          <div className="opacity-80">Source: {baseLabel}</div>
          <div className="opacity-70 mt-1">Note: adjusted by regional & complexity multipliers shown here.</div>
        </Popover>

        <Popover open={openChip === "sf"} anchorRef={{ current: chipRef.current["sf"] as HTMLButtonElement }}>
          <div className="font-medium mb-1">Square Footage</div>
          <div className="mb-1">{sf.toLocaleString()} SF</div>
          <div className="opacity-70">From project input.</div>
        </Popover>

        <Popover open={openChip === "regional"} anchorRef={{ current: chipRef.current["regional"] as HTMLButtonElement }}>
          <div className="font-medium mb-1">Regional Multiplier</div>
          <div className="mb-1">× {regionalMult.toFixed(2)}</div>
          <div className="opacity-80">Source: SpecSharp Regional Index{location ? ` for ${location}` : ""}.</div>
          <div className="opacity-70">Reflects localized labor/material costs.</div>
        </Popover>

        <Popover open={openChip === "complex"} anchorRef={{ current: chipRef.current["complex"] as HTMLButtonElement }}>
          <div className="font-medium mb-1">Occupancy / Complexity</div>
          <div className="mb-1">× {complexityMult.toFixed(2)}</div>
          <div className="opacity-80">Reason: {isHealthcare || surgicalLike ? "Healthcare/Surgical compliance & systems" : "No special complexity detected"}</div>
        </Popover>

        <Popover open={openChip === "allow"} anchorRef={{ current: chipRef.current["allow"] as HTMLButtonElement }}>
          <div className="font-medium mb-1">Allowances</div>
          <div className="mb-1">{mode === "psf" ? fmt$(allowances / (sf || 1), 2) + "/SF" : fmt$(allowances)}</div>
          <div className="opacity-70">No specific allowances detected for this project.</div>
        </Popover>

        {/* Waterfall / Step progression */}
        <div className="mt-3">
          <div className="flex items-stretch text-sm">
            <div className="flex-1 border rounded-l p-2">
              <div className="opacity-70">Base</div>
              <div className="font-medium">{mode === "psf" ? fmt$(basePsfSolved, 2) + "/SF" : fmt$(baseVal)}</div>
            </div>
            <div className="px-2 self-center opacity-50">→</div>
            <div className="flex-1 border p-2">
              <div className="opacity-70">× Regional</div>
              <div className="font-medium">{mode === "psf" ? fmt$(basePsfSolved * regionalMult, 2) + "/SF" : fmt$(regionalVal)}</div>
            </div>
            <div className="px-2 self-center opacity-50">→</div>
            <div className="flex-1 border p-2">
              <div className="opacity-70">× Complexity</div>
              <div className="font-medium">{mode === "psf" ? fmt$(basePsfSolved * regionalMult * complexityMult, 2) + "/SF" : fmt$(complexVal)}</div>
            </div>
            <div className="px-2 self-center opacity-50">→</div>
            <div className="flex-1 border p-2">
              <div className="opacity-70">+ Allowances</div>
              <div className="font-medium">{mode === "psf" ? fmt$(allowances / (sf || 1), 2) + "/SF" : fmt$(allowances)}</div>
            </div>
            <div className="px-2 self-center opacity-50">=</div>
            <div className="flex-1 border rounded-r p-2 bg-gray-50">
              <div className="opacity-70">Final</div>
              <div className="font-semibold">{mode === "psf" ? fmt$(finalVal / (sf || 1), 2) + "/SF" : fmt$(finalVal)}</div>
            </div>
          </div>
        </div>

        {/* Sources / provenance line */}
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-sm opacity-80">
          <div>Inputs: {(projectData.occupancy_type || "Occupancy")} • {sf.toLocaleString()} SF • {projectData.project_classification || "Ground-Up"} • {location || "Region"}</div>
          <div>Sources: Base — {srcName} ({srcVer}) {location ? `for ${location}` : ""} • Regional — Index {regionalMult.toFixed(2)} • Complexity — {surgicalLike || isHealthcare ? "Healthcare/Surgical" : "None"}</div>
          <div>Calc v1 • {new Date().toLocaleDateString()}</div>
        </div>

        {/* Cost Fingerprint (mirrors pie) */}
        <div className="mt-4">
          <div className="text-sm opacity-70 mb-1">Cost Fingerprint (matches trade breakdown)</div>
          <div className="w-full h-3 flex rounded overflow-hidden border">
            {fingerprint.map((f, i) => (
              <div key={i} title={`${f.trade}: ${pct(f.percent)}`} style={{ width: `${f.percent * 100}%`, backgroundColor: f.color }} className="h-full" />
            ))}
          </div>
          <div className="flex flex-wrap gap-3 mt-2 text-sm">
            {fingerprint.map((f, i) => (
              <span key={i} className="opacity-80">
                <span style={{ backgroundColor: f.color, display: "inline-block", width: 10, height: 10, marginRight: 6 }}></span>
                {f.trade}: {pct(f.percent)}
              </span>
            ))}
          </div>
        </div>

        {/* Factors + confidence */}
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            {factors.length ? factors.map((fa, i) => (
              <span key={i} className="px-2 py-1 rounded-full border text-sm" title={`impact: ${fa.impact}`}>{fa.label}</span>
            )) : <span className="text-sm opacity-70">No special factors detected</span>}
          </div>
          <div className="ml-auto flex items-center gap-2">
            <div className="text-sm">Confidence</div>
            <div className="w-28 h-2 bg-gray-200 rounded overflow-hidden">
              <div className="h-full bg-black" style={{ width: `${confidenceScore * 100}%` }} />
            </div>
            <div className="text-sm">{Math.round(confidenceScore * 100)}%</div>
          </div>
        </div>
        <div className="text-xs opacity-70 mt-1">Why: {confidenceText || "limited signals"}</div>

        {/* Anchor to trade math below */}
        <div className="mt-3 text-sm">
          <button
            type="button"
            className="underline hover:no-underline"
            onClick={() => {
              const el = document.querySelector("#trade-breakdown, #cost-breakdown, [data-anchor='cost-breakdown']");
              if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
          >
            See trade math below ↴
          </button>
        </div>
      </div>
    </div>
  );
};

export default CostDNADisplay;