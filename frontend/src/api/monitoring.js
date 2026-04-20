import http from "./http";

export const evaluateMonitoring = async (payload) => {
  const response = await http.post("/monitoring/evaluate", payload);
  return response.data;
};