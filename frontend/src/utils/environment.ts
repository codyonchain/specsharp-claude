class EnvironmentChecker {
  static getEnvironment(): 'development' | 'production' {
    return import.meta.env.MODE as 'development' | 'production';
  }

  static isTestingMode(): boolean {
    return import.meta.env.VITE_TESTING === 'true';
  }

  static getApiUrl(): string {
    return import.meta.env.VITE_API_URL || 
           (this.getEnvironment() === 'development' 
            ? 'http://localhost:8001' 
            : window.location.origin + '/api');
  }

  static logStartupConfig(): void {
    const env = this.getEnvironment();
    const isTesting = this.isTestingMode();
    const apiUrl = this.getApiUrl();

    console.group('%c🚀 SpecSharp Frontend Starting', 'color: #2563eb; font-weight: bold');
    console.log(`Environment: ${env}`);
    console.log(`Testing Mode: ${isTesting}`);
    console.log(`API URL: ${apiUrl}`);
    
    if (env === 'development' && isTesting) {
      console.warn('⚠️ Auth bypass enabled - Dev mode only');
    }
    
    if (env === 'production' && isTesting) {
      console.error('🚨 CRITICAL: Testing mode enabled in production!');
    }
    
    // Log available environment variables (safe ones only)
    if (env === 'development') {
      console.log('Available env vars:', {
        MODE: import.meta.env.MODE,
        DEV: import.meta.env.DEV,
        PROD: import.meta.env.PROD,
        BASE_URL: import.meta.env.BASE_URL,
      });
    }
    
    console.groupEnd();
  }

  static validateConfig(): boolean {
    const env = this.getEnvironment();
    
    if (env === 'production') {
      // Check critical production requirements
      if (this.isTestingMode()) {
        console.error('Testing mode must be disabled in production!');
        return false;
      }
      
      if (!import.meta.env.VITE_API_URL) {
        console.error('API URL must be configured for production!');
        return false;
      }
      
      // Verify API URL is HTTPS in production
      const apiUrl = this.getApiUrl();
      if (!apiUrl.startsWith('https://') && !apiUrl.startsWith('/')) {
        console.error('Production API URL must use HTTPS!');
        return false;
      }
    }
    
    return true;
  }

  static getGoogleClientId(): string | undefined {
    return import.meta.env.VITE_GOOGLE_CLIENT_ID;
  }

  static isOAuthConfigured(): boolean {
    return !!this.getGoogleClientId();
  }

  static shouldUseAuthBypass(): boolean {
    // Only allow auth bypass in development with testing mode
    return this.getEnvironment() === 'development' && this.isTestingMode();
  }
}

export default EnvironmentChecker;