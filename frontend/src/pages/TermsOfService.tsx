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
            <p className="text-gray-600 mb-8">Last updated: {new Date().toLocaleDateString()}</p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">1. Service Description</h2>
              <p className="mb-4">
                SpecSharp provides automated construction cost estimation services through our web platform. 
                Our service generates preliminary budget estimates based on project descriptions and regional 
                construction data.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">2. Accuracy Disclaimer</h2>
              <p className="mb-4">
                <strong>IMPORTANT:</strong> All estimates provided by SpecSharp are for preliminary budgeting 
                purposes only. Actual construction costs may vary significantly based on:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>Site-specific conditions</li>
                <li>Current material and labor costs</li>
                <li>Design specifications and finishes</li>
                <li>Local building codes and requirements</li>
                <li>Market conditions at time of construction</li>
              </ul>
              <p className="mb-4">
                Users should always consult with qualified construction professionals for final project pricing.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">3. Payment Terms</h2>
              <p className="mb-4">
                SpecSharp is offered at $799 per month for unlimited use. You may cancel your subscription 
                at any time. Cancellations take effect at the end of the current billing period.
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>Billing is monthly in advance</li>
                <li>No refunds for partial months</li>
                <li>Prices subject to change with 30 days notice</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">4. Data Ownership</h2>
              <p className="mb-4">
                You retain full ownership of all project data you input into SpecSharp and all estimates 
                generated. We claim no ownership rights over your project information.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">5. Limitation of Liability</h2>
              <p className="mb-4">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, SPECSHARP SHALL NOT BE LIABLE FOR ANY INDIRECT, 
                INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, 
                WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER 
                INTANGIBLE LOSSES.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">6. Acceptable Use</h2>
              <p className="mb-4">
                You agree not to use SpecSharp to:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>Violate any laws or regulations</li>
                <li>Infringe on intellectual property rights</li>
                <li>Transmit malicious code or interfere with the service</li>
                <li>Attempt to gain unauthorized access to our systems</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">7. Contact Information</h2>
              <p className="mb-4">
                For questions about these Terms of Service, please contact us at:
              </p>
              <p className="mb-4">
                Email: <a href="mailto:support@specsharp.ai" className="text-blue-600 hover:underline">support@specsharp.ai</a>
              </p>
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};