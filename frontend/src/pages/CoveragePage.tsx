import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Building2, Layers3, ShieldCheck } from 'lucide-react';
import { Footer } from '../components/Footer';
import './CoveragePage.css';

type CoverageGroup = {
  buildingType: string;
  subtypes: string[];
};

const COVERAGE_GROUPS: CoverageGroup[] = [
  {
    buildingType: 'Multifamily',
    subtypes: ['Market Rate Apartments', 'Luxury Apartments', 'Affordable Housing'],
  },
  {
    buildingType: 'Industrial',
    subtypes: ['Warehouse', 'Distribution Center', 'Manufacturing', 'Flex Space', 'Cold Storage'],
  },
  {
    buildingType: 'Restaurant',
    subtypes: ['Quick Service', 'Full Service', 'Fine Dining', 'Cafe', 'Bar / Tavern'],
  },
  {
    buildingType: 'Hotels',
    subtypes: ['Limited Service Hotel', 'Full Service Hotel'],
  },
  {
    buildingType: 'Specialty',
    subtypes: ['Data Center', 'Laboratory', 'Self Storage', 'Car Dealership', 'Broadcast Facility'],
  },
  {
    buildingType: 'Healthcare',
    subtypes: [
      'Surgical Center',
      'Imaging Center',
      'Urgent Care',
      'Outpatient Clinic',
      'Medical Office Building',
      'Dental Office',
      'Hospital',
      'Medical Center',
      'Nursing Home',
      'Rehabilitation',
    ],
  },
  {
    buildingType: 'Office',
    subtypes: ['Class A', 'Class B'],
  },
  {
    buildingType: 'Retail',
    subtypes: ['Shopping Center', 'Big Box'],
  },
  {
    buildingType: 'Educational',
    subtypes: ['Elementary School', 'Middle School', 'High School', 'University', 'Community College'],
  },
  {
    buildingType: 'Civic',
    subtypes: ['Library', 'Courthouse', 'Government Building', 'Community Center', 'Public Safety'],
  },
  {
    buildingType: 'Recreation',
    subtypes: ['Fitness Center', 'Sports Complex', 'Aquatic Center', 'Recreation Center', 'Stadium'],
  },
  {
    buildingType: 'Mixed Use',
    subtypes: ['Office/Residential', 'Retail/Residential', 'Hotel/Residential', 'Transit Oriented', 'Urban Mixed'],
  },
  {
    buildingType: 'Parking',
    subtypes: ['Surface Parking', 'Parking Garage', 'Underground Parking', 'Automated Parking'],
  },
];

const COVERAGE_STYLES: Record<string, { icon: string; accent: string; soft: string }> = {
  Multifamily: { icon: '🏘️', accent: '#3566e8', soft: 'rgba(53, 102, 232, 0.12)' },
  Industrial: { icon: '🏭', accent: '#475569', soft: 'rgba(71, 85, 105, 0.12)' },
  Restaurant: { icon: '🍽️', accent: '#f59e0b', soft: 'rgba(245, 158, 11, 0.14)' },
  Hotels: { icon: '🏨', accent: '#7c3aed', soft: 'rgba(124, 58, 237, 0.12)' },
  Specialty: { icon: '🧪', accent: '#0f766e', soft: 'rgba(15, 118, 110, 0.14)' },
  Healthcare: { icon: '🏥', accent: '#dc2626', soft: 'rgba(220, 38, 38, 0.12)' },
  Office: { icon: '🏢', accent: '#2563eb', soft: 'rgba(37, 99, 235, 0.12)' },
  Retail: { icon: '🛍️', accent: '#0891b2', soft: 'rgba(8, 145, 178, 0.12)' },
  Educational: { icon: '🎓', accent: '#9333ea', soft: 'rgba(147, 51, 234, 0.12)' },
  Civic: { icon: '🏛️', accent: '#0f766e', soft: 'rgba(15, 118, 110, 0.12)' },
  Recreation: { icon: '🏟️', accent: '#059669', soft: 'rgba(5, 150, 105, 0.12)' },
  'Mixed Use': { icon: '🌆', accent: '#4f46e5', soft: 'rgba(79, 70, 229, 0.12)' },
  Parking: { icon: '🅿️', accent: '#334155', soft: 'rgba(51, 65, 85, 0.12)' },
};

