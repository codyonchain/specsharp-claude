import React, { useMemo, useState } from "react";
import { X, TrendingDown, TrendingUp, Scale } from "lucide-react";

type ScenarioKey = "base" | "value_engineered" | "high_end";

export type ScenarioBaseMetrics = {
  projectTitle: string;
  locationLine: string;

  totalInvestment: number | null;
  costPerSf: number | null;

  stabilizedNoi: number | null;
  stabilizedYieldPct: number | null;
  dscr: number | null;
  paybackYears: number | null;
};

export type ScenarioModalProps = {
  open: boolean;
  onClose: () => void;
  base: ScenarioBaseMetrics;
  multipliers?: Partial<Record<ScenarioKey, { cost: number; revenue: number }>>;
};

const fmtMoney = (v: number | null) =>
  v === null || Number.isNaN(v) ? "—" : v.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

const fmtMoneyCompact = (v: number | null) => {
  if (v === null || Number.isNaN(v)) return "—";
  const abs = Math.abs(v);
  if (abs >= 1_000_000_000) return `$${(v / 1_000_000_000).toFixed(2)}B`;
  if (abs >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000) return `$${(v / 1_000).toFixed(0)}K`;
  return fmtMoney(v);
};

const fmtPct = (v: number | null, digits = 1) =>
  v === null || Number.isNaN(v) ? "—" : `${v.toFixed(digits)}%`;

const fmtNum = (v: number | null, digits = 2) =>
  v === null || Number.isNaN(v) ? "—" : v.toFixed(digits);

const deltaLabel = (base: number | null, current: number | null, mode: "money" | "pct" | "num") => {
  if (base === null || current === null || Number.isNaN(base) || Number.isNaN(current)) return null;
  const diff = current - base;
  if (Math.abs(diff) < 1e-9) return "No change";
  if (mode === "money") return `${diff >= 0 ? "+" : ""}${fmtMoneyCompact(diff)}`;
  if (mode === "pct") return `${diff >= 0 ? "+" : ""}${diff.toFixed(1)}%`;
  return `${diff >= 0 ? "+" : ""}${diff.toFixed(2)}`;
};

