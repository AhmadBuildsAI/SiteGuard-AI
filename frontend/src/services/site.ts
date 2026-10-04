import api from './api';
import { InspectionListItem, InspectionDetail, AlertItem, DashboardData } from '../types';

export const listInspections = async (): Promise<InspectionListItem[]> => {
  const r = await api.get('/inspections/');
  return r.data;
};

export const getInspection = async (id: string): Promise<InspectionDetail> => {
  const r = await api.get(`/inspections/${id}`);
  return r.data;
};

export const uploadInspection = async (file: File, siteName: string, siteArea?: string): Promise<InspectionDetail> => {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('site_name', siteName);
  if (siteArea) fd.append('site_area', siteArea);
  const r = await api.post('/inspections/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return r.data;
};

export const getOverlay = async (id: string): Promise<string> => {
  const r = await api.get(`/inspections/${id}/overlay`);
  return r.data.overlay;
};

export const listAlerts = async (): Promise<AlertItem[]> => {
  const r = await api.get('/alerts/');
  return r.data;
};

export const acknowledgeAlert = async (id: string): Promise<AlertItem> => {
  const r = await api.post(`/alerts/${id}/acknowledge`);
  return r.data;
};

export const getDashboard = async (): Promise<DashboardData> => {
  const r = await api.get('/analytics/dashboard');
  return r.data;
};

export const getModelInfo = async () => {
  const r = await api.get('/analytics/model-info');
  return r.data;
};
