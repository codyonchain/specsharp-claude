import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/Footer';

type Subprocessor = {
  name: string;
  purpose: string;
  data: string;
  location: string;
  status?: string;
};

const subprocessors: Subprocessor[] = [
  {
    name: 'Supabase',
    purpose: 'Authentication, database, and storage infrastructure',
    data: 'Account identifiers, project metadata, audit logs',
    location: 'United States',
  },
  {
    name: 'Railway',
    purpose: 'Backend hosting',
    data: 'Service logs and request metadata',
    location: 'United States',
  },
  {
    name: 'Vercel',
    purpose: 'Frontend hosting and delivery',
    data: 'Service logs and request metadata',
    location: 'United States',
  },
  {
    name: 'Google (OAuth)',
    purpose: 'Authentication provider',
    data: 'User email and OAuth identifiers',
    location: 'United States',
  },
  {
    name: 'Google Analytics',
    purpose: 'Usage analytics (if enabled)',
    data: 'Usage and device metadata',
    location: 'United States',
    status: 'Planned',
  },
];

export const SubprocessorList: React.FC = () => {
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
            <h1 className="text-3xl font-bold mb-6">Subprocessor List</h1>
            <p className="text-gray-600 mb-8">Last updated: May 29, 2025</p>

            <p className="mb-6">
              SpecSharp uses the following subprocessors to provide the Service. If you have questions or
              requests, contact <a href="mailto:cody@specsharp.ai" className="text-blue-600 hover:underline">cody@specsharp.ai</a>.
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="py-2 pr-4 font-semibold">Subprocessor</th>
                    <th className="py-2 pr-4 font-semibold">Purpose</th>
                    <th className="py-2 pr-4 font-semibold">Data Processed</th>
                    <th className="py-2 pr-4 font-semibold">Location</th>
                    <th className="py-2 pr-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {subprocessors.map((sp) => (
                    <tr key={sp.name} className="border-b">
                      <td className="py-2 pr-4">{sp.name}</td>
                      <td className="py-2 pr-4">{sp.purpose}</td>
                      <td className="py-2 pr-4">{sp.data}</td>
                      <td className="py-2 pr-4">{sp.location}</td>
                      <td className="py-2 pr-4">{sp.status || 'Active'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