const toCoverageId = (buildingType: string): string =>
  `coverage-${buildingType.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;

export const CoveragePage: React.FC = () => {
  const totalTypes = COVERAGE_GROUPS.length;
  const totalSubtypes = COVERAGE_GROUPS.reduce((sum, group) => sum + group.subtypes.length, 0);

  return (
    <div className="coverage-page">
      <div className="coverage-bg-orb coverage-bg-orb--top" />
      <div className="coverage-bg-orb coverage-bg-orb--bottom" />

      <nav className="coverage-nav">
        <div className="coverage-shell coverage-nav-inner">
          <Link to="/" className="coverage-brand">
            SpecSharp
          </Link>
          <div className="coverage-nav-actions">
            <Link to="/" className="coverage-btn coverage-btn--ghost">
              Back to Home
            </Link>
            <Link to="/new" className="coverage-btn coverage-btn--primary">
              Generate Decision Packet
            </Link>
          </div>
        </div>
      </nav>

      <main className="coverage-shell coverage-main">
        <section className="coverage-hero">
          <div className="coverage-hero-copy">
            <div className="coverage-pill">
              <Building2 className="w-4 h-4" />
              Coverage
            </div>
            <h1 className="coverage-hero-title">Coverage: Supported Building Types &amp; Subtypes</h1>
            <p className="coverage-hero-subtitle">Pick the closest subtype. SpecSharp is calibrated by subtype.</p>
            <p className="coverage-hero-detail">
              Not seeing your exact project? Choose the nearest match and SpecSharp will surface the key deltas in DealShield questions.
            </p>
          </div>

          <aside className="coverage-hero-stats">
            <div className="coverage-stat-card">
              <span className="coverage-stat-label">Building Types</span>
              <strong className="coverage-stat-value">{totalTypes}</strong>
            </div>
            <div className="coverage-stat-card">
              <span className="coverage-stat-label">Subtypes</span>
              <strong className="coverage-stat-value">{totalSubtypes}</strong>
            </div>
            <div className="coverage-stat-card coverage-stat-card--wide">
              <span className="coverage-stat-inline">
                <ShieldCheck className="w-4 h-4" />
                Deterministic packet format + subtype-level calibration
              </span>
            </div>
          </aside>
        </section>

        <section className="coverage-jump">
          <div className="coverage-jump-title">
            <Layers3 className="w-4 h-4" />
            Jump to Type
          </div>
          <div className="coverage-jump-links">
            {COVERAGE_GROUPS.map((group) => (
              <a key={`jump-${group.buildingType}`} href={`#${toCoverageId(group.buildingType)}`} className="coverage-jump-link">
                {group.buildingType}
              </a>
            ))}
          </div>
        </section>

        <section className="coverage-grid">
          {COVERAGE_GROUPS.map((group) => (
            <article
              key={group.buildingType}
              id={toCoverageId(group.buildingType)}
              className="coverage-card"
              style={
                {
                  '--coverage-accent': COVERAGE_STYLES[group.buildingType]?.accent ?? '#3566e8',
                  '--coverage-soft': COVERAGE_STYLES[group.buildingType]?.soft ?? 'rgba(53, 102, 232, 0.12)',
                } as React.CSSProperties
              }
            >
              <div className="coverage-card-header">
                <div className="coverage-card-type">
                  <span className="coverage-card-icon">{COVERAGE_STYLES[group.buildingType]?.icon ?? '🏗️'}</span>
                  <h2>{group.buildingType}</h2>
                </div>
                <span className="coverage-card-count">{group.subtypes.length} subtypes</span>
              </div>
              <ul className="coverage-subtype-list">
                {group.subtypes.map((subtype) => (
                  <li key={`${group.buildingType}-${subtype}`} className="coverage-subtype-pill">
                    {subtype}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </section>

        <section className="coverage-request">
          <h3>Not listed?</h3>
          <p>Send your project type and a 2-line description. We&apos;ll tell you the closest subtype to use and what to watch.</p>
          <div className="coverage-request-actions">
            <a
              href="mailto:cody@specsharp.ai?subject=Request%20a%20Subtype&body=Project%20type%3A%0A2-line%20description%3A%0A"
              className="coverage-btn coverage-btn--request"
            >
              Request a subtype
              <ArrowRight className="w-4 h-4" />
            </a>
            <p className="coverage-request-note">
              We&apos;ll map your deal to the nearest calibrated subtype and call out key deltas before you run.
            </p>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};