export const ScenarioModal: React.FC<ScenarioModalProps> = ({ open, onClose, base, multipliers }) => {
  const [selectedKey, setSelectedKey] = useState<ScenarioKey>("base");
  const mult = useMemo(() => {
    const defaults: Record<ScenarioKey, { cost: number; revenue: number }> = {
      base: { cost: 1.0, revenue: 1.0 },
      value_engineered: { cost: 0.94, revenue: 1.0 },
      high_end: { cost: 1.06, revenue: 1.03 },
    };
    return {
      base: { ...defaults.base, ...(multipliers?.base || {}) },
      value_engineered: { ...defaults.value_engineered, ...(multipliers?.value_engineered || {}) },
      high_end: { ...defaults.high_end, ...(multipliers?.high_end || {}) },
    };
  }, [multipliers]);

  const scenarios = useMemo(() => {
    const baseCost = base.totalInvestment;
    const baseNoi = base.stabilizedNoi;
    const baseYield = base.stabilizedYieldPct;
    const baseDscr = base.dscr;

    const mkScenario = (key: ScenarioKey) => {
      const m = mult[key];
      const totalInvestment = baseCost === null ? null : Math.round(baseCost * m.cost);
      const stabilizedNoi = baseNoi === null ? null : baseNoi * m.revenue;
      const stabilizedYieldPct =
        stabilizedNoi !== null && totalInvestment !== null && totalInvestment > 0
          ? (stabilizedNoi / totalInvestment) * 100
          : baseYield === null
            ? null
            : (baseYield * m.revenue) / m.cost;
      const dscr = baseDscr === null ? null : baseDscr * m.revenue;
      const costPerSf = base.costPerSf === null ? null : base.costPerSf * m.cost;
      const paybackYears = base.paybackYears === null ? null : base.paybackYears / m.revenue;

      return {
        key,
        title: key === "base" ? "Base (Current)" : key === "value_engineered" ? "Value Engineered" : "High-End Finishes",
        subtitle:
          key === "base"
            ? "Current case as modeled"
            : key === "value_engineered"
              ? "Cost-reduced scope / VE package"
              : "Premium / flagship finish package",
        icon: key === "base" ? Scale : key === "value_engineered" ? TrendingDown : TrendingUp,
        multipliers: m,
        metrics: {
          totalInvestment,
          costPerSf,
          stabilizedNoi,
          stabilizedYieldPct,
          dscr,
          paybackYears,
        },
      };
    };

    return [mkScenario("base"), mkScenario("value_engineered"), mkScenario("high_end")];
  }, [base, mult]);

  const baseScenario = scenarios[0];
  const baseMetrics = baseScenario.metrics;
  const selectedScenario = scenarios.find((scenario) => scenario.key === selectedKey) || baseScenario;
  const selectedMetrics = selectedScenario.metrics;

  const summaryItems = [
    {
      label: "Total investment",
      value: fmtMoneyCompact(selectedMetrics.totalInvestment),
      delta: selectedScenario.key === "base" ? null : deltaLabel(baseMetrics.totalInvestment, selectedMetrics.totalInvestment, "money"),
    },
    {
      label: "Yield",
      value: fmtPct(selectedMetrics.stabilizedYieldPct),
      delta: selectedScenario.key === "base" ? null : deltaLabel(baseMetrics.stabilizedYieldPct, selectedMetrics.stabilizedYieldPct, "pct"),
    },
    {
      label: "DSCR",
      value: selectedMetrics.dscr === null ? "—" : `${fmtNum(selectedMetrics.dscr, 2)}×`,
      delta: selectedScenario.key === "base" ? null : deltaLabel(baseMetrics.dscr, selectedMetrics.dscr, "num"),
    },
  ];

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[1000]">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="absolute inset-0 flex items-center justify-center p-6">
        <div className="w-full max-w-6xl rounded-2xl border border-white/10 bg-gradient-to-br from-blue-950 via-blue-900 to-indigo-900 text-white shadow-2xl overflow-hidden">
          <div className="px-7 py-5 border-b border-white/10 flex items-start justify-between gap-6">
            <div>
              <div className="text-xs tracking-[0.18em] uppercase text-slate-300">Scenario Analysis</div>
              <div className="text-xl font-extrabold mt-1">{base.projectTitle}</div>
              <div className="text-sm text-slate-300 mt-1">{base.locationLine}</div>
            </div>
            <button
              onClick={onClose}
              className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm hover:bg-white/10 transition"
            >
              <X className="h-4 w-4" />
              Close
            </button>
          </div>

          <div className="p-7 space-y-6">
            <div className="rounded-xl border border-white/15 bg-white/10 backdrop-blur p-4">
              <div className="text-sm font-semibold">How this works (v1)</div>
              <div className="text-sm text-slate-300 mt-1">
                Scenarios apply universal multipliers to capex and NOI. Yield is re-computed from NOI ÷ total cost; DSCR & payback scale with NOI. Future versions will re-run full underwriting per building type/subtype.
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
              {scenarios.map((scenario) => {
                const Icon = scenario.icon;
                const isBase = scenario.key === "base";
                const isSelected = scenario.key === selectedKey;
                const m = scenario.metrics;
                return (
                  <div
                    key={scenario.key}
                    role="button"
                    tabIndex={0}
                    onClick={() => setSelectedKey(scenario.key)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        setSelectedKey(scenario.key);
                      }
                    }}
                    className={`h-full flex flex-col rounded-2xl border p-5 transition cursor-pointer ${
                      isSelected
                        ? "border-white/60 bg-white/10 shadow-2xl ring-2 ring-white/40"
                        : "border-white/10 bg-white/5 hover:bg-white/10"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`h-9 w-9 rounded-xl flex items-center justify-center ${
                            isSelected ? "bg-white/20" : isBase ? "bg-white/10" : "bg-white/5"
                          }`}
                        >
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="font-extrabold">{scenario.title}</div>
                          <div className="text-xs text-slate-300 mt-0.5">{scenario.subtitle}</div>
                        </div>
                      </div>
                      <div className="text-right text-xs text-slate-300 flex flex-col items-end gap-1">
                        {isSelected && (
                          <span className="inline-flex items-center rounded-full bg-emerald-400/20 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-emerald-200">
                            Selected
                          </span>
                        )}
                        <div className="text-right">
                          <div>Cost × {scenario.multipliers.cost.toFixed(2)}</div>
                          <div>NOI × {scenario.multipliers.revenue.toFixed(2)}</div>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 flex-1 flex flex-col">
                      <div className="space-y-3">
                        <div className="rounded-xl bg-slate-900/40 border border-white/10 p-4">
                          <div className="text-[11px] tracking-[0.14em] uppercase text-slate-300">Total Investment</div>
                          <div className="text-2xl font-extrabold mt-1">{fmtMoneyCompact(m.totalInvestment)}</div>
                          {!isBase && (
                            <div className="text-xs text-slate-300 mt-1">
                              {deltaLabel(baseMetrics.totalInvestment, m.totalInvestment, "money")}
                            </div>
                          )}
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <div className="rounded-xl bg-slate-900/40 border border-white/10 p-4">
                            <div className="text-[11px] tracking-[0.14em] uppercase text-slate-300">Yield (NOI/Cost)</div>
                            <div className="text-xl font-extrabold mt-1">{fmtPct(m.stabilizedYieldPct)}</div>
                            {!isBase && (
                              <div className="text-xs text-slate-300 mt-1">
                                {deltaLabel(baseMetrics.stabilizedYieldPct, m.stabilizedYieldPct, "pct")}
                              </div>
                            )}
                          </div>
                          <div className="rounded-xl bg-slate-900/40 border border-white/10 p-4">
                            <div className="text-[11px] tracking-[0.14em] uppercase text-slate-300">DSCR</div>
                            <div className="text-xl font-extrabold mt-1">
                              {fmtNum(m.dscr, 2)}
                              {m.dscr === null ? "" : "×"}
                            </div>
                            {!isBase && (
                              <div className="text-xs text-slate-300 mt-1">
                                {deltaLabel(baseMetrics.dscr, m.dscr, "num")}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <div className="rounded-xl bg-slate-900/40 border border-white/10 p-4">
                            <div className="text-[11px] tracking-[0.14em] uppercase text-slate-300">Stabilized NOI</div>
                            <div className="text-xl font-extrabold mt-1">{fmtMoneyCompact(m.stabilizedNoi)}</div>
                            {!isBase && (
                              <div className="text-xs text-slate-300 mt-1">
                                {deltaLabel(baseMetrics.stabilizedNoi, m.stabilizedNoi, "money")}
                              </div>
                            )}
                          </div>
                          <div className="rounded-xl bg-slate-900/40 border border-white/10 p-4">
                            <div className="text-[11px] tracking-[0.14em] uppercase text-slate-300">Payback</div>
                            <div className="text-xl font-extrabold mt-1">
                              {m.paybackYears === null ? "—" : `${m.paybackYears.toFixed(1)} yrs`}
                            </div>
                            {!isBase && (
                              <div className="text-xs text-slate-300 mt-1">
                                {deltaLabel(baseMetrics.paybackYears, m.paybackYears, "num")}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="rounded-xl bg-white/5 border border-white/10 p-4 mt-auto">
                        <div className="text-xs text-slate-300">
                          Cost/SF:{" "}
                          <span className="text-white font-semibold">
                            {m.costPerSf === null ? "—" : `$${m.costPerSf.toFixed(0)}/SF`}
                          </span>
                          {!isBase && baseMetrics.costPerSf !== null && m.costPerSf !== null ? (
                            <span className="text-slate-300"> ({deltaLabel(baseMetrics.costPerSf, m.costPerSf, "num")})</span>
                          ) : null}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="rounded-2xl border border-white/20 bg-white/10 px-6 py-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-[11px] tracking-[0.2em] uppercase text-slate-300">Selected Scenario</div>
                <div className="text-lg font-bold mt-1">{selectedScenario.title}</div>
                <div className="text-sm text-slate-200 mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                  {summaryItems.map((item, idx) => (
                    <span key={item.label} className="flex items-center gap-1">
                      <span className="font-semibold text-white">{item.label}:</span>
                      <span>{item.value}</span>
                      {item.delta ? <span className="text-slate-400">({item.delta})</span> : null}
                      {idx < summaryItems.length - 1 ? <span className="text-slate-500">•</span> : null}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={onClose}
                className="inline-flex items-center justify-center rounded-full border border-white/30 bg-white/10 px-6 py-2 text-sm font-semibold uppercase tracking-wide text-white hover:bg-white/20 transition"
              >
                Keep Browsing
              </button>
            </div>

            <div className="text-xs text-slate-400">
              Note: VE and High-End multipliers are universal in v1. Future update will pull subtype-specific drivers (scope deltas, rents, and financing).
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
