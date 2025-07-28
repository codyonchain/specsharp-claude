import { useEffect, useCallback } from 'react';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  metaKey?: boolean;
  action: () => void;
  description: string;
  enabled?: boolean;
}

interface UseKeyboardShortcutsOptions {
  shortcuts: KeyboardShortcut[];
  enabled?: boolean;
}

export const useKeyboardShortcuts = ({ 
  shortcuts, 
  enabled = true 
}: UseKeyboardShortcutsOptions) => {
  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    // Find matching shortcut
    const matchingShortcut = shortcuts.find(shortcut => {
      if (shortcut.enabled === false) return false;
      
      const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
      const ctrlMatch = shortcut.ctrlKey ? (event.ctrlKey || event.metaKey) : true;
      const shiftMatch = shortcut.shiftKey ? event.shiftKey : !event.shiftKey;
      const altMatch = shortcut.altKey ? event.altKey : !event.altKey;
      
      return keyMatch && ctrlMatch && shiftMatch && altMatch;
    });

    if (matchingShortcut) {
      event.preventDefault();
      matchingShortcut.action();
    }
  }, [shortcuts, enabled]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  // Return shortcuts for display in help menu
  return shortcuts.filter(s => s.enabled !== false);
};

// Common shortcuts for SpecSharp
export const useProjectShortcuts = ({
  onSave,
  onDuplicate,
  onNew,
  onExport,
  onPrint,
  onSearch,
  onHelp,
  enabled = true
}: {
  onSave?: () => void;
  onDuplicate?: () => void;
  onNew?: () => void;
  onExport?: () => void;
  onPrint?: () => void;
  onSearch?: () => void;
  onHelp?: () => void;
  enabled?: boolean;
}) => {
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 's',
      ctrlKey: true,
      action: onSave || (() => {}),
      description: 'Save project',
      enabled: !!onSave
    },
    {
      key: 'd',
      ctrlKey: true,
      action: onDuplicate || (() => {}),
      description: 'Duplicate project',
      enabled: !!onDuplicate
    },
    {
      key: 'n',
      ctrlKey: true,
      action: onNew || (() => {}),
      description: 'New project',
      enabled: !!onNew
    },
    {
      key: 'e',
      ctrlKey: true,
      action: onExport || (() => {}),
      description: 'Export to Excel',
      enabled: !!onExport
    },
    {
      key: 'p',
      ctrlKey: true,
      action: onPrint || (() => {}),
      description: 'Print/PDF',
      enabled: !!onPrint
    },
    {
      key: 'k',
      ctrlKey: true,
      action: onSearch || (() => {}),
      description: 'Search projects',
      enabled: !!onSearch
    },
    {
      key: '?',
      shiftKey: true,
      action: onHelp || (() => {}),
      description: 'Show help',
      enabled: !!onHelp
    }
  ];

  return useKeyboardShortcuts({ shortcuts, enabled });
};

// Navigation shortcuts
export const useNavigationShortcuts = ({
  onNext,
  onPrevious,
  onClose,
  enabled = true
}: {
  onNext?: () => void;
  onPrevious?: () => void;
  onClose?: () => void;
  enabled?: boolean;
}) => {
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'ArrowRight',
      altKey: true,
      action: onNext || (() => {}),
      description: 'Next item',
      enabled: !!onNext
    },
    {
      key: 'ArrowLeft',
      altKey: true,
      action: onPrevious || (() => {}),
      description: 'Previous item',
      enabled: !!onPrevious
    },
    {
      key: 'Escape',
      action: onClose || (() => {}),
      description: 'Close/Cancel',
      enabled: !!onClose
    }
  ];

  return useKeyboardShortcuts({ shortcuts, enabled });
};

// Form shortcuts
export const useFormShortcuts = ({
  onSubmit,
  onReset,
  onCancel,
  enabled = true
}: {
  onSubmit?: () => void;
  onReset?: () => void;
  onCancel?: () => void;
  enabled?: boolean;
}) => {
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'Enter',
      ctrlKey: true,
      action: onSubmit || (() => {}),
      description: 'Submit form',
      enabled: !!onSubmit
    },
    {
      key: 'r',
      ctrlKey: true,
      shiftKey: true,
      action: onReset || (() => {}),
      description: 'Reset form',
      enabled: !!onReset
    },
    {
      key: 'Escape',
      action: onCancel || (() => {}),
      description: 'Cancel',
      enabled: !!onCancel
    }
  ];

  return useKeyboardShortcuts({ shortcuts, enabled });
};