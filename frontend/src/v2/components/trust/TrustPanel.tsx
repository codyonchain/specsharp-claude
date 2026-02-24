import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { trustNarrative } from '@/content/trustNarrative';

interface TrustPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialSectionId?: string;
}

export const TrustPanel: React.FC<TrustPanelProps> = ({ open, onOpenChange, initialSectionId }) => {
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const lastActiveElementRef = useRef<HTMLElement | null>(null);

  const sections = useMemo(() => (Array.isArray(trustNarrative?.sections) ? trustNarrative.sections : []), []);

  const scrollToSection = useCallback((sectionId: string, behavior: ScrollBehavior = 'smooth') => {
    const element = document.getElementById(`trust-${sectionId}`);
    if (element) {
      element.scrollIntoView({ behavior, block: 'start' });
    }
  }, []);

  const resolveInitialSectionId = useCallback(() => {
    if (!sections.length) return undefined;
    if (initialSectionId && sections.some(section => section.id === initialSectionId)) {
      return initialSectionId;
    }
    return sections[0].id;
  }, [initialSectionId, sections]);

  const [activeSectionId, setActiveSectionId] = useState<string | undefined>(() => resolveInitialSectionId());

  const handleClose = useCallback(() => {
    onOpenChange(false);
  }, [onOpenChange]);

  useEffect(() => () => {
    document.body.style.overflow = '';
  }, []);

  useEffect(() => {
    if (!open) {
      document.body.style.overflow = '';
      lastActiveElementRef.current?.focus?.();
      return;
    }

    document.body.style.overflow = 'hidden';
    lastActiveElementRef.current = document.activeElement as HTMLElement | null;

    const targetSectionId = resolveInitialSectionId();
    if (targetSectionId) {
      setActiveSectionId(targetSectionId);
      requestAnimationFrame(() => scrollToSection(targetSectionId, 'auto'));
    }

    requestAnimationFrame(() => closeButtonRef.current?.focus());

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        handleClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleClose, open, resolveInitialSectionId, scrollToSection]);

  const updateActiveSectionFromScroll = useCallback(() => {
    if (!sections.length) return;

    const container = scrollContainerRef.current;
    if (!container) return;

    const containerTop = container.getBoundingClientRect().top + 24;
    let closestSectionId = sections[0].id;
    let smallestDistance = Number.POSITIVE_INFINITY;

    sections.forEach(section => {
      const element = document.getElementById(`trust-${section.id}`);
      if (!element) return;
      const distance = Math.abs(element.getBoundingClientRect().top - containerTop);
      if (distance < smallestDistance) {
        smallestDistance = distance;
        closestSectionId = section.id;
      }
    });

    setActiveSectionId(prev => (prev === closestSectionId ? prev : closestSectionId));
  }, [sections]);

  useEffect(() => {
    if (!open) return;
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleScroll = () => updateActiveSectionFromScroll();
    container.addEventListener('scroll', handleScroll);
    updateActiveSectionFromScroll();

    return () => {
      container.removeEventListener('scroll', handleScroll);
    };
  }, [open, updateActiveSectionFromScroll]);

  const handleLensClick = (sectionId: string) => {
    setActiveSectionId(sectionId);
    scrollToSection(sectionId);
  };

  const hasNarrative = sections.length > 0;

  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/40 transition-opacity ${open ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={handleClose}
      />
      <aside
        aria-label="Trust panel"
        role="dialog"
        aria-modal="true"
        className={`fixed right-0 top-0 z-50 h-screen w-[560px] max-w-[92vw] bg-white shadow-2xl transition-transform duration-200 ease-out ${
          open ? 'translate-x-0' : 'translate-x-full pointer-events-none'
        }`}
      >
        <div className="relative flex h-full flex-col">
          <button
            ref={closeButtonRef}
            type="button"
            aria-label="Close trust panel"
            onClick={handleClose}
            className="absolute right-4 top-4 inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-500"
          >
            <XIcon />
          </button>
          <div className="sticky top-0 z-10 border-b border-slate-200 bg-white p-5 pb-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-500">Trust &amp; Assumptions</p>
            <h2 className="mt-2 text-2xl font-bold text-slate-900">{trustNarrative?.title ?? 'How to interpret this output'}</h2>
            {trustNarrative?.intro && <p className="mt-2 text-sm text-slate-600">{trustNarrative.intro}</p>}
            <div className="mt-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Interpretation lenses</p>
              <div className="mt-2 flex flex-wrap gap-2 pr-8">
                {sections.map(section => {
                  const isActive = section.id === activeSectionId;
                  return (
                    <button
                      key={section.id}
                      type="button"
                      onClick={() => handleLensClick(section.id)}
                      className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                        isActive
                          ? 'border-slate-900 bg-slate-900 text-white'
                          : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      {section.title}
                    </button>
                  );
                })}
                {!hasNarrative && <p className="text-xs text-amber-600">Trust narrative not available.</p>}
              </div>
            </div>
          </div>
          <div ref={scrollContainerRef} className="h-[calc(100vh-240px)] flex-1 overflow-y-auto p-5 pt-4">
            {sections.map(section => (
              <section key={section.id} id={`trust-${section.id}`} data-trust-section={section.id} className="py-4 scroll-mt-24">
                <h3 className="text-base font-semibold text-slate-900">{section.title}</h3>
                <div className="mt-2 space-y-3">
                  {section.bodyParagraphs.map((paragraph, index) => (
                    <p key={index} className="text-sm leading-relaxed text-slate-700">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </section>
            ))}
            {!hasNarrative && <p className="text-sm text-amber-700">Trust narrative content could not be loaded.</p>}
          </div>
        </div>
      </aside>
    </>
  );
};

const XIcon: React.FC = () => (
  <svg
    className="h-4 w-4"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
);
