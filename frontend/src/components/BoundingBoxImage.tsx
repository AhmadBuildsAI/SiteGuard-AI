import React, { useEffect, useRef, useState } from 'react';
import { getOverlay } from '../services/site';
import { InspectionDetail } from '../types';

interface Props {
  inspection: InspectionDetail;
}

const SEV_COLORS: Record<string, string> = {
  CRITICAL: '#dc2626',
  HIGH: '#ea580c',
  MEDIUM: '#eab308',
  LOW: '#3b82f6',
};

const BoundingBoxImage: React.FC<Props> = ({ inspection }) => {
  const [overlay, setOverlay] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showBoxes, setShowBoxes] = useState(true);

  useEffect(() => {
    setLoading(true);
    getOverlay(inspection.id)
      .then(setOverlay)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [inspection.id]);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold text-gray-800">🔍 Detected Objects & Violations</h3>
        <button
          onClick={() => setShowBoxes(!showBoxes)}
          className="text-xs px-3 py-1 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          {showBoxes ? 'Hide' : 'Show'} boxes
        </button>
      </div>
      {loading ? (
        <div className="h-96 bg-gray-100 rounded-lg animate-pulse" />
      ) : (
        <div className="relative">
          <img
            src={showBoxes && overlay ? overlay : `/uploads/${inspection.filename}`}
            alt="Site"
            className="w-full rounded-lg border border-gray-200"
          />
          <div className="mt-3 flex flex-wrap gap-3 text-xs">
            {Object.entries(SEV_COLORS).map(([sev, color]) => (
              <span key={sev} className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full" style={{ background: color }} />
                {sev}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BoundingBoxImage;
