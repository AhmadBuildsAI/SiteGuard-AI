import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import toast from 'react-hot-toast';
import StatCard from './StatCard';
import { getDashboard } from '../services/site';
import { DashboardData } from '../types';

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Site Safety Dashboard</h1>
          <p className="text-gray-500 text-sm">Overview of inspections and potential safety observations</p>
        </div>
        <Link
          to="/analyze"
          className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition"
        >
          📸 Analyze Site
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Inspections" value={data.total_inspections} icon="📁" color="orange" />
        <StatCard title="Alerts" value={data.total_alerts} icon="🚨" color="red" />
        <StatCard title="Critical" value={data.critical_alerts} icon="🔥" color="red" />
        <StatCard title="High" value={data.high_alerts} icon="⚠️" color="yellow" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-3">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data.risk_distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="level" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#ea580c" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-3">Safety Score Trend</h3>
          {data.safety_trend.length === 0 ? (
            <p className="text-sm text-gray-500 py-12 text-center">No inspections yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={data.safety_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#16a34a" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">Recent Inspections</h3>
        {data.recent_inspections.length === 0 ? (
          <p className="text-sm text-gray-500 py-8 text-center">No inspections yet. Analyze a site to begin.</p>
        ) : (
          <div className="space-y-2">
            {data.recent_inspections.map((i) => (
              <Link
                key={i.id}
                to={`/history`}
                className="flex items-center justify-between p-3 border border-gray-100 rounded-lg hover:bg-gray-50 transition"
              >
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">
                    {i.ref} — {i.site_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(i.created_at).toLocaleString()} · {i.violation_count} observation(s)
                  </p>
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded ${
                  i.risk_level === 'LOW' ? 'bg-green-100 text-green-700' :
                  i.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                  i.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {i.safety_score.toFixed(0)}/100
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
