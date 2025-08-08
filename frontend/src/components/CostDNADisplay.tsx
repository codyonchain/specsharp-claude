import React, { useEffect, useMemo, useRef, useState } from "react";

/** ---------- Types ---------- **/
type CategoryAny = { trade?: string; name?: string; label?: string; amount?: number; value?: number; total?: number };
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
  categories?: CategoryAny[];
  request_data?: {
    location?: string;
    occupancy_type?: string;
    region_multiplier?: number;
    data_source?: string;     // e.g. "RSMeans"
    data_version?: string;    // e.g. "2024 Q3"
    base_psf_source?: string; // optional display override
    [k: string]: any;
  } | undefined;
  [k: string]: any;
};

interface Props {
  projectData: ProjectLike;
}

/** ---------- Constants ---------- **/
const TRADE_ORDER = ["Structural", "Mechanical", "Electrical", "Plumbing", "General Conditions"]; // must mirror pie order

// Mirror your pie colors exactly (update hex if your design tokens differ)
const TRADE_COLORS: Record<string, string> = {
  Structural: "#4F81BD",           // blue
  Mechanical: "#9BBB59",           // green
  Electrical: "#8064A2",           // purple
  Plumbing: "#C0504D",             // red
  "General Conditions": "#F79646", // orange
};

const REGIONAL_INDEX_FALLBACK: Record<string, number> = {
  "Nashville, TN": 1.08,
  Tennessee: 1.08,
  Default: 1.00,
};

/** ---------- Utils ---------- **/
const norm = (s: string) => String(s || "").toLowerCase().replace(/[^a-z]/g, "");
const fmtMoney = (n: number, frac: number = 0) =>
  isFinite(n) ? n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: frac }) : "$0";
const pct = (n: number) => (isFinite(n) ? `${(n * 100).toFixed(1)}%` : "0%");
const todayStr = () => new Date().toLocaleDateString();

