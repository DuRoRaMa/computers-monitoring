import http from "./http";

export const createObservation = async (payload) => {
  const response = await http.post("/observations", payload);
  return response.data;
};

export const getObservations = async () => {
  const response = await http.get("/observations");
  return response.data;
};

export const getObservation = async (id) => {
  const response = await http.get(`/observations/${id}`);
  return response.data;
};

export const getObservationDiagnosis = async (id) => {
  const response = await http.get(`/observations/${id}/diagnosis`);
  return response.data;
};