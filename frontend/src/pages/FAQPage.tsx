import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown, ChevronUp, ShieldCheck, Sparkles, Gauge, FileText, Users } from 'lucide-react';
import { Footer } from '../components/Footer';
import './FAQPage.css';

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQSection {
  id: string;
  title: string;
  summary: string;
  items: FAQItem[];
}

const faqSections: FAQSection[] = [
  {
    id: 'basics',
    title: 'Platform Basics',
    summary: 'What SpecSharp is, who it is for, and what it does.',
    items: [
      {
        question: 'What is SpecSharp?',
        answer:
          'SpecSharp is a decision-support platform for development deals. We generate structured, auditable estimates and a DealShield summary so teams can pressure-test scope, cost, and risk fast.'
      },
      {
        question: 'Who is it built for?',
        answer:
          'SpecSharp is built for developers, owners, lenders, and operators who need a fast, credible early-stage cost view. It is a B2B product and is not intended for consumer use.'
      },
      {
        question: 'How do I run a deal?',
        answer:
          'Describe the project in plain English (type, size, location, and special features). SpecSharp returns a trade-level budget, schedule signals, and a decision summary.'
      },
      {
        question: 'Is this a bid or a contract?',
        answer:
          'No. SpecSharp is for preliminary budgeting and decision support. Final pricing should be validated by qualified professionals.'
      }
    ]
  },
  {
    id: 'onboarding',
    title: 'Onboarding & Access',
    summary: 'How accounts, run limits, and teams work.',
    items: [
      {
        question: 'Do you offer self-serve signup?',
        answer:
          'Not yet. We onboard manually to ensure accurate configuration, clean data, and the right usage limits. Email cody@specsharp.ai to get access.'
      },
      {
        question: 'How do run limits work?',
        answer:
          'Each organization has an included run quota. You can add runs at any time by request. We can also grant temporary or unlimited access for approved internal users.'
      },
      {
        question: 'Can I add teammates?',
        answer:
          'Yes. We support team access and role-based permissions. Tell us who to add and their role.'
      },
      {
        question: 'Can I transfer ownership or change org details?',
        answer:
          'Yes. We can update organization ownership, rename the org, or adjust roles on request.'
      }
    ]
  },
  {
    id: 'outputs',
    title: 'Outputs & Accuracy',
    summary: 'What you get, what’s included, and how to use it safely.',
    items: [
      {
        question: 'What does SpecSharp output?',
        answer:
          'You get a trade-level cost breakdown, a DealShield decision summary, and supporting narrative signals. Exports include PDF and spreadsheet formats.'
      },
      {
        question: 'How accurate are the estimates?',
        answer:
          'SpecSharp is designed for early-stage budgeting. Use it to identify directional cost, scope risk, and decision readiness. Final pricing should always be validated by qualified professionals.'
      },
      {
        question: 'What is included in the cost?',
        answer:
          'Core trade scopes, regional adjustments, and major systems are included. You can also layer in special features and finish-level adjustments.'
      },
      {
        question: 'What is not included?',
        answer:
          'Land, financing, permitting fees, legal work, and owner-procured items are typically excluded unless explicitly configured.'
      }
    ]
  },
  {
    id: 'security',
    title: 'Data & Security',
    summary: 'How we protect your data and keep accounts isolated.',
    items: [
      {
        question: 'Who can see my projects?',
        answer:
          'Only users in your organization can access your projects. Shared links are optional and controlled by you.'
      },
      {
        question: 'How is data secured?',
        answer:
          'We use secure OAuth authentication, encrypted connections, strict access controls, and database row-level security for tenant isolation.'
      },
      {
        question: 'Do you sell or share my data?',
        answer:
          'No. We do not sell your data. We share data only with vetted service providers required to run the platform.'
      },
      {
        question: 'Do you use my data to train public models?',
        answer:
          'We use your data only to provide the Service. If training or analytics requirements change, we will disclose them in our policies.'
      }
    ]
  },
  {
    id: 'collaboration',
    title: 'Exports & Collaboration',
    summary: 'How to share outputs with stakeholders.',
    items: [
      {
        question: 'Can I export to PDF or Excel?',
        answer:
          'Yes. You can export DealShield PDFs and structured spreadsheets for internal review or external sharing.'
      },
      {
        question: 'Can I share a link with partners?',
        answer:
          'Yes. You can generate a share link to provide view-only access to a specific project.'
      },
      {
        question: 'Can I pull trade packages for subs?',
        answer:
          'Yes. SpecSharp can export trade-specific summaries to support subcontractor pricing workflows.'
      }
    ]
  },
  {
    id: 'support',
    title: 'Support & Roadmap',
    summary: 'How to get help and what’s coming next.',
    items: [
      {
        question: 'How do I get support?',
        answer:
          'Email cody@specsharp.ai. We typically respond within one business day.'
      },
      {
        question: 'Do you offer training?',
        answer:
          'Yes. We can provide onboarding sessions for teams and review your first few deals together.'
      },
      {
        question: 'Do you integrate with other tools?',
        answer:
          'Not yet. API access and integrations are on our roadmap. Tell us which tools matter most.'
      },
      {
        question: 'Where can I request features?',
        answer:
          'Email cody@specsharp.ai with your request. We prioritize features based on customer impact.'
      }
    ]
  }
];

