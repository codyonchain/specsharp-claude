import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Footer } from '../components/Footer';
import './FAQPage.css';

interface FAQItem {
  question: string;
  answer: string;
}

interface FAQSection {
  title: string;
  items: FAQItem[];
}

const faqData: FAQSection[] = [
  {
    title: "Getting Started",
    items: [
      {
        question: "How does SpecSharp work?",
        answer: "Simply describe your project in plain English (e.g., \"50,000 sf office building in Nashville, Tennessee\") and get a detailed cost estimate with 200+ line items in 60 seconds. No complex forms, no waiting."
      },
      {
        question: "Do I need to sign up to try it?",
        answer: "No! You can create 3 estimates without any signup. Just click \"Try It Now\" and see the magic happen. After 3 estimates, create an account to continue."
      },
      {
        question: "What information do I need to provide?",
        answer: "Just the basics: building type, size, location, and any special requirements. For example: \"100,000 sf hospital with emergency department in Manchester, New Hampshire.\""
      },
      {
        question: "How accurate are the estimates?",
        answer: "Our estimates are 85-90% accurate for preliminary budgeting. They include regional pricing, local building codes, and requirements specific to your area. Always verify final numbers with contractors before proceeding."
      }
    ]
  },
  {
    title: "Pricing & Billing",
    items: [
      {
        question: "How much does SpecSharp cost?",
        answer: "$799/month for unlimited estimates. This includes 3 team seats. Additional team members are $99/month each."
      },
      {
        question: "Is there a free trial?",
        answer: "Better than a trial - you can create 3 full estimates before signing up. No credit card required. See exactly what you're getting before you pay."
      },
      {
        question: "Can I cancel anytime?",
        answer: "Yes. No contracts, no cancellation fees. Cancel anytime from your account settings."
      },
      {
        question: "What payment methods do you accept?",
        answer: "We accept all major credit cards through Stripe. For enterprise accounts, we can arrange ACH payments."
      }
    ]
  },
  {
    title: "Features & Capabilities",
    items: [
      {
        question: "What building types do you support?",
        answer: "All major commercial types including:\n• Office buildings\n• Medical facilities\n• Warehouses & industrial\n• Retail & restaurants\n• Hotels & hospitality\n• Schools & education\n• Multi-family residential\n• Mixed-use developments"
      },
      {
        question: "Can I export estimates?",
        answer: "Yes! Export to Excel with detailed line items and formulas, or professional PDF reports. Perfect for sharing with clients or subs."
      },
      {
        question: "Do you handle mixed-use buildings?",
        answer: "Absolutely. Just specify the mix, like \"warehouse (70%) + office (30%)\" and we'll calculate accordingly."
      },
      {
        question: "Can I adjust for finish quality?",
        answer: "Yes. Choose from Basic, Standard, or Premium finishes. You can even set different quality levels for different trades."
      },
      {
        question: "Can I share estimates with others?",
        answer: "Yes! Generate share links that let anyone view your estimate without logging in. Links expire after 30 days for security."
      }
    ]
  },
  {
    title: "Accuracy & Reliability",
    items: [
      {
        question: "How do you determine costs?",
        answer: "We use current regional pricing data, RSMeans references, and local market conditions. Costs are updated regularly and adjusted for your specific location."
      },
      {
        question: "Why are New Hampshire and Tennessee costs different?",
        answer: "Labor rates, material costs, and code requirements vary by region. New Hampshire typically runs 10-15% higher than Tennessee due to labor costs and climate requirements."
      },
      {
        question: "What's included in the estimates?",
        answer: "Everything needed for preliminary budgeting:\n• All major trades (structural, mechanical, electrical, plumbing)\n• Regional adjustments\n• Local code requirements (snow loads for NH, seismic for TN)\n• Contractor overhead & profit\n• Contingency allowances"
      },
      {
        question: "What's NOT included?",
        answer: "Land costs, financing, permits, architectural fees, and owner-supplied items. These vary too much to estimate accurately without specific project details."
      }
    ]
  },
  {
    title: "Team & Collaboration",
    items: [
      {
        question: "How do team seats work?",
        answer: "Your base subscription includes 3 seats. All team members can view and create estimates. Add more team members for $99/month each."
      },
      {
        question: "Can subcontractors use SpecSharp?",
        answer: "Yes! Use the \"Extract for Subs\" feature to download trade-specific scopes. Send to your subs for accurate pricing."
      },
      {
        question: "Who can see my estimates?",
        answer: "Only your team members can see your estimates, unless you create a share link. You control who has access."
      }
    ]
  },
  {
    title: "Technical & Security",
    items: [
      {
        question: "Is my data secure?",
        answer: "Yes. We use bank-level encryption, secure Google OAuth for login, and httpOnly cookies for sessions. We never store passwords."
      },
      {
        question: "Can I access SpecSharp on mobile?",
        answer: "Yes, SpecSharp works on any device with a web browser. The interface is responsive and works great on tablets and phones."
      },
      {
        question: "Do you integrate with other software?",
        answer: "Not yet, but API access is on our roadmap for 2025. Let us know what integrations you need!"
      },
      {
        question: "What browsers do you support?",
        answer: "SpecSharp works best on Chrome, Safari, Firefox, and Edge. We recommend using the latest version for the best experience."
      }
    ]
  },
  {
    title: "Support",
    items: [
      {
        question: "How do I get help?",
        answer: "Email us at support@specsharp.ai. We typically respond within 24 hours on business days."
      },
      {
        question: "Do you offer training?",
        answer: "SpecSharp is designed to be intuitive - most users are creating estimates within minutes. We have video tutorials available and can arrange training for enterprise accounts."
      },
      {
        question: "Can you add my specific requirements?",
        answer: "We're always improving! Send feature requests to support@specsharp.ai. Many of our best features came from user suggestions."
      },
      {
        question: "What if I find an error in an estimate?",
        answer: "Let us know immediately at support@specsharp.ai. We'll investigate and update our algorithms if needed. Your feedback helps everyone get better estimates."
      }
    ]
  }
];

const FAQAccordion: React.FC<{ section: FAQSection }> = ({ section }) => {
  const [openItems, setOpenItems] = useState<number[]>([]);

  const toggleItem = (index: number) => {
    setOpenItems(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  return (
    <div className="faq-section">
      <h2 className="faq-section-title">{section.title}</h2>
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
    </div>
  );
};

export const FAQPage: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="font-bold text-2xl text-blue-600">SpecSharp</Link>
          <div className="flex items-center space-x-4">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              Back to Home
            </Link>
            <Link 
              to="/demo" 
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Demo
            </Link>
          </div>
        </div>
      </nav>

      {/* FAQ Content */}
      <main className="flex-grow bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold text-center mb-8">Frequently Asked Questions</h1>
            
            <div className="space-y-8">
              {faqData.map((section, index) => (
                <FAQAccordion key={index} section={section} />
              ))}
            </div>

            <div className="mt-12 text-center bg-white rounded-lg shadow-sm p-8">
              <h3 className="text-2xl font-semibold mb-4">Still have questions?</h3>
              <p className="text-gray-600 mb-6">
                Email <a href="mailto:support@specsharp.ai" className="text-blue-600 hover:underline">support@specsharp.ai</a> and we'll be happy to help!
              </p>
              <Link 
                to="/demo" 
                className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Try SpecSharp Now
              </Link>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};