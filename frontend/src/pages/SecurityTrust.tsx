import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/Footer';

export const SecurityTrust: React.FC = () => {
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
            <h1 className="text-3xl font-bold mb-6">Security &amp; Trust</h1>
            <p className="text-gray-600 mb-8">Last updated: May 29, 2025</p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">1. Security Overview</h2>
              <p className="mb-4">
                SpecSharp is built for business customers who need confidentiality, integrity, and
                availability. We apply industry-standard security practices and a defense-in-depth model
                across authentication, data access, and infrastructure.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">2. Data Protection</h2>
              <ul className="list-disc pl-6 mb-4">
                <li><strong>Encryption in transit:</strong> All traffic uses TLS.</li>
                <li><strong>Access controls:</strong> Role-based access and least-privilege policies.</li>
                <li><strong>Tenant isolation:</strong> Backend authorization + database row-level security.</li>
                <li><strong>Secrets management:</strong> Keys are stored in secured environment variables.</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">3. Authentication</h2>
              <p className="mb-4">
                We use Google OAuth for login. Sessions are validated server-side and access is scoped to
                the user and organization that owns the data.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">4. Logging &amp; Monitoring</h2>
              <p className="mb-4">
                We maintain audit trails and operational logs to detect abuse and troubleshoot issues. We
                avoid logging sensitive credentials and limit access to logs.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">5. Incident Response</h2>
              <p className="mb-4">
                We investigate suspected security incidents promptly and take corrective action. If an
                incident affects your data, we will notify you without undue delay.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">6. Contact</h2>
              <p className="mb-4">
                For security questions or to request documentation, contact:
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
