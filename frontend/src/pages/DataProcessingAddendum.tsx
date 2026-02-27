import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/Footer';

export const DataProcessingAddendum: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="font-bold text-2xl text-blue-600">SpecSharp</Link>
          <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">
            Back to Home
          </Link>
        </div>
      </nav>

      <main className="flex-grow bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-sm p-8">
            <h1 className="text-3xl font-bold mb-6">Data Processing Addendum (DPA)</h1>
            <p className="text-gray-600 mb-8">Last updated: May 29, 2025</p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">1. Scope and Roles</h2>
              <p className="mb-4">
                This DPA applies to personal data processed by BidSharp Technologies LLC ("SpecSharp") on behalf
                of a customer using the SpecSharp Service. The customer is the data controller and SpecSharp is
                the data processor for such data.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">2. Processing Details</h2>
              <ul className="list-disc pl-6 mb-4">
                <li><strong>Purpose:</strong> Provide, secure, and improve the Service.</li>
                <li><strong>Types of data:</strong> Account identifiers, email, and project-related inputs.</li>
                <li><strong>Data subjects:</strong> Customer employees, contractors, and authorized users.</li>
                <li><strong>Duration:</strong> For the term of the Service and retention period in the Privacy Policy.</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">3. Security Measures</h2>
              <p className="mb-4">
                SpecSharp implements appropriate technical and organizational measures to protect personal data,
                including encryption in transit, access controls, and monitoring.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">4. Subprocessors</h2>
              <p className="mb-4">
                SpecSharp may use subprocessors to provide the Service. A current list is available on the
                Subprocessor List page. We require subprocessors to implement appropriate safeguards.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">5. Assistance and Requests</h2>
              <p className="mb-4">
                SpecSharp will reasonably assist customers with data subject requests and privacy inquiries
                related to personal data processed through the Service.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">6. Deletion and Return</h2>
              <p className="mb-4">
                Upon termination of the Service, SpecSharp will delete or return personal data in accordance
                with the Privacy Policy and applicable law.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">7. Breach Notification</h2>
              <p className="mb-4">
                SpecSharp will notify customers of a confirmed security incident affecting personal data
                without undue delay.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">8. Contact</h2>
              <p className="mb-4">
                For DPA requests or questions, contact:
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
