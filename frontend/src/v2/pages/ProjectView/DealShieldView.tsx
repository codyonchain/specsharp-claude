import React, { useEffect, useMemo, useState } from 'react';
import { Download, ShieldCheck } from 'lucide-react';
import { api } from '../../api/client';
import { DealShieldViewModel } from '../../types';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { pdfService } from '@/services/api';

interface Props {
  projectId: string;
  data?: DealShieldViewModel | null;
  loading?: boolean;
  error?: Error | null;
}

const formatValue = (value: unknown) => {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'number' && Number.isFinite(value)) {
    return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
  }
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'string') return value;
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
};

const isCurrencyMetric = (metricRef: unknown) => {
  if (typeof metricRef !== 'string') return false;
  const ref = metricRef.toLowerCase();
  const hints = ['cost', 'revenue', 'price', 'value', 'amount', 'budget', 'income', 'noi', 'capex', 'opex'];
  return hints.some(hint => ref.includes(hint));
};

const formatDecisionMetricValue = (value: unknown, metricRef: unknown) => {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'number' && Number.isFinite(value)) {
    if (isCurrencyMetric(metricRef)) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0,
      }).format(value);
    }
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  }
  return formatValue(value);
};

const labelFrom = (value: any, fallback: string = '-') => {
  if (!value) return fallback;
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return String(value);
  if (typeof value === 'object') {
    return (
      value.label ??
      value.name ??
      value.title ??
      value.display ??
      value.text ??
      value.question ??
      value.flag ??
      value.action ??
      value.value ??
      fallback
    );
  }
  return fallback;
};

const listValue = (value: unknown) => {
  if (Array.isArray(value)) return value.map(item => formatValue(item)).join(', ');
  return formatValue(value);
};

