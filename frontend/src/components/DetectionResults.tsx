import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import SafetyScoreGauge from './SafetyScoreGauge';
import BoundingBoxImage from './BoundingBoxImage';
import DetectionList from './DetectionList';
import StatCard from './StatCard';
import { getInspection } from '../services/site';
import { InspectionDetail } from '../types';

const DetectionResults: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [insp, setInsp] = useState<InspectionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getInspection(id)
      .then(setInsp)
      .catch(() => { toast.error('Failed to load inspection'); navigate('/'); })
      .finally(() => setLoading(false));
  }, [id, navigate]);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!insp) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Detection Results</h1>
          <p className="text-gray-500 text-sm">
            {insp.inspection_ref} · {insp.site_name}
            {insp.site_area && ` · ${insp.site_area}`}
            {insp.vlm_used === 'true' && <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">VLM</span>}
          </p>
        </div>
        <button onClick={() => navigate('/')} className="text-sm text-orange-600 hover:underline">
          ← Dashboard
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div>
          <SafetyScoreGauge score={insp.safety_score} riskLevel={insp.risk_level} />
        </div>
        <div className="lg:col-span-2 grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard title="Workers" value={insp.worker_count} icon="👷" color="blue" />
          <StatCard title="Helmets" value={insp.helmet_count} icon="🪖" color="green" />
          <StatCard title="Vests" value={insp.vest_count} icon="🦺" color="yellow" />
          <StatCard title="Equipment" value={insp.equipment_count} icon="🚜" color="orange" />
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard title="PPE Compliance" value={`${insp.ppe_score.toFixed(0)}%`} color={insp.ppe_score > 70 ? 'green' : 'red'} />
        <StatCard title="Zone Safety" value={`${insp.zone_score.toFixed(0)}%`} color={insp.zone_score > 70 ? 'green' : 'red'} />
        <StatCard title="Equipment Safety" value={`${insp.equipment_score.toFixed(0)}%`} color={insp.equipment_score > 70 ? 'green' : 'red'} />
        <StatCard title="Site Organization" value={`${insp.organization_score.toFixed(0)}%`} color={insp.organization_score > 70 ? 'green' : 'yellow'} />
      </div>

      <BoundingBoxImage inspection={insp} />

      {insp.explanation && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-2">🧠 AI Analysis</h3>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">{insp.explanation}</pre>
        </div>
      )}

      <DetectionList detections={insp.detections} violations={insp.violations} />

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
        <p className="text-sm text-amber-800">⚠️ {insp.disclaimer}</p>
      </div>
    </div>
  );
};

export default DetectionResults;
