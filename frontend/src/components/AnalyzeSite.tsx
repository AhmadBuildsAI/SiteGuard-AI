import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { uploadInspection } from '../services/site';

const AnalyzeSite: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [siteName, setSiteName] = useState('Site A');
  const [siteArea, setSiteArea] = useState('');
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const f = e.target.files[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
    }
  };

  const handleSubmit = async () => {
    if (!file) { toast.error('Please select an image'); return; }
    setLoading(true);
    try {
      const insp = await uploadInspection(file, siteName, siteArea || undefined);
      toast.success(`Analysis complete — ${insp.violations.length} observation(s)`);
      navigate(`/results/${insp.id}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Analyze Site Image</h1>
        <p className="text-gray-500 text-sm">
          Upload a construction-site photo for safety and progress analysis
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp"
          onChange={handleFile}
          className="hidden"
        />

        {!preview ? (
          <div
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center cursor-pointer hover:border-orange-500 transition"
          >
            <div className="text-6xl mb-3">📸</div>
            <p className="font-medium text-gray-700">Click to upload site image</p>
            <p className="text-sm text-gray-500 mt-1">JPG, PNG, WebP · max 15 MB</p>
          </div>
        ) : (
          <div>
            <img src={preview} alt="Preview" className="max-h-80 w-full object-contain rounded-lg bg-gray-100" />
            <div className="flex justify-between items-center mt-2">
              <p className="text-sm text-gray-600 truncate">{file?.name}</p>
              <button
                onClick={() => { setFile(null); setPreview(null); }}
                className="text-xs text-red-600 hover:underline"
              >
                Remove
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Site Name</label>
            <input
              type="text"
              value={siteName}
              onChange={(e) => setSiteName(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Area (optional)</label>
            <input
              type="text"
              value={siteArea}
              onChange={(e) => setSiteArea(e.target.value)}
              placeholder="e.g., North Zone"
              className="w-full rounded-lg border border-gray-300 px-3 py-2"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={loading || !file}
            className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 font-semibold"
          >
            {loading ? '⏳ Analyzing...' : '🔍 Analyze Site'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalyzeSite;
