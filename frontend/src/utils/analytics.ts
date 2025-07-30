/**
 * Simple analytics tracking utility
 * Replace with your actual analytics provider (Google Analytics, Mixpanel, etc.)
 */

interface TrackingEvent {
  event: string;
  properties?: Record<string, any>;
  timestamp?: Date;
}

export const trackEvent = (eventName: string, properties?: Record<string, any>) => {
  const event: TrackingEvent = {
    event: eventName,
    properties,
    timestamp: new Date()
  };

  // Log to console in development
  if (import.meta.env.DEV) {
    console.log('📊 Track Event:', event);
  }

  // Google Analytics (if available)
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', eventName, {
      event_category: 'User Interaction',
      ...properties
    });
  }

  // Mixpanel (if available)
  if (typeof window !== 'undefined' && (window as any).mixpanel) {
    (window as any).mixpanel.track(eventName, properties);
  }

  // Custom analytics endpoint
  // fetch('/api/analytics', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(event)
  // }).catch(() => {});
};

// Specific tracking functions for common events
export const trackCTAClick = (button: string, location: string) => {
  trackEvent('CTA_Clicked', { button, location });
};

export const trackROICalculatorUsed = (savings: number, hoursPerMonth: number) => {
  trackEvent('ROI_Calculator_Used', { 
    savings, 
    hoursPerMonth,
    savingsBracket: savings > 5000 ? 'high' : savings > 2000 ? 'medium' : 'low'
  });
};

export const trackPageView = (page: string) => {
  trackEvent('Page_Viewed', { page, url: window.location.href });
};

export const trackSectionViewed = (section: string) => {
  trackEvent('Section_Viewed', { section });
};

// Set up intersection observer for tracking when sections come into view
export const setupViewTracking = () => {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const section = entry.target.getAttribute('data-track-section');
          if (section) {
            trackSectionViewed(section);
            observer.unobserve(entry.target);
          }
        }
      });
    },
    { threshold: 0.5 }
  );

  // Track all elements with data-track-section attribute
  document.querySelectorAll('[data-track-section]').forEach(el => {
    observer.observe(el);
  });
};