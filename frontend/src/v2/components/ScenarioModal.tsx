import React, { useEffect, useMemo, useState } from "react";
import { X, TrendingDown, TrendingUp, Scale } from "lucide-react";

type FallbackScenarioKey = "base" | "value_engineered" | "high_end";
type AnyRecord = Record<string, any>;

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
  multipliers?: Partial<Record<FallbackScenarioKey, { cost: number; revenue: number }>>;
  dealShieldScenarioBundle?: unknown;
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

const toRecord = (value: unknown): AnyRecord =>
  value && typeof value === "object" && !Array.isArray(value) ? (value as AnyRecord) : {};

const toFiniteNumber = (value: unknown): number | null => {
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  if (typeof value === "string") {
    const normalized = value.trim().replace(/[$,%\s,]/g, "");
    if (!normalized) return null;
    const parsed = Number(normalized);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const getPathValue = (source: AnyRecord, path: string): unknown => {
  let current: unknown = source;
  for (const part of path.split(".")) {
    if (!current || typeof current !== "object" || Array.isArray(current)) return undefined;
    current = (current as AnyRecord)[part];
  }
  return current;
};

const pickNumber = (source: AnyRecord, paths: string[]): number | null => {
  for (const path of paths) {
    const value = toFiniteNumber(getPathValue(source, path));
    if (value !== null) return value;
  }
  return null;
};

const toPercentDisplayValue = (value: number | null): number | null => {
  if (value === null) return null;
  return Math.abs(value) <= 1 ? value * 100 : value;
};

const titleFromScenarioId = (scenarioId: string): string => {
  const normalized = scenarioId.trim().toLowerCase();
  if (normalized === "base") return "Base (Current)";
  if (normalized === "value_engineered") return "Value Engineered";
  if (normalized === "high_end") return "High-End Finishes";
  return scenarioId
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
};

const scenarioIconFor = (scenarioId: string, isBaseline = false) => {
  if (isBaseline) return Scale;
  const normalized = scenarioId.toLowerCase();
  if (normalized === "base") return Scale;
  if (
    normalized.includes("conservative") ||
    normalized.includes("ugly") ||
    normalized.includes("stress") ||
    normalized.includes("downside") ||
    normalized.includes("value_engineered")
  ) {
    return TrendingDown;
  }
  if (
    normalized.includes("high_end") ||
    normalized.includes("premium") ||
    normalized.includes("upside") ||
    normalized.includes("aggressive")
  ) {
    return TrendingUp;
  }
  return Scale;
};

const fmtScalar = (value: number | null) =>
  value === null || Number.isNaN(value) ? "—" : value.toFixed(2);

type NormalizedBundle = {
  scenarios: Record<string, AnyRecord>;
  scenarioInputs: Record<string, AnyRecord>;
  scenarioOrder: string[];
};

const normalizeScenarioInputs = (rawInputs: unknown): Record<string, AnyRecord> => {
  if (Array.isArray(rawInputs)) {
    const out: Record<string, AnyRecord> = {};
    rawInputs.forEach((item) => {
      const record = toRecord(item);
      const scenarioIdValue =
        record.scenario ??
        record.scenario_id ??
        record.scenarioId ??
        record.label ??
        record.name;
      if (typeof scenarioIdValue !== "string" || !scenarioIdValue.trim()) return;
      out[scenarioIdValue.trim()] = record;
    });
    return out;
  }
  if (rawInputs && typeof rawInputs === "object" && !Array.isArray(rawInputs)) {
    return Object.entries(rawInputs as AnyRecord).reduce<Record<string, AnyRecord>>((acc, [scenarioId, value]) => {
      acc[scenarioId] = toRecord(value);
      return acc;
    }, {});
  }
  return {};
};

const normalizeDealShieldBundle = (bundle: unknown): NormalizedBundle | null => {
  const root = toRecord(bundle);
  const viewModel = toRecord(root.view_model ?? root.viewModel);
  const candidates = [
    root,
    toRecord(root.dealshield_scenarios),
    toRecord(root.dealShieldScenarios),
    toRecord(viewModel.dealshield_scenarios),
    toRecord(viewModel.dealShieldScenarios),
  ];

  for (const candidate of candidates) {
    const scenariosRecord = toRecord(candidate.scenarios);
    const scenarioIds = Object.keys(scenariosRecord);
    if (scenarioIds.length === 0) continue;

    const provenance = toRecord(candidate.provenance);
    const rawOrder = Array.isArray(provenance.scenario_ids)
      ? provenance.scenario_ids
      : Array.isArray(candidate.scenario_ids)
        ? candidate.scenario_ids
        : [];
    const orderedIds = rawOrder
      .map((id) => (typeof id === "string" ? id.trim() : ""))
      .filter(Boolean)
      .filter((id, idx, arr) => arr.indexOf(id) === idx && id in scenariosRecord);

    const baseId = scenarioIds.find((id) => id.toLowerCase() === "base");
    const mergedOrder = [...orderedIds, ...scenarioIds.filter((id) => !orderedIds.includes(id))];
    const scenarioOrder = baseId ? [baseId, ...mergedOrder.filter((id) => id !== baseId)] : mergedOrder;

    const scenarioInputs = normalizeScenarioInputs(
      provenance.scenario_inputs ?? candidate.scenario_inputs ?? candidate.scenarioInputs
    );

    return {
      scenarios: scenariosRecord,
      scenarioInputs,
      scenarioOrder,
    };
  }

  return null;
};

type ScenarioCardView = {
  key: string;
  title: string;
  subtitle: string;
  icon: typeof Scale;
  multipliers: { cost: number | null; revenue: number | null };
  metrics: {
    totalInvestment: number | null;
    costPerSf: number | null;
    stabilizedNoi: number | null;
    stabilizedYieldPct: number | null;
    dscr: number | null;
    paybackYears: number | null;
  };
  appliedTileIds: string[];
  explainShort: string | null;
};

const deltaLabel = (base: number | null, current: number | null, mode: "money" | "pct" | "num") => {
  if (base === null || current === null || Number.isNaN(base) || Number.isNaN(current)) return null;
  const diff = current - base;
  if (Math.abs(diff) < 1e-9) return "No change";
  if (mode === "money") return `${diff >= 0 ? "+" : ""}${fmtMoneyCompact(diff)}`;
  if (mode === "pct") return `${diff >= 0 ? "+" : ""}${diff.toFixed(1)}%`;
  return `${diff >= 0 ? "+" : ""}${diff.toFixed(2)}`;
};

export const ScenarioModal: React.FC<ScenarioModalProps> = ({ open, onClose, base, multipliers, dealShieldScenarioBundle }) => {
  const [selectedKey, setSelectedKey] = useState<string>("base");
  const normalizedBundle = useMemo(
    () => normalizeDealShieldBundle(dealShieldScenarioBundle),
    [dealShieldScenarioBundle]
  );

  const fallbackMultipliers = useMemo(() => {
    const defaults: Record<FallbackScenarioKey, { cost: number; revenue: number }> = {
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

  const fallbackScenarios = useMemo<ScenarioCardView[]>(() => {
    const baseCost = base.totalInvestment;
    const baseNoi = base.stabilizedNoi;
    const baseYield = base.stabilizedYieldPct;
    const baseDscr = base.dscr;

    const mkScenario = (key: FallbackScenarioKey): ScenarioCardView => {
      const m = fallbackMultipliers[key];
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
        appliedTileIds: [],
        explainShort: null,
      };
    };

    return [mkScenario("base"), mkScenario("value_engineered"), mkScenario("high_end")];
  }, [base, fallbackMultipliers]);

  const backendScenarios = useMemo<ScenarioCardView[] | null>(() => {
    if (!normalizedBundle) return null;

    const scenarioList = normalizedBundle.scenarioOrder
      .map((scenarioId, index) => {
        const snapshot = toRecord(normalizedBundle.scenarios[scenarioId]);
        if (Object.keys(snapshot).length === 0) return null;

        const input = toRecord(
          normalizedBundle.scenarioInputs[scenarioId] ??
          normalizedBundle.scenarioInputs[scenarioId.toLowerCase()] ??
          normalizedBundle.scenarioInputs[scenarioId.toUpperCase()]
        );
        const explain = toRecord(input.explain);

        const appliedTileRaw = input.applied_tile_ids ?? input.appliedTileIds ?? input.tiles;
        const appliedTileIds = Array.isArray(appliedTileRaw)
          ? appliedTileRaw
              .map((id) => (id == null ? "" : String(id).trim()))
              .filter(Boolean)
          : [];

        const yieldValue = pickNumber(snapshot, [
          "ownership_analysis.yield_on_cost",
          "ownershipAnalysis.yieldOnCost",
          "yield_on_cost",
          "yieldOnCost",
        ]);

        const isBaselineScenario = scenarioId.toLowerCase() === "base" || index === 0;

        return {
          key: scenarioId,
          title: titleFromScenarioId(scenarioId),
          subtitle:
            typeof explain.short === "string" && explain.short.trim()
              ? explain.short.trim()
              : isBaselineScenario
                ? "Current case as modeled"
                : "Backend DealShield scenario snapshot",
          icon: scenarioIconFor(scenarioId, isBaselineScenario),
          multipliers: {
            cost: toFiniteNumber(input.cost_scalar ?? input.costScalar),
            revenue: toFiniteNumber(input.revenue_scalar ?? input.revenueScalar),
          },
          metrics: {
            totalInvestment: pickNumber(snapshot, ["totals.total_project_cost", "totals.totalProjectCost"]),
            costPerSf: pickNumber(snapshot, ["totals.cost_per_sf", "totals.costPerSf"]),
            stabilizedNoi: pickNumber(snapshot, [
              "ownership_analysis.return_metrics.estimated_annual_noi",
              "ownershipAnalysis.returnMetrics.estimatedAnnualNoi",
              "return_metrics.estimated_annual_noi",
              "returnMetrics.estimatedAnnualNoi",
            ]),
            stabilizedYieldPct: toPercentDisplayValue(yieldValue),
            dscr: pickNumber(snapshot, [
              "ownership_analysis.debt_metrics.calculated_dscr",
              "ownershipAnalysis.debtMetrics.calculatedDscr",
            ]),
            paybackYears: pickNumber(snapshot, [
              "ownership_analysis.return_metrics.payback_period",
              "ownershipAnalysis.returnMetrics.paybackPeriod",
              "return_metrics.payback_period",
              "returnMetrics.paybackPeriod",
            ]),
          },
          appliedTileIds,
          explainShort:
            typeof explain.short === "string" && explain.short.trim()
              ? explain.short.trim()
              : null,
        } as ScenarioCardView;
      })
      .filter((scenario): scenario is ScenarioCardView => scenario !== null);

    if (scenarioList.length === 0) return null;

    const hasNumericMetrics = scenarioList.some((scenario) => {
      const m = scenario.metrics;
      return [m.totalInvestment, m.costPerSf, m.stabilizedNoi, m.stabilizedYieldPct, m.dscr, m.paybackYears].some(
        (v) => v !== null
      );
    });
    if (!hasNumericMetrics) return null;

    return scenarioList;
  }, [normalizedBundle]);

  const scenarios = backendScenarios ?? fallbackScenarios;
  const usingBackendSnapshots = backendScenarios !== null;

  useEffect(() => {
    if (!open) return;
    if (scenarios.length === 0) return;
    if (!scenarios.some((scenario) => scenario.key === selectedKey)) {
      setSelectedKey(scenarios[0].key);
    }
  }, [open, scenarios, selectedKey]);

  const baseScenario = scenarios[0];
  const baseScenarioKey = baseScenario.key;
  const baseMetrics = baseScenario.metrics;
  const selectedScenario = scenarios.find((scenario) => scenario.key === selectedKey) || baseScenario;
  const selectedMetrics = selectedScenario.metrics;

  const summaryItems = [
    {
      label: "Total investment",
      value: fmtMoneyCompact(selectedMetrics.totalInvestment),
      delta: selectedScenario.key === baseScenarioKey ? null : deltaLabel(baseMetrics.totalInvestment, selectedMetrics.totalInvestment, "money"),
    },
    {
      label: "Yield",
      value: fmtPct(selectedMetrics.stabilizedYieldPct),
      delta: selectedScenario.key === baseScenarioKey ? null : deltaLabel(baseMetrics.stabilizedYieldPct, selectedMetrics.stabilizedYieldPct, "pct"),
    },
    {
      label: "DSCR",
      value: selectedMetrics.dscr === null ? "—" : `${fmtNum(selectedMetrics.dscr, 2)}×`,
      delta: selectedScenario.key === baseScenarioKey ? null : deltaLabel(baseMetrics.dscr, selectedMetrics.dscr, "num"),
    },
  ];

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[1000]">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="absolute inset-0 p-3 sm:p-6">
        <div className="h-full flex items-start justify-center">
          <div className="w-full max-w-6xl rounded-2xl border border-white/10 bg-gradient-to-br from-blue-950 via-blue-900 to-indigo-900 text-white shadow-2xl overflow-hidden h-full max-h-full flex flex-col">
            <div className="px-7 py-5 border-b border-white/10 flex items-start justify-between gap-6 shrink-0 sticky top-0 z-10 bg-gradient-to-r from-blue-950/95 via-blue-900/95 to-indigo-900/95 backdrop-blur">
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

            <div className="p-7 space-y-6 overflow-y-auto min-h-0">
              <div className="rounded-xl border border-white/15 bg-white/10 backdrop-blur p-4">
                <div className="text-sm font-semibold">
                  How this works ({usingBackendSnapshots ? "backend snapshots" : "v1"})
                </div>
                <div className="text-sm text-slate-300 mt-1">
                  {usingBackendSnapshots
                    ? "Scenarios are sourced from backend DealShield snapshots and show fully recomputed underwriting outputs per scenario."
                    : "Scenarios apply universal multipliers to capex and NOI. Yield is re-computed from NOI ÷ total cost; DSCR & payback scale with NOI. Future versions will re-run full underwriting per building type/subtype."}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
                {scenarios.map((scenario) => {
                  const Icon = scenario.icon;
                  const isBase = scenario.key === baseScenarioKey;
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
                            <div>Cost × {fmtScalar(scenario.multipliers.cost)}</div>
                            <div>NOI × {fmtScalar(scenario.multipliers.revenue)}</div>
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
                          <div className="text-xs text-slate-300 mt-2">
                            Cost/SF:{" "}
                            <span className="text-white font-semibold">
                              {m.costPerSf === null ? "—" : `$${m.costPerSf.toFixed(0)}/SF`}
                            </span>
                            {!isBase && baseMetrics.costPerSf !== null && m.costPerSf !== null ? (
                              <span className="text-slate-300"> ({deltaLabel(baseMetrics.costPerSf, m.costPerSf, "num")})</span>
                            ) : null}
                          </div>
                          {scenario.appliedTileIds.length > 0 && (
                            <div className="text-xs text-slate-300 mt-2">
                              Tiles: <span className="text-white font-semibold">{scenario.appliedTileIds.join(", ")}</span>
                            </div>
                          )}
                          {scenario.explainShort && (
                            <div className="text-xs text-slate-400 mt-2">{scenario.explainShort}</div>
                          )}
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
                {usingBackendSnapshots
                  ? "Note: Metrics and levers come from backend DealShield scenario snapshots when available."
                  : "Note: VE and High-End multipliers are universal in v1. Future update will pull subtype-specific drivers (scope deltas, rents, and financing)."}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
