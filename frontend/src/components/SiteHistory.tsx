import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listInspections } from '../services/site';
import { InspectionListItem } from '../types';

const SiteHistory: React.FC = () => {
  const [inspections, setInspections] = useState<InspectionListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listInspections()
      .then(setInspections)
      .catch(() => toast.error('Failed to load history'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Site History</h1>
        <p className="text-gray-500 text-sm">{inspections.length} inspections</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="px-4 py-3 text-left">Ref</th>
              <th className="px-4 py-3 text-left">Site</th>
              <th className="px-4 py-3 text-left">Safety Score</th>
              <th className="px-4 py-3 text-left">Risk</th>
              <th className="px-4 py-3 text-left">Workers</th>
              <th className="px-4 py-3 text-left">Observations</th>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-left">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : inspections.length === 0 ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-gray-400">
                No inspections yet. Upload a site image to begin.
              </td></tr>
            ) : (
              inspections.map((i) => (
                <tr key={i.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs">{i.inspection_ref}</td>
                  <td className="px-4 py-3 text-gray-700">{i.site_name}</td>
                  <td className="px-4 py-3 font-bold">{i.safety_score.toFixed(0)}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                      i.risk_level === 'LOW' ? 'bg-green-100 text-green-700' :
                      i.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                      i.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                      'bg-red-100 text-red-700'
                    }`}>{i.risk_level}</span>
                  </td>
                  <td className="px-4 py-3">{i.worker_count}</td>
                  <td className="px-4 py-3">{i.violation_count}</td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {new Date(i.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/results/${i.id}`} className="text-orange-600 hover:underline">
                      View
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SiteHistory;
