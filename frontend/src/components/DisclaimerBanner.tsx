import React from 'react';

const DisclaimerBanner: React.FC = () => (
  <div className="bg-amber-50 border-b border-amber-200">
    <div className="max-w-7xl mx-auto px-4 py-2 text-xs text-amber-800">
      ⚠️ <strong>Human review required.</strong> All alerts are potential observations, not confirmed violations.
      A qualified on-site safety inspector must verify every alert before any action is taken.
    </div>
  </div>
);

export default DisclaimerBanner;
