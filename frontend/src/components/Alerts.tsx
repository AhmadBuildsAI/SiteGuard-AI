import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listAlerts, acknowledgeAlert } from '../services/site';
import { AlertItem } from '../types';

const SEV_STYLE: Record<string, string> = {
  CRITICAL: 'bg-red-50 border-red-200',
  HIGH: 'bg-orange-50 border-orange-200',
  MEDIUM: 'bg-yellow-50 border-yellow-200',
  LOW: 'bg-blue-50 border-blue-200',
};

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = () => {
    setLoading(true);
    listAlerts().then(setAlerts).catch(() => toast.error('Failed to load alerts')).finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const handleAck = async (id: string) => {
    try {
      await acknowledgeAlert(id);
      toast.success('Alert acknowledged');
      refresh();
    } catch {
      toast.error('Failed to acknowledge');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Safety Alerts</h1>
        <p className="text-gray-500 text-sm">
          {alerts.length} potential observations ({alerts.filter((a) => !a.is_acknowledged).length} unacknowledged)
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : alerts.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <p className="text-sm text-gray-500">No alerts. Great!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((a) => (
            <div key={a.id} className={`rounded-xl border p-5 ${SEV_STYLE[a.severity] || SEV_STYLE.LOW}`}>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                      a.severity === 'CRITICAL' ? 'bg-red-600 text-white' :
                      a.severity === 'HIGH' ? 'bg-orange-500 text-white' :
                      a.severity === 'MEDIUM' ? 'bg-yellow-500 text-white' :
                      'bg-blue-500 text-white'
                    }`}>{a.severity}</span>
                    <Link to={`/results/${a.inspection_id}`} className="text-xs text-gray-600 hover:underline">
                      {a.inspection_ref}
                    </Link>
                    <span className="text-xs font-mono text-gray-500">{a.rule_id}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-800">{a.title}</p>
                  <p className="text-sm text-gray-700 mt-1">{a.message}</p>
                  {a.vlm_observation && (
                    <p className="text-xs text-gray-500 mt-1 italic">VLM: {a.vlm_observation}</p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2 ml-4">
                  <span className="text-xs text-gray-500">
                    {new Date(a.created_at).toLocaleString()}
                  </span>
                  {!a.is_acknowledged ? (
                    <button
                      onClick={() => handleAck(a.id)}
                      className="px-3 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50"
                    >
                      Acknowledge
                    </button>
                  ) : (
                    <span className="text-xs text-green-700">✓ Acknowledged</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
        <p className="text-sm text-amber-800">
          ⚠️ <strong>Reminder:</strong> All alerts are potential observations. A qualified on-site safety inspector
          must physically verify each alert before any action is taken. This system is not a substitute for
          regulatory compliance and must not be used for automated disciplinary decisions.
        </p>
      </div>
    </div>
  );
};

export default Alerts;