export const DealShieldView: React.FC<Props> = ({
  projectId,
  data,
  loading,
  error,
}) => {
  const isControlled = data !== undefined || loading !== undefined || error !== undefined;
  const [localState, setLocalState] = useState<{
    data: DealShieldViewModel | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: !isControlled,
    error: null,
  });
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (isControlled || !projectId) return;
    let isActive = true;
    setLocalState({ data: null, loading: true, error: null });
    api.fetchDealShield(projectId)
      .then((response) => {
        if (!isActive) return;
        setLocalState({ data: response, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (!isActive) return;
        setLocalState({ data: null, loading: false, error: err });
      });
    return () => {
      isActive = false;
    };
  }, [isControlled, projectId]);

  const dealShieldData = isControlled ? data ?? null : localState.data;
  const dealShieldLoading = isControlled ? !!loading : localState.loading;
  const dealShieldError = isControlled ? error ?? null : localState.error;

  const viewModel = useMemo(() => {
    if (!dealShieldData) return null;
    return (
      (dealShieldData as any).view_model ??
      (dealShieldData as any).viewModel ??
      dealShieldData
    );
  }, [dealShieldData]);

  const content = (viewModel as any)?.content ?? (dealShieldData as any)?.content ?? {};
  const decisionTable = (viewModel as any)?.decision_table ?? (viewModel as any)?.decisionTable ?? null;
  const fallbackColumns = Array.isArray((viewModel as any)?.columns) ? (viewModel as any).columns : [];
  const fallbackRows = Array.isArray((viewModel as any)?.rows) ? (viewModel as any).rows : [];
  const columns = Array.isArray(decisionTable?.columns) ? decisionTable.columns : fallbackColumns;
  const rows = Array.isArray(decisionTable?.rows) ? decisionTable.rows : fallbackRows;

  const fastestChangeDrivers = Array.isArray(content?.fastest_change?.drivers)
    ? content.fastest_change.drivers
    : Array.isArray(content?.fastestChange?.drivers)
      ? content.fastestChange.drivers
      : [];
  const fastestChangeText = fastestChangeDrivers
    .map((driver: any) => labelFrom(driver, ''))
    .filter(Boolean)
    .join('; ');

  const mostLikelyWrongRaw =
    content?.most_likely_wrong ??
    content?.mostLikelyWrong ??
    content?.most_likely_wrong_items ??
    [];
  const mostLikelyWrong = Array.isArray(mostLikelyWrongRaw)
    ? mostLikelyWrongRaw
    : Array.isArray(mostLikelyWrongRaw?.items)
      ? mostLikelyWrongRaw.items
      : [];

  const questionBankRaw = content?.question_bank ?? content?.questionBank ?? [];
  const questionBank = Array.isArray(questionBankRaw)
    ? questionBankRaw
    : Array.isArray(questionBankRaw?.items)
      ? questionBankRaw.items
      : [];
  const hasDriverTileId = questionBank.some(
    (item: any) => item?.driver_tile_id || item?.driverTileId
  );
  const questionGroups = questionBank.reduce((acc: Record<string, any[]>, item: any) => {
    const key = hasDriverTileId
      ? (item?.driver_tile_id || item?.driverTileId || '-')
      : 'all';
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  }, {});

  const redFlagsActionsRaw = content?.red_flags_actions ?? content?.redFlagsActions ?? [];
  const redFlagsActions = Array.isArray(redFlagsActionsRaw) ? redFlagsActionsRaw : [];
  const redFlagsRaw = content?.red_flags ?? content?.redFlags ?? [];
  const actionsRaw = content?.actions ?? content?.action_items ?? content?.actionItems ?? [];
  const redFlags = Array.isArray(redFlagsRaw) && redFlagsRaw.length > 0
    ? redFlagsRaw
    : redFlagsActions.map((item: any) => item?.flag).filter(Boolean);
  const actions = Array.isArray(actionsRaw) && actionsRaw.length > 0
    ? actionsRaw
    : redFlagsActions.map((item: any) => item?.action).filter(Boolean);

  const provenance = (viewModel as any)?.provenance ?? (dealShieldData as any)?.provenance ?? {};
  const scenarioInputsRaw = provenance?.scenario_inputs ?? (viewModel as any)?.scenario_inputs;
  const scenarioInputs = useMemo(() => {
    if (Array.isArray(scenarioInputsRaw)) return scenarioInputsRaw;
    if (scenarioInputsRaw && typeof scenarioInputsRaw === 'object') {
      return Object.entries(scenarioInputsRaw).map(([scenarioId, input]) => {
        const payload = input && typeof input === 'object' ? input : {};
        return {
          scenario: scenarioId,
          ...(payload as Record<string, unknown>),
        };
      });
    }
    return [];
  }, [scenarioInputsRaw]);
  const metricRefsUsed = Array.isArray(provenance?.metric_refs_used)
    ? provenance.metric_refs_used
    : Array.isArray((viewModel as any)?.metric_refs_used)
      ? (viewModel as any).metric_refs_used
      : [];

  const profileId =
    (dealShieldData as any)?.profile_id ??
    (dealShieldData as any)?.profileId ??
    (viewModel as any)?.profile_id ??
    (viewModel as any)?.profileId;
  const context =
    (dealShieldData as any)?.context ??
    (viewModel as any)?.context ??
    (dealShieldData as any)?.profile_context ??
    {};
  const contextLocation =
    context?.location_display ??
    context?.location ??
    [context?.city, context?.state].filter(Boolean).join(', ');
  const contextSf =
    context?.square_footage ??
    context?.squareFootage ??
    context?.sf ??
    context?.gross_sf ??
    context?.grossSf;

  const handleExportPdf = async () => {
    if (!projectId || exporting) return;
    try {
      setExporting(true);
      const response = await pdfService.exportDealShield(projectId);
      const blob = new Blob(
        [response.data],
        { type: response.headers?.['content-type'] || 'application/pdf' }
      );

      const filename = `dealshield_${projectId}.pdf`;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('DealShield PDF export failed:', err);
      alert('Failed to export DealShield PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-blue-600" />
              <h2 className="text-2xl font-semibold text-slate-900">DealShield</h2>
            </div>
            {profileId && (
              <p className="text-sm text-slate-500">
                profile_id: <span className="font-medium text-slate-700">{profileId}</span>
              </p>
            )}
            <div className="flex flex-wrap gap-2 text-xs text-slate-600">
              {contextLocation && (
                <span className="rounded-full bg-slate-100 px-2.5 py-1">
                  {contextLocation}
                </span>
              )}
              {contextSf !== undefined && contextSf !== null && contextSf !== '' && (
                <span className="rounded-full bg-slate-100 px-2.5 py-1">
                  {formatValue(contextSf)} SF
                </span>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={handleExportPdf}
            disabled={!dealShieldData || exporting}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Download className="h-4 w-4" />
            {exporting ? 'Exporting...' : 'Export DealShield PDF'}
          </button>
        </div>
      </div>

      {dealShieldLoading && (
        <LoadingSpinner size="large" message="Loading DealShield..." />
      )}

      {dealShieldError && (
        <ErrorMessage error="DealShield not available" />
      )}

      {!dealShieldLoading && !dealShieldError && !dealShieldData && (
        <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">
          DealShield not available.
        </div>
      )}

      {!dealShieldLoading && !dealShieldError && dealShieldData && (
        <>
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Decision Metrics</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full border border-slate-200 text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-3 py-2 text-left font-semibold">Scenario</th>
                    {columns.map((column: any, index: number) => (
                      <th key={index} className="px-3 py-2 text-left font-semibold">
                        {labelFrom(column?.label ?? column, '-')}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row: any, rowIndex: number) => {
                    const rowValues = Array.isArray(row?.values)
                      ? row.values
                      : Array.isArray(row?.cells)
                        ? row.cells
                        : Array.isArray(row?.data)
                          ? row.data
                          : [];
                    const byColId = new Map<string, any>();
                    rowValues.forEach((cell: any, cellIndex: number) => {
                      if (!cell || typeof cell !== 'object') {
                        byColId.set(String(cellIndex), cell);
                        return;
                      }
                      const cellColId =
                        cell?.col_id ??
                        cell?.colId ??
                        cell?.tile_id ??
                        cell?.tileId ??
                        cell?.id;
                      if (cellColId !== undefined && cellColId !== null) {
                        byColId.set(String(cellColId), cell);
                      }
                    });
                    return (
                      <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                        <td className="px-3 py-2 font-medium text-slate-800">
                          {labelFrom(row, '-')}
                        </td>
                        {columns.map((column: any, colIndex: number) => {
                          const columnId =
                            column?.id ??
                            column?.col_id ??
                            column?.colId ??
                            column?.tile_id ??
                            column?.tileId ??
                            String(colIndex);
                          const cell = byColId.get(String(columnId)) ?? rowValues[colIndex];
                          const rawValue =
                            cell?.display ??
                            cell?.formatted ??
                            cell?.value ??
                            cell?.label ??
                            cell;
                          const metricRef =
                            cell?.metric_ref ??
                            cell?.metricRef ??
                            column?.metric_ref ??
                            column?.metricRef;
                          return (
                            <td key={colIndex} className="px-3 py-2 text-slate-700">
                              {formatDecisionMetricValue(rawValue, metricRef)}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-5">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Fastest-Change</h3>
              <p className="text-sm text-slate-700">
                {fastestChangeText || '-'}
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Most Likely Wrong</h3>
              {mostLikelyWrong.length > 0 ? (
                <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                  {mostLikelyWrong.map((item: any, index: number) => (
                    <li key={index}>{labelFrom(item)}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500">-</p>
              )}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Question Bank</h3>
              {questionBank.length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(questionGroups).map(([groupKey, items]) => (
                    <div key={groupKey} className="space-y-2">
                      {hasDriverTileId && (
                        <p className="text-xs font-semibold uppercase text-slate-500">
                          driver_tile_id: {groupKey}
                        </p>
                      )}
                      <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                        {(items as any[]).flatMap((item, index) => {
                          const questions = Array.isArray(item?.questions)
                            ? item.questions
                            : [labelFrom(item)];
                          return questions.map((question: any, qIndex: number) => (
                            <li key={`${index}-${qIndex}`}>{labelFrom(question)}</li>
                          ));
                        })}
                      </ul>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">-</p>
              )}
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Red Flags</h3>
                {redFlags.length > 0 ? (
                  <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                    {redFlags.map((item: any, index: number) => (
                      <li key={index}>{labelFrom(item)}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500">-</p>
                )}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Actions</h3>
                {actions.length > 0 ? (
                  <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                    {actions.map((item: any, index: number) => (
                      <li key={index}>{labelFrom(item)}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500">-</p>
                )}
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900">Provenance</h3>
              <span className="text-xs uppercase tracking-wide text-slate-400">Inputs</span>
            </div>
            {scenarioInputs.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full border border-slate-200 text-sm">
                  <thead className="bg-slate-50 text-slate-600">
                    <tr>
                      <th className="px-3 py-2 text-left font-semibold">Scenario</th>
                      <th className="px-3 py-2 text-left font-semibold">Applied Tile IDs</th>
                      <th className="px-3 py-2 text-left font-semibold">Cost Scalar</th>
                      <th className="px-3 py-2 text-left font-semibold">Revenue Scalar</th>
                      <th className="px-3 py-2 text-left font-semibold">Metric Ref</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scenarioInputs.map((input: any, index: number) => {
                      const metricRef =
                        input?.driver?.metric_ref ??
                        input?.driver?.metricRef ??
                        input?.metric_ref ??
                        input?.metricRef;
                      return (
                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                          <td className="px-3 py-2 text-slate-700">
                            {labelFrom(input?.scenario ?? input?.scenario_label ?? input?.label ?? input?.name)}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {listValue(input?.applied_tile_ids ?? input?.appliedTileIds ?? input?.tiles)}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {formatValue(input?.cost_scalar ?? input?.costScalar)}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {formatValue(input?.revenue_scalar ?? input?.revenueScalar)}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {formatValue(metricRef)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-slate-500">-</p>
            )}

            {metricRefsUsed.length > 0 && (
              <div className="mt-4 text-sm text-slate-600">
                <span className="font-medium text-slate-700">metric_refs_used:</span>{' '}
                {listValue(metricRefsUsed)}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};