const FAQAccordion: React.FC<{ section: FAQSection }> = ({ section }) => {
  const [openItems, setOpenItems] = useState<number[]>([]);

  const toggleItem = (index: number) => {
    setOpenItems((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  return (
    <section id={section.id} className="faq-section">
      <div className="faq-section-head">
        <h2 className="faq-section-title">{section.title}</h2>
        <p className="faq-section-summary">{section.summary}</p>
      </div>
      <div className="faq-items">
        {section.items.map((item, index) => (
          <div key={index} className="faq-item">
            <button
              className="faq-question"
              onClick={() => toggleItem(index)}
              aria-expanded={openItems.includes(index)}
            >
              <span>{item.question}</span>
              {openItems.includes(index) ? (
                <ChevronUp className="faq-icon" />
              ) : (
                <ChevronDown className="faq-icon" />
              )}
            </button>
            {openItems.includes(index) && (
              <div className="faq-answer">
                {item.answer.split('\n').map((line, i) => (
                  <p key={i} className={line.startsWith('•') ? 'faq-list-item' : ''}>
                    {line}
                  </p>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export const FAQPage: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="faq-page">
      <nav className="faq-nav">
        <div className="faq-nav-inner">
          <Link to="/" className="faq-logo">SpecSharp</Link>
          <div className="faq-nav-links">
            <Link to="/coverage">Coverage</Link>
            <Link to="/demo">Demo</Link>
            <a href="mailto:cody@specsharp.ai?subject=SpecSharp%20Access">Request Access</a>
          </div>
        </div>
      </nav>

      <header className="faq-hero">
        <div className="faq-hero-content">
          <span className="faq-kicker">SpecSharp FAQ</span>
          <h1>Clear answers before you run your first deal</h1>
          <p>
            SpecSharp is built for fast, defensible decision making. This FAQ covers onboarding,
            outputs, security, and how teams use SpecSharp in real workflows.
          </p>
          <div className="faq-hero-actions">
            <Link to="/demo" className="faq-primary-btn">View Demo</Link>
            <a href="mailto:cody@specsharp.ai?subject=SpecSharp%20Access" className="faq-secondary-btn">Request Access</a>
          </div>
        </div>
        <div className="faq-hero-card">
          <div className="faq-hero-card-header">
            <ShieldCheck size={22} />
            <span>Decision Insurance Snapshot</span>
          </div>
          <ul>
            <li><Sparkles size={18} /> Trade-level budget + risk signals</li>
            <li><Gauge size={18} /> Fast turnaround, built for precon</li>
            <li><FileText size={18} /> PDF + spreadsheet exports</li>
            <li><Users size={18} /> Org‑scoped access controls</li>
          </ul>
        </div>
      </header>

      <section className="faq-metrics">
        <div className="faq-metric-card">
          <p className="faq-metric-label">Designed for</p>
          <h3>Developers &amp; Owners</h3>
        </div>
        <div className="faq-metric-card">
          <p className="faq-metric-label">Outputs</p>
          <h3>DealShield + Trade Detail</h3>
        </div>
        <div className="faq-metric-card">
          <p className="faq-metric-label">Security Model</p>
          <h3>Tenant-Isolated by Default</h3>
        </div>
      </section>

      <section className="faq-quick-nav">
        {faqSections.map((section) => (
          <a key={section.id} href={`#${section.id}`} className="faq-quick-card">
            <span>{section.title}</span>
            <p>{section.summary}</p>
          </a>
        ))}
      </section>

      <main className="faq-body">
        {faqSections.map((section) => (
          <FAQAccordion key={section.id} section={section} />
        ))}

        <section className="faq-contact-section">
          <h3>Still have questions?</h3>
          <p>
            We respond quickly and can walk you through a live example.
          </p>
          <a href="mailto:cody@specsharp.ai?subject=SpecSharp%20Questions">
            Email cody@specsharp.ai
          </a>
        </section>
      </main>

      <Footer />
    </div>
  );
};
