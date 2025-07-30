import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Mail } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Generate a unique error ID for support reference
    const errorId = `ERR-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      hasError: true,
      error,
      errorInfo: null,
      errorId
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to console in development
    if (import.meta.env.DEV) {
      console.error('Error caught by boundary:', error, errorInfo);
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log to error reporting service (e.g., Sentry)
    if (typeof window !== 'undefined' && (window as any).Sentry) {
      (window as any).Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        },
        tags: {
          errorBoundary: true,
          errorId: this.state.errorId
        }
      });
    }

    // Update state with error info
    this.setState({
      errorInfo
    });

    // Save error details to localStorage for recovery
    this.saveErrorToLocalStorage(error, errorInfo);
  }

  saveErrorToLocalStorage(error: Error, errorInfo: ErrorInfo) {
    try {
      const errorData = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        errorId: this.state.errorId,
        url: window.location.href,
        userAgent: navigator.userAgent
      };

      const existingErrors = JSON.parse(
        localStorage.getItem('specsharp_errors') || '[]'
      );
      
      // Keep only last 10 errors
      const updatedErrors = [errorData, ...existingErrors].slice(0, 10);
      localStorage.setItem('specsharp_errors', JSON.stringify(updatedErrors));
    } catch (e) {
      console.error('Failed to save error to localStorage:', e);
    }
  }

  handleReset = () => {
    // Clear error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleReportError = () => {
    const { error, errorId } = this.state;
    const subject = encodeURIComponent(`Error Report - ${errorId}`);
    const body = encodeURIComponent(
      `Error ID: ${errorId}\n\nError Message: ${error?.message}\n\nURL: ${window.location.href}\n\nPlease describe what you were doing when the error occurred:\n\n`
    );
    window.location.href = `mailto:support@specsharp.com?subject=${subject}&body=${body}`;
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return <>{this.props.fallback}</>;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            
            <h1 className="text-xl font-semibold text-center text-gray-900 mb-2">
              Oops! Something went wrong
            </h1>
            
            <p className="text-gray-600 text-center mb-6">
              Don't worry - your work has been saved. You can safely refresh the page to continue.
            </p>

            {import.meta.env.DEV && this.state.error && (
              <div className="mb-4 p-3 bg-gray-100 rounded text-xs font-mono overflow-auto max-h-32">
                <p className="font-semibold mb-1">Error: {this.state.error.message}</p>
                <p className="text-gray-600 whitespace-pre-wrap">
                  {this.state.error.stack}
                </p>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Page
              </button>
              
              <button
                onClick={this.handleGoHome}
                className="w-full flex items-center justify-center px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                <Home className="w-4 h-4 mr-2" />
                Go to Dashboard
              </button>
              
              <button
                onClick={this.handleReportError}
                className="w-full flex items-center justify-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors text-sm"
              >
                <Mail className="w-4 h-4 mr-2" />
                Report this error
              </button>
            </div>

            <p className="text-xs text-gray-500 text-center mt-4">
              Error ID: {this.state.errorId}
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Hook to catch errors in async operations
 */
export const useAsyncError = () => {
  const [, setError] = React.useState();
  
  return React.useCallback(
    (error: Error) => {
      setError(() => {
        throw error;
      });
    },
    [setError]
  );
};

/**
 * Wrapper component with error boundary
 */
export const WithErrorBoundary: React.FC<{
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}> = ({ children, fallback, onError }) => {
  return (
    <ErrorBoundary fallback={fallback} onError={onError}>
      {children}
    </ErrorBoundary>
  );
};

/**
 * Error recovery component for forms
 */
export const FormErrorRecovery: React.FC<{
  onRecover: () => void;
  onReset: () => void;
}> = ({ onRecover, onReset }) => {
  return (
    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div className="flex items-start">
        <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-yellow-800">
            We saved your work!
          </h3>
          <p className="text-sm text-yellow-700 mt-1">
            An error occurred, but we've saved your progress. You can recover your work or start fresh.
          </p>
          <div className="mt-3 flex space-x-3">
            <button
              onClick={onRecover}
              className="text-sm font-medium text-yellow-800 hover:text-yellow-900"
            >
              Recover my work
            </button>
            <button
              onClick={onReset}
              className="text-sm font-medium text-gray-600 hover:text-gray-700"
            >
              Start fresh
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};