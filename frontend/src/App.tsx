import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/Login';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import AnalyzeSite from './components/AnalyzeSite';
import DetectionResults from './components/DetectionResults';
import Alerts from './components/Alerts';
import SiteHistory from './components/SiteHistory';

const App: React.FC = () => (
  <BrowserRouter>
    <Toaster position="top-right" />
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="analyze" element={<AnalyzeSite />} />
        <Route path="results/:id" element={<DetectionResults />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="history" element={<SiteHistory />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
);

export default App;
