import http from "./http";

export const evaluateMonitoring = async (payload) => {
  const response = await http.post("/monitoring/evaluate", payload);
  return response.data;
};

export const evaluateMonitoringMlStub = async (payload) => {
  const response = await http.post("/monitoring/evaluate-ml-stub", payload);
  return response.data;
};