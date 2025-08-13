import React from 'react';
import { cn } from '../lib/utils';
import { Building2, Heart } from 'lucide-react';

interface ViewToggleProps {
  currentView: 'trade' | 'healthcare';
  onViewChange: (view: 'trade' | 'healthcare') => void;
  className?: string;
}

export const ViewToggle: React.FC<ViewToggleProps> = ({ 
  currentView, 
  onViewChange, 
  className 
}) => {
  return (
    <div className={cn("inline-flex items-center rounded-lg bg-muted p-1", className)}>
      <button
        onClick={() => onViewChange('trade')}
        className={cn(
          "inline-flex items-center justify-center rounded-md px-3 py-1.5 text-sm font-medium transition-all",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          currentView === 'trade'
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        <Building2 className="mr-2 h-4 w-4" />
        Trade Breakdown
      </button>
      <button
        onClick={() => onViewChange('healthcare')}
        className={cn(
          "inline-flex items-center justify-center rounded-md px-3 py-1.5 text-sm font-medium transition-all",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          currentView === 'healthcare'
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground"
        )}
      >
        <Heart className="mr-2 h-4 w-4" />
        Healthcare View
      </button>
    </div>
  );
};