import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/Footer';

export const TermsOfService: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="font-bold text-2xl text-blue-600">SpecSharp</Link>
          <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">
            Back to Home
          </Link>
        </div>
      </nav>

      {/* Content */}
      <main className="flex-grow bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-sm p-8">
            <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
            <p className="text-gray-600 mb-8">Last updated: May 29, 2025</p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">1. Agreement and Definitions</h2>
              <p className="mb-4">
                These Terms of Service (the "Terms") govern your access to and use of the SpecSharp platform
                and related services (the "Service"). The Service is provided by BidSharp Technologies LLC
                ("SpecSharp," "we," "us," or "our"), located at 3669 Charlotte Pike, Nashville, TN 37209,
                United States. By using the Service, you agree to these Terms.
              </p>
              <p className="mb-4">
                The Service is offered for business-to-business use only. You represent that you are acting
                on behalf of a business entity and have authority to bind that entity to these Terms.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">2. Service Description and Disclaimers</h2>
              <p className="mb-4">
                SpecSharp provides automated construction cost estimation and decision-support outputs based
                on project descriptions and regional data. Outputs are scenario-based and not a guarantee
                of project performance.
              </p>
              <p className="mb-4">
                <strong>IMPORTANT:</strong> All estimates are for preliminary budgeting purposes only. Actual
                construction costs may vary based on:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>Site-specific conditions</li>
                <li>Current material and labor costs</li>
                <li>Design specifications and finishes</li>
                <li>Local building codes and requirements</li>
                <li>Market conditions at time of construction</li>
              </ul>
              <p className="mb-4">
                The Service does not provide legal, tax, accounting, or investment advice. You should consult
                qualified professionals for final pricing, contracts, and investment decisions.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">3. Accounts and Access</h2>
              <p className="mb-4">
                You are responsible for maintaining the confidentiality of your account credentials and
                for all activities that occur under your account. Do not share credentials outside your
                organization. You must provide accurate account information and keep it current.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">4. Fees, Invoices, and Run Limits</h2>
              <p className="mb-4">
                Fees are provided by invoice or an order form and are due according to the payment terms
                stated therein. The Service may include run limits or usage caps as described in your order
                form or account settings. Additional runs may be purchased or granted by SpecSharp.
              </p>
              <p className="mb-4">
                <strong>No refunds unless required by law.</strong>
              </p>
              <p className="mb-4">
                You are responsible for any applicable taxes, levies, or duties imposed by taxing authorities.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">5. Data Ownership and License</h2>
              <p className="mb-4">
                You retain ownership of your project data and inputs. You grant SpecSharp a limited, non-exclusive
                license to process your data solely to provide the Service, including generating outputs and
                maintaining audit trails.
              </p>
              <p className="mb-4">
                SpecSharp retains all rights to the Service, software, models, and output formatting, including
                all related intellectual property.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">6. Acceptable Use</h2>
              <p className="mb-4">
                You agree not to use the Service to:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>Violate any laws or regulations</li>
                <li>Infringe intellectual property rights</li>
                <li>Transmit malicious code or interfere with the Service</li>
                <li>Attempt unauthorized access to systems or data</li>
                <li>Reverse engineer or misuse the Service</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">7. Suspension and Termination</h2>
              <p className="mb-4">
                We may suspend or terminate access if we reasonably believe you have violated these Terms,
                posed a security risk, or failed to pay fees. You may stop using the Service at any time.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">8. Warranty Disclaimer</h2>
              <p className="mb-4">
                THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE." SPECSHARP DISCLAIMS ALL WARRANTIES,
                WHETHER EXPRESS, IMPLIED, OR STATUTORY, INCLUDING IMPLIED WARRANTIES OF MERCHANTABILITY,
                FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">9. Limitation of Liability</h2>
              <p className="mb-4">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, SPECSHARP SHALL NOT BE LIABLE FOR ANY INDIRECT, 
                INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, 
                WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER 
                INTANGIBLE LOSSES.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">10. Governing Law</h2>
              <p className="mb-4">
                These Terms are governed by the laws of the State of Tennessee, United States, without regard
                to conflict of law principles. Any disputes shall be brought in the state or federal courts
                located in Davidson County, Tennessee.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">11. Contact Information</h2>
              <p className="mb-4">
                For questions about these Terms of Service, please contact us at:
              </p>
              <p className="mb-4">
                Email: <a href="mailto:cody@specsharp.ai" className="text-blue-600 hover:underline">cody@specsharp.ai</a>
              </p>
              <p className="mb-4">
                BidSharp Technologies LLC, 3669 Charlotte Pike, Nashville, TN 37209, United States.
              </p>
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
