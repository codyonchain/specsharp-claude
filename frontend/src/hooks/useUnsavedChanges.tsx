import { useEffect, useCallback, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface UnsavedChangesOptions {
  message?: string;
  enabled?: boolean;
  onNavigationBlocked?: () => void;
}

/**
 * Hook to warn users about unsaved changes when leaving the page
 */
export const useUnsavedChanges = (
  hasChanges: boolean,
  options: UnsavedChangesOptions = {}
) => {
  const {
    message = 'You have unsaved changes. Are you sure you want to leave?',
    enabled = true,
    onNavigationBlocked
  } = options;

  const navigate = useNavigate();
  const location = useLocation();
  const isBlockingRef = useRef(false);

  // Handle browser navigation (back/forward, refresh, close)
  useEffect(() => {
    if (!enabled) return;

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasChanges) {
        e.preventDefault();
        // Chrome requires returnValue to be set
        e.returnValue = message;
        return message;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasChanges, message, enabled]);

  // Handle React Router navigation
  useEffect(() => {
    if (!enabled || !hasChanges) {
      isBlockingRef.current = false;
      return;
    }

    isBlockingRef.current = true;

    // Create a navigation blocker
    const unblock = (callback: () => void) => {
      const confirmNavigation = window.confirm(message);
      if (confirmNavigation) {
        isBlockingRef.current = false;
        callback();
      } else {
        if (onNavigationBlocked) {
          onNavigationBlocked();
        }
      }
    };

    // Override navigate function
    const originalNavigate = navigate;
    const blockedNavigate = (to: any, options?: any) => {
      if (isBlockingRef.current) {
        unblock(() => originalNavigate(to, options));
      } else {
        originalNavigate(to, options);
      }
    };

    // Replace navigate in the component
    Object.assign(navigate, blockedNavigate);

    return () => {
      isBlockingRef.current = false;
      Object.assign(navigate, originalNavigate);
    };
  }, [hasChanges, message, navigate, enabled, onNavigationBlocked]);

  // Provide a way to bypass the warning for intentional navigation
  const navigateWithoutWarning = useCallback((to: string) => {
    isBlockingRef.current = false;
    navigate(to);
  }, [navigate]);

  return {
    navigateWithoutWarning,
    isBlocking: isBlockingRef.current
  };
};

/**
 * Hook for managing navigation with unsaved changes in forms
 */
export const useFormNavigation = (
  hasChanges: boolean,
  onSave?: () => Promise<void>
) => {
  const [showSaveDialog, setShowSaveDialog] = React.useState(false);
  const [pendingNavigation, setPendingNavigation] = React.useState<string | null>(null);
  
  const { navigateWithoutWarning } = useUnsavedChanges(hasChanges, {
    enabled: !showSaveDialog, // Disable when showing custom dialog
    onNavigationBlocked: () => setShowSaveDialog(true)
  });

  const handleSaveAndNavigate = useCallback(async () => {
    if (onSave) {
      try {
        await onSave();
        if (pendingNavigation) {
          navigateWithoutWarning(pendingNavigation);
        }
      } catch (error) {
        console.error('Failed to save:', error);
      }
    }
    setShowSaveDialog(false);
    setPendingNavigation(null);
  }, [onSave, pendingNavigation, navigateWithoutWarning]);

  const handleDiscardAndNavigate = useCallback(() => {
    if (pendingNavigation) {
      navigateWithoutWarning(pendingNavigation);
    }
    setShowSaveDialog(false);
    setPendingNavigation(null);
  }, [pendingNavigation, navigateWithoutWarning]);

  const handleCancelNavigation = useCallback(() => {
    setShowSaveDialog(false);
    setPendingNavigation(null);
  }, []);

  const navigateWithPrompt = useCallback((to: string) => {
    if (hasChanges) {
      setPendingNavigation(to);
      setShowSaveDialog(true);
    } else {
      navigateWithoutWarning(to);
    }
  }, [hasChanges, navigateWithoutWarning]);

  return {
    showSaveDialog,
    navigateWithPrompt,
    handleSaveAndNavigate,
    handleDiscardAndNavigate,
    handleCancelNavigation
  };
};

/**
 * Component for rendering save dialog
 */
export const UnsavedChangesDialog: React.FC<{
  isOpen: boolean;
  onSave: () => void;
  onDiscard: () => void;
  onCancel: () => void;
  title?: string;
  message?: string;
}> = ({
  isOpen,
  onSave,
  onDiscard,
  onCancel,
  title = 'Unsaved Changes',
  message = 'You have unsaved changes. What would you like to do?'
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600 mb-6">{message}</p>
        
        <div className="flex flex-col space-y-3">
          <button
            onClick={onSave}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Save Changes
          </button>
          
          <button
            onClick={onDiscard}
            className="w-full py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
          >
            Discard Changes
          </button>
          
          <button
            onClick={onCancel}
            className="w-full py-2 px-4 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

// Re-export React for the component
import React from 'react';