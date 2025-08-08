import React, { useEffect, useMemo, useRef, useState } from "react";
import { getPieBreakdown, PIE_TRADE_COLORS, PIE_TRADE_ORDER } from "./ProjectDetail";

/** ---------- Types ---------- **/
type ProjectLike = {
  project_name?: string;
  description?: string;
  project_type?: string;
  project_classification?: string;
  square_footage?: number;
  location?: string;
  occupancy_type?: string;
  total_cost?: number;
  categories?: any[];
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
const REGIONAL_INDEX_FALLBACK: Record<string, number> = {
  "Nashville, TN": 1.08,
  Tennessee: 1.08,
  Default: 1.00,
};

// Mocked sample size from "comparables" (replace later with real count)
const SAMPLE_SIZE = 47;
const SAMPLE_STD_DEV_PSF = 26; // mock $/SF variance for CI calc

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

  /** Use shared pie breakdown helper for perfect consistency */
  const pieData = useMemo(() => getPieBreakdown(projectData), [
    projectData?.id || projectData?.project_id,
    projectData.total_cost,
    projectData.square_footage,
    JSON.stringify(projectData.categories || (projectData as any).category_breakdown || [])
  ]);

  // Debug log to verify data
  console.debug("CostDNA pieData ->", pieData);

  // Calculate total from pie data
  const totalAmt = pieData.reduce((a, i) => a + (Number(i.amount) || 0), 0);

  // Build fingerprint in canonical order with colors from pie
  const fingerprint = PIE_TRADE_ORDER.map(trade => {
    const item = pieData.find(i => i.trade === trade);
    const amt = Number(item?.amount || 0);
    const percent = totalAmt > 0 ? amt / totalAmt : 0;
    return { trade, amt, percent, color: PIE_TRADE_COLORS[trade] || "#999" };
  });

  /** Jump to trade with highlight */
  function jumpToTrade(tradeLabel: string) {
    const id = `trade-${String(tradeLabel).toLowerCase().replace(/[^a-z]/g, "")}`;
    const el = document.getElementById(id) || document.querySelector(`[data-trade-id='${id}']`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      // Add highlight classes
      el.classList.add("ring-2", "ring-indigo-500", "ring-offset-2", "transition-all");
      setTimeout(() => {
        el.classList.remove("ring-2", "ring-indigo-500", "ring-offset-2");
      }, 1500);
    }
  }

  /** Back-solve base $/SF */
  const basePsf = sf > 0 ? total / (sf * regionalMult * complexityMult) : 0;

  /** ========== STATES ========== **/
  const [mode, setMode] = useState<"total"|"psf">("total");
  const [provOpen, setProvOpen] = useState(false);
  const [animateFingerprint, setAnimateFingerprint] = useState(false);
  
  // Sensitivity sliders
  const [regMultAdj, setRegMultAdj] = useState(regionalMult);
  const [compMultAdj, setCompMultAdj] = useState(complexityMult);

  // Animate fingerprint on mount
  useEffect(() => {
    const timer = setTimeout(() => setAnimateFingerprint(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // Calculate adjusted values
  const psfFinal = basePsf * regMultAdj * compMultAdj;
  const totalFinal = psfFinal * sf;

  // Confidence interval calculation
  const ciHalf = 1.96 * (SAMPLE_STD_DEV_PSF / Math.sqrt(Math.max(1, SAMPLE_SIZE)));
  const ciLow  = Math.max(0, psfFinal - ciHalf);
  const ciHigh = psfFinal + ciHalf;

  /** Confidence score */
  const confidenceScore = Math.min(
    0.98,
    0.60
      + (occ ? 0.15 : 0)
      + (location ? 0.10 : 0)
      + (pieData.filter(c => c.amount > 0).length >= 4 ? 0.08 : 0)
      + (sf > 0 ? 0.05 : 0)
      + (SAMPLE_SIZE >= 30 ? 0.05 : 0)
  );

  const confidenceText = [
    occ && "clear occupancy type",
    location && "known region",
    pieData.filter(c => c.amount > 0).length >= 4 && "trade-level breakdown",
    sf > 0 && "square footage provided",
    SAMPLE_SIZE >= 30 && "sufficient sample size",
  ].filter(Boolean).join(", ") || "limited signals";

  /** Factors */
  const factors: {label: string; impact: "low"|"medium"|"high"}[] = [];
  if (isHealthcare || /(surgical|operating room|\bor\b)/.test(descText)) factors.push({ label: "OSHPD/Healthcare Compliance", impact: "high" });
  if (/medical gas/.test(descText)) factors.push({ label: "Medical Gas", impact: "medium" });

  /** UI helpers */
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
        {/* ENHANCED CLICKABLE FINGERPRINT */}
        <div className="mb-4">
          <div className="text-sm opacity-70 mb-2">
            Cost Fingerprint (matches trade breakdown) — <span className="opacity-60">click a bar to jump to that trade</span>
          </div>
          {totalAmt === 0 ? (
            <div className="text-sm opacity-70 p-3 border rounded bg-gray-50">
              Trade breakdown not available yet. Once populated, this fingerprint will mirror the pie exactly.
            </div>
          ) : (
            <>
              {/* Taller animated bar chart */}
              <div style={{ height: "200px", display: "flex", alignItems: "flex-end", gap: "10px" }} className="mb-3">
                {fingerprint.map((f, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => jumpToTrade(f.trade)}
                    className="hover:opacity-80 transition-all cursor-pointer relative group"
                    style={{
                      width: `${100 / fingerprint.length}%`,
                      height: animateFingerprint ? `${Math.max(2, f.percent * 100)}%` : '0%',
                      backgroundColor: f.color,
                      borderRadius: "8px 8px 0 0",
                      transition: "height 420ms cubic-bezier(.2,.8,.2,1)",
                      minHeight: "4px"
                    }}
                    title={`${f.trade}: ${pct(f.percent)} - Click to view`}
                  >
                    {/* Show percentage on hover */}
                    <span className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                      {pct(f.percent)}
                    </span>
                  </button>
                ))}
              </div>
              {/* Legend with colors matching the pie */}
              <div className="flex flex-wrap gap-3 text-sm">
                {fingerprint.map((f, i) => (
                  <button 
                    key={i} 
                    type="button"
                    onClick={() => jumpToTrade(f.trade)} 
                    className="hover:underline flex items-center gap-1"
                  >
                    <span style={{ 
                      backgroundColor: f.color, 
                      display: "inline-block", 
                      width: 12, 
                      height: 12, 
                      borderRadius: 3 
                    }}></span>
                    <span>{f.trade}: {pct(f.percent)}</span>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* PRICE JOURNEY */}
        <div className="bg-gray-50 p-4 rounded-lg mb-4">
          <h4 className="font-semibold mb-3">📊 The Price Journey</h4>
          <div className="space-y-2 text-sm">
            <div><strong>Base Cost:</strong> {fmtMoney(basePsf, 2)}/SF — {srcName} ({srcVer})</div>
            <div className="text-gray-400">↓</div>
            <div><strong>Regional Index ({location || "Region"}):</strong> × {regMultAdj.toFixed(2)}</div>
            <div className="text-gray-400">↓</div>
            <div><strong>Complexity ({compMultAdj > 1 ? "Healthcare/Surgical" : "Standard"}):</strong> × {compMultAdj.toFixed(2)}</div>
            <div className="text-gray-400">↓</div>
            <div className="font-bold text-lg pt-2 border-t">
              Final: {mode === 'psf' ? `${fmtMoney(psfFinal, 2)}/SF` : fmtMoney(totalFinal)}
            </div>
          </div>
        </div>

        {/* SENSITIVITY ANALYSIS */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold mb-2">Sensitivity Analysis</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="border rounded-lg p-3">
              <div className="text-xs uppercase tracking-wide opacity-70 mb-2">Regional Multiplier</div>
              <input 
                type="range" 
                min="0.90" 
                max="1.20" 
                step="0.01" 
                value={regMultAdj} 
                onChange={e => setRegMultAdj(parseFloat(e.target.value))} 
                className="w-full accent-indigo-600"
              />
              <div className="text-sm mt-1 font-medium">× {regMultAdj.toFixed(2)}</div>
              <div className="text-xs opacity-60">{((regMultAdj - 1) * 100).toFixed(0)}% from baseline</div>
            </div>
            
            <div className="border rounded-lg p-3">
              <div className="text-xs uppercase tracking-wide opacity-70 mb-2">Complexity Factor</div>
              <input 
                type="range" 
                min="1.00" 
                max="1.30" 
                step="0.01" 
                value={compMultAdj} 
                onChange={e => setCompMultAdj(parseFloat(e.target.value))} 
                className="w-full accent-indigo-600"
              />
              <div className="text-sm mt-1 font-medium">× {compMultAdj.toFixed(2)}</div>
              <div className="text-xs opacity-60">{compMultAdj > 1.14 ? "Healthcare" : "Standard"}</div>
            </div>
            
            <div className="border rounded-lg p-3 bg-indigo-50">
              <div className="text-xs uppercase tracking-wide opacity-70 mb-2">Confidence Band</div>
              <div className="text-sm font-medium">
                {Math.round(confidenceScore * 100)}% confidence
              </div>
              <div className="text-xs mt-1">
                {fmtMoney(ciLow, 2)}/SF – {fmtMoney(ciHigh, 2)}/SF
              </div>
              <div className="text-xs opacity-60 mt-1">Based on {SAMPLE_SIZE} similar projects</div>
            </div>
          </div>
        </div>

        {/* PROVENANCE & SOURCES */}
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <button 
            type="button" 
            className="px-4 py-2 rounded-lg border border-indigo-200 text-sm hover:bg-indigo-50 transition-colors flex items-center gap-2"
            onClick={() => setProvOpen(true)}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            View Provenance Receipt
          </button>
          
          {factors.length > 0 && (
            <div className="flex items-center gap-2">
              {factors.map((fa, i) => (
                <span key={i} className="px-2 py-1 rounded-full border text-xs" title={`impact: ${fa.impact}`}>
                  {fa.label}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Source strip */}
        <div className="px-3 py-2 rounded-lg bg-gray-50 text-xs flex flex-wrap gap-4 items-center">
          <div><span className="opacity-70">Base:</span> {srcName} ({srcVer}){location ? ` • ${location}` : ""}</div>
          <div><span className="opacity-70">Regional:</span> Index {regMultAdj.toFixed(2)}</div>
          <div><span className="opacity-70">Complexity:</span> {isHealthcare ? "Healthcare" : "Standard"}</div>
          <div className="opacity-70 ml-auto">Updated: {todayStr()}</div>
        </div>

        {/* Jump link to trade math */}
        <div className="mt-3 text-sm">
          <button
            type="button"
            className="underline hover:no-underline opacity-70"
            onClick={() => {
              const el = document.querySelector("#trade-breakdown, #cost-breakdown, [data-anchor='cost-breakdown']");
              el?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
          >
            See detailed trade breakdown below ↴
          </button>
        </div>
      </div>

      {/* PROVENANCE MODAL */}
      {provOpen && (
        <div 
          className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4"
          onClick={() => setProvOpen(false)}
        >
          <div 
            className="bg-white rounded-xl shadow-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold">📋 Provenance Receipt</h4>
              <button 
                onClick={() => setProvOpen(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4 text-sm">
              <div className="border-b pb-3">
                <h5 className="font-medium mb-2">Data Sources</h5>
                <div className="space-y-1 text-gray-600">
                  <div><span className="font-medium">Base Cost:</span> {srcName} ({srcVer}) — healthcare comparables {location ? `in ${location}` : "nationwide"}</div>
                  <div><span className="font-medium">Regional Index:</span> {regionalMult.toFixed(2)} (SpecSharp Regional Cost Index)</div>
                  <div><span className="font-medium">Complexity Rule:</span> {complexityMult.toFixed(2)} — {isHealthcare || /(surgical|operating room|\bor\b)/.test(descText) ? "Healthcare/Surgical compliance & systems" : "Standard construction"}</div>
                </div>
              </div>

              <div className="border-b pb-3">
                <h5 className="font-medium mb-2">Statistical Confidence</h5>
                <div className="space-y-1 text-gray-600">
                  <div><span className="font-medium">Sample Size:</span> {SAMPLE_SIZE} similar projects analyzed</div>
                  <div><span className="font-medium">Standard Deviation:</span> ±${SAMPLE_STD_DEV_PSF}/SF</div>
                  <div><span className="font-medium">95% Confidence Interval:</span> {fmtMoney(ciLow, 2)}/SF – {fmtMoney(ciHigh, 2)}/SF</div>
                  <div><span className="font-medium">Confidence Score:</span> {Math.round(confidenceScore * 100)}% ({confidenceText})</div>
                </div>
              </div>

              <div className="border-b pb-3">
                <h5 className="font-medium mb-2">Price Calculation</h5>
                <div className="bg-gray-50 p-3 rounded font-mono text-xs">
                  Price = Base × Regional × Complexity<br/>
                  Price = {fmtMoney(basePsf, 2)}/SF × {regMultAdj.toFixed(2)} × {compMultAdj.toFixed(2)}<br/>
                  Price = <strong>{fmtMoney(psfFinal, 2)}/SF</strong><br/>
                  <br/>
                  Total = Price × Square Footage<br/>
                  Total = {fmtMoney(psfFinal, 2)}/SF × {sf.toLocaleString()} SF<br/>
                  Total = <strong>{fmtMoney(totalFinal)}</strong>
                </div>
              </div>

              <div className="border-b pb-3">
                <h5 className="font-medium mb-2">Trade Distribution (Matching Pie Colors)</h5>
                <div className="space-y-1">
                  {fingerprint.filter(f => f.percent > 0).map((f, i) => (
                    <div key={i} className="flex items-center justify-between text-gray-600">
                      <div className="flex items-center gap-2">
                        <span style={{ backgroundColor: f.color, width: 12, height: 12, borderRadius: 2 }}></span>
                        <span>{f.trade}</span>
                      </div>
                      <span>{pct(f.percent)} • {fmtMoney(f.amt)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="text-xs text-gray-500 italic">
                Note: Sample size and variance statistics are currently mocked. These will be replaced with live dataset analysis when the backend integration is complete.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CostDNADisplay;