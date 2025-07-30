const isDevelopment = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;

export const logger = {
  log: (...args: any[]) => {
    if (!isProduction || import.meta.env.VITE_ENABLE_LOGGING === 'true') {
      console.log('[LOG]', new Date().toISOString(), ...args);
    }
  },
  error: (...args: any[]) => {
    console.error('[ERROR]', new Date().toISOString(), ...args);
    // In production, you might want to send errors to a logging service
    if (isProduction && typeof window !== 'undefined') {
      // Example: Send to error tracking service
      // window.Sentry?.captureException(args[0]);
    }
  },
  warn: (...args: any[]) => {
    if (!isProduction || import.meta.env.VITE_ENABLE_LOGGING === 'true') {
      console.warn('[WARN]', new Date().toISOString(), ...args);
    }
  },
  info: (...args: any[]) => {
    if (!isProduction || import.meta.env.VITE_ENABLE_LOGGING === 'true') {
      console.info('[INFO]', new Date().toISOString(), ...args);
    }
  },
  debug: (...args: any[]) => {
    if (isDevelopment) {
      console.debug('[DEBUG]', new Date().toISOString(), ...args);
    }
  },
};