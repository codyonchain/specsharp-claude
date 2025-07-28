import React from 'react';
import { X, Command } from 'lucide-react';

interface ShortcutItem {
  keys: string[];
  description: string;
  category: string;
}

interface KeyboardShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
}

export const KeyboardShortcutsHelp: React.FC<KeyboardShortcutsHelpProps> = ({
  isOpen,
  onClose
}) => {
  if (!isOpen) return null;

  const shortcuts: ShortcutItem[] = [
    // Project Management
    { keys: ['Ctrl', 'S'], description: 'Save project', category: 'Project' },
    { keys: ['Ctrl', 'D'], description: 'Duplicate project', category: 'Project' },
    { keys: ['Ctrl', 'N'], description: 'New project', category: 'Project' },
    { keys: ['Ctrl', 'E'], description: 'Export to Excel', category: 'Project' },
    { keys: ['Ctrl', 'P'], description: 'Print/Generate PDF', category: 'Project' },
    
    // Navigation
    { keys: ['Alt', '→'], description: 'Next item', category: 'Navigation' },
    { keys: ['Alt', '←'], description: 'Previous item', category: 'Navigation' },
    { keys: ['Esc'], description: 'Close dialog/Cancel', category: 'Navigation' },
    { keys: ['Ctrl', 'K'], description: 'Search projects', category: 'Navigation' },
    
    // Forms
    { keys: ['Ctrl', 'Enter'], description: 'Submit form', category: 'Forms' },
    { keys: ['Ctrl', 'Shift', 'R'], description: 'Reset form', category: 'Forms' },
    
    // Help
    { keys: ['?'], description: 'Show this help', category: 'Help' },
  ];

  const categories = [...new Set(shortcuts.map(s => s.category))];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-800">Keyboard Shortcuts</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="px-6 py-4 overflow-y-auto max-h-[calc(80vh-120px)]">
          <div className="text-sm text-gray-600 mb-4 flex items-center">
            <Command className="w-4 h-4 mr-1" />
            <span>On Mac, use ⌘ instead of Ctrl</span>
          </div>
          
          {categories.map(category => (
            <div key={category} className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3">
                {category}
              </h3>
              <div className="space-y-2">
                {shortcuts
                  .filter(s => s.category === category)
                  .map((shortcut, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50"
                    >
                      <span className="text-gray-700">{shortcut.description}</span>
                      <div className="flex items-center space-x-1">
                        {shortcut.keys.map((key, keyIndex) => (
                          <React.Fragment key={keyIndex}>
                            {keyIndex > 0 && <span className="text-gray-400">+</span>}
                            <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-300 rounded">
                              {key}
                            </kbd>
                          </React.Fragment>
                        ))}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
          
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">Pro Tips</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Use keyboard shortcuts to speed up your workflow</li>
              <li>• Combine shortcuts for maximum efficiency</li>
              <li>• Press ? anytime to see this help dialog</li>
            </ul>
          </div>
        </div>
        
        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full py-2 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

// Inline keyboard shortcut indicator
export const KeyboardShortcut: React.FC<{
  keys: string[];
  className?: string;
}> = ({ keys, className = '' }) => {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  
  const formatKey = (key: string) => {
    if (key === 'Ctrl' && isMac) return '⌘';
    if (key === 'Alt' && isMac) return '⌥';
    if (key === 'Shift' && isMac) return '⇧';
    return key;
  };
  
  return (
    <span className={`inline-flex items-center space-x-0.5 text-xs ${className}`}>
      {keys.map((key, index) => (
        <React.Fragment key={index}>
          {index > 0 && <span className="text-gray-400">+</span>}
          <kbd className="px-1.5 py-0.5 font-semibold text-gray-600 bg-gray-100 border border-gray-300 rounded text-xs">
            {formatKey(key)}
          </kbd>
        </React.Fragment>
      ))}
    </span>
  );
};