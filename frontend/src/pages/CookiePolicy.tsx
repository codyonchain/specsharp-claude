import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/Footer';

export const CookiePolicy: React.FC = () => {
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
            <h1 className="text-3xl font-bold mb-6">Cookie Notice</h1>
            <p className="text-gray-600 mb-8">Last updated: May 29, 2025</p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">1. What Are Cookies</h2>
              <p className="mb-4">
                Cookies are small text files that are stored on your device when you visit our website. 
                They help us provide you with a better experience by remembering your preferences and 
                login status.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">2. How We Use Cookies</h2>
              <p className="mb-4">
                SpecSharp uses cookies for the following purposes:
              </p>
              
              <h3 className="text-xl font-semibold mb-2 mt-4">Essential Cookies</h3>
              <ul className="list-disc pl-6 mb-4">
                <li><strong>Authentication:</strong> To keep you logged in as you navigate between pages</li>
                <li><strong>Security:</strong> To ensure secure access to your account and protect against fraud</li>
                <li><strong>Session Management:</strong> To remember your active session</li>
              </ul>

              <h3 className="text-xl font-semibold mb-2 mt-4">Analytics Cookies (if enabled)</h3>
              <ul className="list-disc pl-6 mb-4">
                <li><strong>Usage Analytics:</strong> To understand how visitors use our site</li>
                <li><strong>Performance Monitoring:</strong> To identify and fix technical issues</li>
                <li><strong>Feature Improvement:</strong> To see which features are most popular</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">3. Third-Party Cookies</h2>
              <p className="mb-4">
                We may use third-party services that set their own cookies:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li><strong>Google OAuth:</strong> For secure authentication</li>
                <li><strong>Google Analytics (if enabled):</strong> To understand usage and improve the Service</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">4. Managing Cookies</h2>
              <p className="mb-4">
                You can control and manage cookies in several ways:
              </p>
              
              <h3 className="text-xl font-semibold mb-2 mt-4">Browser Settings</h3>
              <p className="mb-4">
                Most browsers allow you to:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li>View what cookies are stored</li>
                <li>Delete cookies individually or entirely</li>
                <li>Block third-party cookies</li>
                <li>Block all cookies from specific sites</li>
              </ul>

              <p className="mb-4">
                <strong>Note:</strong> Blocking essential cookies may prevent you from using certain 
                features of SpecSharp, including the ability to log in.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">5. Cookie Duration</h2>
              <p className="mb-4">
                Our cookies have different durations:
              </p>
              <ul className="list-disc pl-6 mb-4">
                <li><strong>Session Cookies:</strong> Deleted when you close your browser</li>
                <li><strong>Persistent Cookies:</strong> Remain for a period set by the provider (up to 2 years for analytics, if enabled)</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">6. Updates to This Policy</h2>
              <p className="mb-4">
                We may update this Cookie Policy from time to time. We will notify you of any changes 
                by updating the "Last updated" date at the top of this policy.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold mb-4">7. Contact Us</h2>
              <p className="mb-4">
                If you have questions about our use of cookies, please contact us at:
              </p>
              <p className="mb-4">
                Email: <a href="mailto:cody@specsharp.ai" className="text-blue-600 hover:underline">cody@specsharp.ai</a>
              </p>
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
