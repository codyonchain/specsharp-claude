import { useEffect, useRef, useCallback } from 'react';
import { toast } from 'react-toastify';

interface AutosaveOptions {
  interval?: number;
  key?: string;
  onSave?: (data: any) => Promise<void>;
  onError?: (error: Error) => void;
  showNotification?: boolean;
  debounceDelay?: number;
}

/**
 * Hook for autosaving data at regular intervals
 */
export const useAutosave = <T extends object>(
  data: T | null,
  hasChanges: boolean,
  options: AutosaveOptions = {}
) => {
  const {
    interval = 30000, // 30 seconds default
    key = 'autosave_draft',
    onSave,
    onError,
    showNotification = true,
    debounceDelay = 1000
  } = options;

  const lastSavedRef = useRef<string>('');
  const saveTimeoutRef = useRef<NodeJS.Timeout>();
  const isSavingRef = useRef(false);

  // Save to localStorage
  const saveToLocalStorage = useCallback((dataToSave: T) => {
    try {
      const serialized = JSON.stringify({
        data: dataToSave,
        timestamp: new Date().toISOString(),
        version: '1.0'
      });
      
      localStorage.setItem(key, serialized);
      lastSavedRef.current = serialized;
      
      if (showNotification) {
        toast.info('Draft saved', { 
          autoClose: 1000,
          hideProgressBar: true,
          position: 'bottom-right'
        });
      }
    } catch (error) {
      console.error('Failed to save draft:', error);
      if (onError) {
        onError(error as Error);
      }
    }
  }, [key, showNotification, onError]);

  // Save to backend if onSave provided
  const saveToBackend = useCallback(async (dataToSave: T) => {
    if (!onSave || isSavingRef.current) return;
    
    isSavingRef.current = true;
    try {
      await onSave(dataToSave);
      lastSavedRef.current = JSON.stringify(dataToSave);
      
      if (showNotification) {
        toast.success('Changes saved', { 
          autoClose: 1000,
          hideProgressBar: true,
          position: 'bottom-right'
        });
      }
    } catch (error) {
      console.error('Failed to save to backend:', error);
      // Fall back to localStorage
      saveToLocalStorage(dataToSave);
      
      if (onError) {
        onError(error as Error);
      } else if (showNotification) {
        toast.warning('Saved locally. Will sync when online.', {
          autoClose: 3000,
          position: 'bottom-right'
        });
      }
    } finally {
      isSavingRef.current = false;
    }
  }, [onSave, onError, showNotification, saveToLocalStorage]);

  // Debounced save function
  const debouncedSave = useCallback((dataToSave: T) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    
    saveTimeoutRef.current = setTimeout(() => {
      if (onSave) {
        saveToBackend(dataToSave);
      } else {
        saveToLocalStorage(dataToSave);
      }
    }, debounceDelay);
  }, [debounceDelay, onSave, saveToBackend, saveToLocalStorage]);

  // Set up interval-based autosave
  useEffect(() => {
    if (!data || !hasChanges) return;

    const intervalId = setInterval(() => {
      const currentData = JSON.stringify(data);
      if (currentData !== lastSavedRef.current && hasChanges) {
        if (onSave) {
          saveToBackend(data);
        } else {
          saveToLocalStorage(data);
        }
      }
    }, interval);

    return () => {
      clearInterval(intervalId);
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [data, hasChanges, interval, onSave, saveToBackend, saveToLocalStorage]);

  // Save on immediate change (debounced)
  useEffect(() => {
    if (!data || !hasChanges) return;
    
    debouncedSave(data);
  }, [data, hasChanges, debouncedSave]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  // Manual save function
  const manualSave = useCallback(async () => {
    if (!data) return;
    
    if (onSave) {
      await saveToBackend(data);
    } else {
      saveToLocalStorage(data);
    }
  }, [data, onSave, saveToBackend, saveToLocalStorage]);

  // Load draft function
  const loadDraft = useCallback((): T | null => {
    try {
      const saved = localStorage.getItem(key);
      if (saved) {
        const parsed = JSON.parse(saved);
        return parsed.data;
      }
    } catch (error) {
      console.error('Failed to load draft:', error);
    }
    return null;
  }, [key]);

  // Clear draft function
  const clearDraft = useCallback(() => {
    localStorage.removeItem(key);
    lastSavedRef.current = '';
  }, [key]);

  // Get last saved timestamp
  const getLastSavedTime = useCallback((): Date | null => {
    try {
      const saved = localStorage.getItem(key);
      if (saved) {
        const parsed = JSON.parse(saved);
        return new Date(parsed.timestamp);
      }
    } catch (error) {
      console.error('Failed to get last saved time:', error);
    }
    return null;
  }, [key]);

  return {
    manualSave,
    loadDraft,
    clearDraft,
    getLastSavedTime,
    isSaving: isSavingRef.current
  };
};

/**
 * Hook for managing form drafts with recovery
 */
export const useFormDraft = <T extends object>(
  formId: string,
  initialData?: T
) => {
  const [formData, setFormData] = React.useState<T | null>(null);
  const [hasChanges, setHasChanges] = React.useState(false);
  const [showRecoveryPrompt, setShowRecoveryPrompt] = React.useState(false);
  
  const key = `form_draft_${formId}`;
  
  // Check for existing draft on mount
  useEffect(() => {
    const draft = loadDraft();
    if (draft && !formData) {
      setShowRecoveryPrompt(true);
    } else if (!formData && initialData) {
      setFormData(initialData);
    }
  }, []);

  const { 
    manualSave, 
    loadDraft, 
    clearDraft,
    getLastSavedTime 
  } = useAutosave(formData, hasChanges, { 
    key,
    showNotification: false 
  });

  const updateFormData = useCallback((updates: Partial<T>) => {
    setFormData(prev => {
      if (!prev) return updates as T;
      return { ...prev, ...updates };
    });
    setHasChanges(true);
  }, []);

  const recoverDraft = useCallback(() => {
    const draft = loadDraft();
    if (draft) {
      setFormData(draft);
      setHasChanges(false);
      toast.success('Draft recovered', { autoClose: 2000 });
    }
    setShowRecoveryPrompt(false);
  }, [loadDraft]);

  const discardDraft = useCallback(() => {
    clearDraft();
    if (initialData) {
      setFormData(initialData);
    }
    setHasChanges(false);
    setShowRecoveryPrompt(false);
  }, [clearDraft, initialData]);

  const resetForm = useCallback(() => {
    if (initialData) {
      setFormData(initialData);
    } else {
      setFormData(null);
    }
    setHasChanges(false);
    clearDraft();
  }, [initialData, clearDraft]);

  const submitForm = useCallback(() => {
    clearDraft();
    setHasChanges(false);
  }, [clearDraft]);

  return {
    formData,
    updateFormData,
    hasChanges,
    resetForm,
    submitForm,
    showRecoveryPrompt,
    recoverDraft,
    discardDraft,
    lastSavedTime: getLastSavedTime()
  };
};

// Re-export React for the component that imports this
import React from 'react';