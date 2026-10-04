import React from 'react';
import { Detection, Violation } from '../types';

interface Props {
  detections: Detection[];
  violations: Violation[];
}

const SEV_BADGE: Record<string, string> = {
  CRITICAL: 'bg-red-100 text-red-700',
  HIGH: 'bg-orange-100 text-orange-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  LOW: 'bg-blue-100 text-blue-700',
};

const DetectionList: React.FC<Props> = ({ detections, violations }) => {
  return (
    <div className="space-y-4">
      {violations.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-3">
            🚨 Potential Safety Observations ({violations.length})
          </h3>
          <div className="space-y-2">
            {violations.map((v, i) => (
              <div key={i} className="border-l-4 pl-3 py-2" style={{
                borderColor: v.severity === 'CRITICAL' ? '#dc2626' : v.severity === 'HIGH' ? '#ea580c' : v.severity === 'MEDIUM' ? '#eab308' : '#3b82f6',
              }}>
                <div className="flex justify-between items-start">
                  <p className="text-sm font-medium text-gray-800">{v.title}</p>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${SEV_BADGE[v.severity]}`}>
                    {v.severity}
                  </span>
                </div>
                <p className="text-xs text-gray-600 mt-1">{v.message}</p>
                <p className="text-xs text-gray-400 mt-1">
                  Rule: <span className="font-mono">{v.rule_id}</span> · Confidence: {(v.confidence * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">
          📦 Object Detections ({detections.length})
        </h3>
        {detections.length === 0 ? (
          <p className="text-sm text-gray-500">No YOLO detections (VLM may still have analyzed the image).</p>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th className="px-3 py-2 text-left">Label</th>
                <th className="px-3 py-2 text-left">Confidence</th>
                <th className="px-3 py-2 text-left">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {detections.map((d, i) => (
                <tr key={i}>
                  <td className="px-3 py-2 font-mono text-xs">{d.label}</td>
                  <td className="px-3 py-2">{(d.confidence * 100).toFixed(0)}%</td>
                  <td className="px-3 py-2 text-gray-500">{d.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DetectionList;
