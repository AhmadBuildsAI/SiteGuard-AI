export interface Detection {
  label: string;
  bbox: number[];
  confidence: number;
  source: string;
}

export interface Violation {
  rule_id: string;
  severity: string;
  title: string;
  message: string;
  evidence: Record<string, any>;
  confidence: number;
  vlm_observation?: string | null;
}

export interface InspectionListItem {
  id: string;
  inspection_ref: string;
  site_name: string;
  safety_score: number;
  risk_level: string;
  worker_count: number;
  violation_count: number;
  filename: string | null;
  image_url: string | null;
  created_at: string;
}

export interface InspectionDetail extends InspectionListItem {
  site_area: string | null;
  image_width: number | null;
  image_height: number | null;
  detections: Detection[];
  violations: Violation[];
  scene_analysis: Record<string, any> | null;
  ppe_score: number;
  zone_score: number;
  equipment_score: number;
  organization_score: number;
  helmet_count: number;
  vest_count: number;
  equipment_count: number;
  vlm_used: string;
  explanation: string | null;
  disclaimer: string;
}

export interface AlertItem {
  id: string;
  inspection_id: string;
  inspection_ref: string;
  rule_id: string;
  severity: string;
  title: string;
  message: string;
  vlm_observation: string | null;
  confidence: number;
  is_acknowledged: boolean;
  created_at: string;
}

export interface DashboardData {
  total_inspections: number;
  total_alerts: number;
  avg_safety_score: number;
  critical_alerts: number;
  high_alerts: number;
  risk_distribution: { level: string; count: number }[];
  safety_trend: { date: string; score: number }[];
  recent_inspections: {
    id: string;
    ref: string;
    site_name: string;
    safety_score: number;
    risk_level: string;
    violation_count: number;
    created_at: string;
  }[];
}
