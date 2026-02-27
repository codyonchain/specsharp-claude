import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/Footer';

export const PrivacyPolicy: React.FC = () => {
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
            <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
            <p className="text-gray-600 mb-8">Last updated: May 29, 2025</p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">1. Who We Are</h2>
              <p className="mb-4">
                This Privacy Policy describes how BidSharp Technologies LLC ("SpecSharp," "we," "us," or "our")
                collects, uses, and shares information when you use the SpecSharp platform. Our address is
                3669 Charlotte Pike, Nashville, TN 37209, United States.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">2. Information We Collect</h2>
              <p className="mb-4">
                When you use SpecSharp, we collect the following information:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li><strong>Account Information:</strong> Name and email address (via Google OAuth)</li>
                <li><strong>Project Data:</strong> Project descriptions, specifications, and outputs you create</li>
                <li><strong>Usage Data:</strong> Interactions with the Service and diagnostic logs</li>
                <li><strong>Device and Browser Data:</strong> IP address, device type, browser type, and basic telemetry</li>
              </ul>
              <p className="mb-4">
                We do not intentionally collect sensitive personal information (such as Social Security numbers,
                financial account numbers, or medical data).
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">3. How We Use Your Information</h2>
              <p className="mb-4">
                We use your information to:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>Provide and improve our estimation services</li>
                <li>Authenticate your account and maintain security</li>
                <li>Send service-related communications</li>
                <li>Analyze usage patterns to enhance features</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">4. Analytics</h2>
              <p className="mb-4">
                We plan to use Google Analytics to understand usage and improve the Service. If enabled, Google
                Analytics may collect information such as pages viewed and interactions. You can opt out by
                adjusting browser settings or using available Google opt-out tools.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">5. Data Security</h2>
              <p className="mb-4">
                We implement industry-standard security measures to protect your data:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>All data is encrypted in transit using TLS/SSL</li>
                <li>Secure authentication through Google OAuth</li>
                <li>Regular security audits and updates</li>
                <li>Limited access to personal information by employees</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">6. Data Sharing</h2>
              <p className="mb-4">
                <strong>We do not sell, trade, or rent your personal information to third parties.</strong>
              </p>
              <p className="mb-4">
                We may share information only in these circumstances:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>With your explicit consent</li>
                <li>To comply with legal obligations</li>
                <li>To protect our rights and prevent fraud</li>
                <li>With service providers who assist our operations (under strict confidentiality)</li>
              </ul>
              <p className="mb-4">
                Current service providers include Supabase (auth and database), Vercel (frontend hosting),
                Railway (backend hosting), and Google (OAuth). A current list is available on the
                Subprocessor List page.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">7. Your Rights</h2>
              <p className="mb-4">
                Depending on your location, you may have the right to:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>Access your personal data</li>
                <li>Correct inaccurate information</li>
                <li>Request deletion of your account and data</li>
                <li>Export your project data</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">8. Data Retention</h2>
              <p className="mb-4">
                We retain your data for as long as your account is active. Upon account deletion, 
                we remove your personal information within 30 days, except where required by law 
                to retain certain records.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">9. International Transfers</h2>
              <p className="mb-4">
                SpecSharp is based in the United States. Your information may be processed and stored in
                the United States or other locations where our service providers operate.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">10. Contact Us</h2>
              <p className="mb-4">
                For privacy-related questions or to exercise your rights, contact us at:
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