/** ---------- Component ---------- **/
const CostDNADisplay: React.FC<Props> = ({ projectData }) => {
  /** Inputs */
  const sf               = Math.max(0, projectData.square_footage || 0);
  const total            = Math.max(0, projectData.total_cost || 0);
  const location         = projectData.location || projectData.request_data?.location || "";
  const occRaw           = projectData.occupancy_type || projectData.request_data?.occupancy_type || "";
  const occ              = occRaw.toLowerCase();
  const isHealthcare     = /health/.test(occ);
  const descText         = `${projectData.description || ""} ${occRaw}`.toLowerCase();

  /** Provenance defaults */
  const srcName   = projectData.request_data?.data_source  || "RSMeans";
  const srcVer    = projectData.request_data?.data_version || "2024 Q3";
  const baseLabel = projectData.request_data?.base_psf_source || `${srcName} (${srcVer}) — comparable ${occRaw || "occupancy"} in ${location || "region"}`;

  /** Regional + complexity */
  const regionalMult =
    projectData.request_data?.region_multiplier ??
    REGIONAL_INDEX_FALLBACK[location] ??
    (() => {
      const stateKey = Object.keys(REGIONAL_INDEX_FALLBACK).find(k => location.includes(k));
      return stateKey ? REGIONAL_INDEX_FALLBACK[stateKey] : REGIONAL_INDEX_FALLBACK.Default;
    })();

  const complexityMult = (isHealthcare || /(surgical|operating room|\bor\b)/.test(descText)) ? 1.15 : 1.00;

  /** Categories normalization (fix 0% bug) */
  const normalizedCats: Category[] = useMemo(() => {
    const raw = (projectData.categories ??
                (projectData as any).category_breakdown ??
                []) as CategoryAny[];

    const mapped = raw
      .map(c => ({
        trade: String(c.trade ?? c.name ?? c.label ?? "").trim(),
        amount: Number(c.amount ?? c.value ?? c.total ?? 0),
      }))
      .filter(c => c.trade && isFinite(c.amount) && c.amount > 0);

    // index by normalized name
    const byNorm = Object.fromEntries(mapped.map(c => [norm(c.trade), c]));

    // build in canonical pie order to mirror labels/colors
    const ordered: Category[] = TRADE_ORDER.map(t => {
      const m = byNorm[norm(t)];
      return { trade: t, amount: Math.max(0, m?.amount ?? 0) };
    });

    return ordered;
  }, [
    projectData.total_cost,
    projectData.square_footage,
    projectData.occupancy_type,
    projectData.location,
    JSON.stringify(projectData.categories ?? (projectData as any).category_breakdown ?? [])
  ]);

  const catSum = normalizedCats.reduce((a, c) => a + c.amount, 0);

  /** Confidence */
  const confidenceScore = Math.min(
    0.95,
    0.55
      + (occ ? 0.15 : 0)
      + (location ? 0.10 : 0)
      + (normalizedCats.filter(c => c.amount > 0).length >= 4 ? 0.10 : 0)
      + (sf > 0 ? 0.05 : 0)
  );
  const confidenceText = [
    occ && "clear occupancy type",
    location && "known region",
    normalizedCats.filter(c => c.amount > 0).length >= 4 && "trade-level breakdown",
    sf > 0 && "square footage provided",
  ].filter(Boolean).join(", ") || "limited signals";

  /** Toggle */
  const [mode, setMode] = useState<"total"|"psf">("total");
  const asVal = (perSf: number) => (mode === "psf" ? perSf : perSf * sf);

  /** Back-solved base_psf so flow reconciles to current total */
  const basePsfSolved = sf > 0 ? total / (sf * regionalMult * complexityMult) : 0;
  const baseVal       = asVal(basePsfSolved);
  const regionalVal   = asVal(basePsfSolved * regionalMult);
  const complexVal    = asVal(basePsfSolved * regionalMult * complexityMult);
  const allowances    = 0;  // visible step; wire real data later
  const finalVal      = complexVal + allowances;

  /** Factors */
  const factors: {label: string; impact: "low"|"medium"|"high"}[] = [];
  if (isHealthcare || /(surgical|operating room|\bor\b)/.test(descText)) factors.push({ label: "OSHPD/Healthcare Compliance", impact: "high" });
  if (/medical gas/.test(descText)) factors.push({ label: "Medical Gas", impact: "medium" });

  /** UI helpers */
  const chipCls = "inline-flex items-center px-2.5 py-1 rounded-full border text-sm bg-white";
  const blockCls = "flex-1 border rounded-lg p-3 bg-white";
  const labelDim = "text-xs uppercase tracking-wide opacity-70";
  const bigNum = "text-lg font-semibold";
  const pill = (active:boolean) => `px-3 py-1 ${active ? "bg-gray-900 text-white" : "bg-white"} rounded-full border`;

  /** Render */
  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h3 className="text-lg font-semibold">🧬 Why This Price (Cost DNA)</h3>
        <div className="flex items-center gap-2">
          <div className="inline-flex gap-1">
            <button className={pill(mode==='total')} onClick={() => setMode('total')}>Total</button>
            <button className={pill(mode==='psf')} onClick={() => setMode('psf')}>Per-SF</button>
          </div>
        </div>
      </div>

      <div className="card-body">
        {/* AHA #1: Fingerprint ties to pie (mirrors order/colors) */}
        <div className="mb-3">
          <div className="text-sm opacity-70 mb-1">Cost Fingerprint (matches trade breakdown)</div>
          <div className="w-full h-3 flex rounded overflow-hidden border">
            {normalizedCats.map((c, i) => {
              const percent = catSum > 0 ? c.amount / catSum : 0;
              return (
                <div
                  key={i}
                  title={`${c.trade}: ${pct(percent)}`}
                  style={{ width: `${percent * 100}%`, backgroundColor: TRADE_COLORS[c.trade] || "#ccc" }}
                  className="h-full"
                  onClick={() => {
                    const el = document.querySelector(`#trade-${norm(c.trade)}`) || document.querySelector("#cost-breakdown, #trade-breakdown");
                    el?.scrollIntoView({ behavior: "smooth", block: "start" });
                  }}
                />
              );
            })}
          </div>
          <div className="flex flex-wrap gap-4 mt-2 text-sm">
            {normalizedCats.map((c, i) => {
              const percent = catSum > 0 ? c.amount / catSum : 0;
              return (
                <span key={i} className="opacity-80 cursor-pointer" onClick={() => {
                  const el = document.querySelector(`#trade-${norm(c.trade)}`) || document.querySelector("#cost-breakdown, #trade-breakdown");
                  el?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}>
                  <span style={{ backgroundColor: TRADE_COLORS[c.trade] || "#ccc", display: "inline-block", width: 10, height: 10, marginRight: 6 }}></span>
                  {c.trade}: {pct(percent)}
                </span>
              );
            })}
          </div>
        </div>

        {/* AHA #2: One-flow visual calculation with provenance */}
        <div className="grid md:grid-cols-5 gap-2 items-stretch">
          <div className={`${blockCls}`}>
            <div className={labelDim}>Base {mode==='psf' ? "$/SF" : "Subtotal"}</div>
            <div className={bigNum}>{mode==='psf' ? `${fmtMoney(basePsfSolved, 2)}/SF` : fmtMoney(baseVal)}</div>
            <div className="text-xs mt-1 opacity-80">
              Source: {baseLabel}
            </div>
          </div>

          <div className="self-center text-center opacity-40">×</div>

          <div className={`${blockCls}`}>
            <div className={labelDim}>Regional Index</div>
            <div className={bigNum}>× {regionalMult.toFixed(2)}</div>
            <div className="text-xs mt-1 opacity-80">
              Source: SpecSharp Regional Index{location ? ` • ${location}` : ""}
            </div>
          </div>

          <div className="self-center text-center opacity-40">×</div>

          <div className={`${blockCls}`}>
            <div className={labelDim}>Complexity</div>
            <div className={bigNum}>× {complexityMult.toFixed(2)}</div>
            <div className="text-xs mt-1 opacity-80">
              {isHealthcare ? "Healthcare" : "Standard"} {/(surgical|operating room|\bor\b)/.test(descText) ? "• Surgical/OR" : ""}
            </div>
          </div>

          <div className="self-center text-center opacity-40 hidden md:block">=</div>

          <div className={`${blockCls} md:col-span-5 bg-gray-50`}>
            <div className="flex items-center justify-between">
              <div>
                <div className={labelDim}>Final {mode==='psf' ? "$/SF" : "Total"}</div>
                <div className="text-2xl font-bold">{mode==='psf' ? `${fmtMoney((basePsfSolved*regionalMult*complexityMult), 2)}/SF` : fmtMoney(finalVal)}</div>
                <div className="text-xs mt-1 opacity-80">Calculated for {sf.toLocaleString()} SF</div>
              </div>
              <div className="text-right">
                <div className="inline-flex items-center gap-2">
                  <span className="text-xs uppercase tracking-wide opacity-70">Confidence</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${confidenceScore>=0.85?"bg-green-100 text-green-700":confidenceScore>=0.7?"bg-yellow-100 text-yellow-700":"bg-red-100 text-red-700"}`}>
                    {Math.round(confidenceScore*100)}% • {confidenceScore>=0.85?"High":confidenceScore>=0.7?"Medium":"Low"}
                  </span>
                </div>
                <div className="text-xs opacity-70 mt-1 max-w-xs">{confidenceText || "limited signals"}</div>
              </div>
            </div>
          </div>
        </div>

        {/* AHA #3: Source strip */}
        <div className="mt-3 px-3 py-2 rounded-lg bg-gray-50 text-sm flex flex-wrap gap-4 items-center">
          <div><span className="opacity-70">Base:</span> {srcName} ({srcVer}){location?` • ${location}`:""}</div>
          <div><span className="opacity-70">Regional:</span> Index {regionalMult.toFixed(2)}</div>
          <div><span className="opacity-70">Complexity:</span> {isHealthcare ? "Healthcare" : "Standard"}{/(surgical|operating room|\bor\b)/.test(descText) ? " • Surgical/OR" : ""}</div>
          <div className="opacity-70 ml-auto">Pulled: {todayStr()}</div>
        </div>

        {/* Factors */}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {factors.length ? factors.map((fa, i) => (
            <span key={i} className="px-2 py-1 rounded-full border text-sm" title={`impact: ${fa.impact}`}>{fa.label}</span>
          )) : <span className="text-sm opacity-70">No special factors detected</span>}
        </div>

        {/* Jump link to trade math */}
        <div className="mt-3 text-sm">
          <button
            type="button"
            className="underline hover:no-underline"
            onClick={() => {
              const el = document.querySelector("#trade-breakdown, #cost-breakdown, [data-anchor='cost-breakdown']");
              el?.scrollIntoView({ behavior: "smooth", block: "start" });
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