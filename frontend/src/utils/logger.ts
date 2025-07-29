// Vite uses import.meta.env, not process.env
const isDevelopment = import.meta.env.MODE === 'development';

interface Logger {
  log: (...args: any[]) => void;
  error: (...args: any[]) => void;
  warn: (...args: any[]) => void;
  info: (...args: any[]) => void;
  debug: (...args: any[]) => void;
}

// Always allow errors to be logged
export const logger: Logger = {
  log: (...args) => isDevelopment && console.log(...args),
  error: (...args) => console.error(...args),  // Always log errors
  warn: (...args) => console.warn(...args),    // Always log warnings
  info: (...args) => isDevelopment && console.info(...args),
  debug: (...args) => isDevelopment && console.debug(...args),
};
