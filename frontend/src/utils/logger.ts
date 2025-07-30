const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = {
  log: (...args: any[]) => isDevelopment && console.log(...args),
  error: (...args: any[]) => isDevelopment && console.error(...args),
  warn: (...args: any[]) => isDevelopment && console.warn(...args),
  info: (...args: any[]) => isDevelopment && console.info(...args),
  debug: (...args: any[]) => isDevelopment && console.debug(...args),
};