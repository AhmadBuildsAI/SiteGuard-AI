import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import DisclaimerBanner from './DisclaimerBanner';

const Layout: React.FC = () => (
  <div className="min-h-screen bg-gray-50">
    <Navbar />
    <DisclaimerBanner />
    <main className="max-w-7xl mx-auto py-6 px-4">
      <Outlet />
    </main>
  </div>
);

export default Layout;
