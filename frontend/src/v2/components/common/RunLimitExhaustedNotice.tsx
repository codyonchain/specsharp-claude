import React from 'react';

const RUN_LIMIT_MAILTO =
  'mailto:cody@specsharp.ai?subject=SpecSharp%20Run%20Limit%20Request';

interface RunLimitExhaustedNoticeProps {
  variant?: 'inline' | 'modal';
  open?: boolean;
  onClose?: () => void;
}

const RunLimitExhaustedContent: React.FC<{ titleId?: string }> = ({ titleId }) => (
  <div className="space-y-3">
    <div className="space-y-2">
      <h3 id={titleId} className="text-lg font-semibold text-slate-900">
        You&apos;ve used all included runs
      </h3>
      <p className="text-sm leading-6 text-slate-600">
        This org has used all included runs for Decision Packet generation. You can
        still analyze drafts and review existing work.
      </p>
    </div>
    <a
      href={RUN_LIMIT_MAILTO}
      className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
    >
      Email Cody to add more runs
    </a>
  </div>
);

export const RunLimitExhaustedNotice: React.FC<RunLimitExhaustedNoticeProps> = ({
  variant = 'inline',
  open = true,
  onClose,
}) => {
  if (variant === 'modal') {
    if (!open) return null;

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4">
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="run-limit-exhausted-title"
          className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <RunLimitExhaustedContent titleId="run-limit-exhausted-title" />
            </div>
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="rounded-md p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                aria-label="Close run limit notice"
              >
                ×
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-4">
      <RunLimitExhaustedContent />
    </div>
  );
};

export default RunLimitExhaustedNotice;
