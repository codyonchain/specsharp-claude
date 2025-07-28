import { useEffect } from 'react';

/**
 * Hook for smooth scrolling to anchor links
 */
export const useSmoothScroll = () => {
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const link = target.closest('a');
      
      if (!link) return;
      
      const href = link.getAttribute('href');
      if (!href || !href.startsWith('#')) return;
      
      e.preventDefault();
      
      const targetId = href.substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        
        // Update URL without triggering scroll
        window.history.pushState({}, '', href);
      }
    };

    document.addEventListener('click', handleClick);
    
    return () => {
      document.removeEventListener('click', handleClick);
    };
  }, []);
};

/**
 * Hook for scroll-triggered animations
 */
export const useScrollAnimation = (threshold = 0.1) => {
  useEffect(() => {
    const observerOptions = {
      threshold,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe all elements with data-animate attribute
    const elements = document.querySelectorAll('[data-animate]');
    elements.forEach(el => observer.observe(el));

    return () => {
      elements.forEach(el => observer.unobserve(el));
    };
  }, [threshold]);
};

/**
 * Hook for parallax scrolling effects
 */
export const useParallax = (speed = 0.5) => {
  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.pageYOffset;
      const parallaxElements = document.querySelectorAll('[data-parallax]');
      
      parallaxElements.forEach(element => {
        const elementSpeed = parseFloat(element.getAttribute('data-parallax') || `${speed}`);
        const yPos = -(scrolled * elementSpeed);
        
        (element as HTMLElement).style.transform = `translateY(${yPos}px)`;
      });
    };

    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [speed]);
};

/**
 * Hook for scroll progress indicator
 */
export const useScrollProgress = () => {
  useEffect(() => {
    const progressBar = document.getElementById('scroll-progress');
    if (!progressBar) return;

    const updateProgress = () => {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight - windowHeight;
      const scrolled = window.scrollY;
      const progress = (scrolled / documentHeight) * 100;
      
      (progressBar as HTMLElement).style.width = `${progress}%`;
    };

    window.addEventListener('scroll', updateProgress);
    updateProgress(); // Initial call
    
    return () => {
      window.removeEventListener('scroll', updateProgress);
    };
  }, []);
};