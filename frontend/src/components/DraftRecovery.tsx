import React from 'react';
import { FileText, Clock, AlertCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface DraftRecoveryProps {
  isOpen: boolean;
  lastSavedTime: Date | null;
  onRecover: () => void;
  onDiscard: () => void;
  draftName?: string;
}

export const DraftRecovery: React.FC<DraftRecoveryProps> = ({
  isOpen,
  lastSavedTime,
  onRecover,
  onDiscard,
  draftName = 'form'
}) => {
  if (!isOpen || !lastSavedTime) return null;

  const timeAgo = formatDistanceToNow(lastSavedTime, { addSuffix: true });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 overflow-hidden">
        <div className="bg-blue-50 px-6 py-4 border-b border-blue-100">
          <div className="flex items-center">
            <FileText className="w-5 h-5 text-blue-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">
              Unsaved Draft Found
            </h2>
          </div>
        </div>
        
        <div className="p-6">
          <div className="flex items-start mb-4">
            <Clock className="w-5 h-5 text-gray-400 mt-0.5 mr-3" />
            <div>
              <p className="text-gray-700">
                We found an unsaved {draftName} from {timeAgo}.
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Would you like to continue where you left off?
              </p>
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onRecover}
              className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Recover Draft
            </button>
            
            <button
              onClick={onDiscard}
              className="flex-1 py-2 px-4 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Start Fresh
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Inline draft status indicator
 */
export const DraftStatus: React.FC<{
  lastSavedTime: Date | null;
  isSaving?: boolean;
  hasError?: boolean;
}> = ({ lastSavedTime, isSaving = false, hasError = false }) => {
  if (hasError) {
    return (
      <div className="flex items-center text-sm text-red-600">
        <AlertCircle className="w-4 h-4 mr-1" />
        <span>Failed to save</span>
      </div>
    );
  }

  if (isSaving) {
    return (
      <div className="flex items-center text-sm text-gray-500">
        <div className="w-4 h-4 mr-1">
          <svg className="animate-spin" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
        <span>Saving...</span>
      </div>
    );
  }

  if (!lastSavedTime) {
    return null;
  }

  const timeAgo = formatDistanceToNow(lastSavedTime, { addSuffix: true });

  return (
    <div className="flex items-center text-sm text-gray-500">
      <Clock className="w-4 h-4 mr-1" />
      <span>Saved {timeAgo}</span>
    </div>
  );
};

/**
 * Autosave indicator with animation
 */
export const AutosaveIndicator: React.FC<{
  enabled: boolean;
  interval: number;
  lastSavedTime: Date | null;
}> = ({ enabled, interval, lastSavedTime }) => {
  const [showPulse, setShowPulse] = React.useState(false);

  React.useEffect(() => {
    if (!enabled) return;

    const pulseInterval = setInterval(() => {
      setShowPulse(true);
      setTimeout(() => setShowPulse(false), 1000);
    }, interval);

    return () => clearInterval(pulseInterval);
  }, [enabled, interval]);

  if (!enabled) {
    return (
      <div className="flex items-center text-sm text-gray-400">
        <span>Autosave disabled</span>
      </div>
    );
  }

  return (
    <div className="flex items-center text-sm text-gray-500">
      <div className={`w-2 h-2 rounded-full mr-2 ${
        showPulse ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
      }`} />
      <span>
        Autosave enabled • Every {Math.floor(interval / 1000)}s
        {lastSavedTime && ` • Last saved ${formatDistanceToNow(lastSavedTime, { addSuffix: true })}`}
      </span>
    </div>
  );
};