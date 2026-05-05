import http from "./http";

export const createObservation = async (payload) => {
  const response = await http.post("/observations", payload);
  return response.data;
};

export const getObservations = async () => {
  const response = await http.get("/observations");
  return response.data;
};

export const getObservationById = async (id) => {
  const response = await http.get(`/observations/${id}`);
  return response.data;
};

// совместимость со старым кодом
export const getObservation = async (id) => {
  return getObservationById(id);
};

export const getObservationDiagnosis = async (id) => {
  const response = await http.get(`/observations/${id}/diagnosis`);
  return response.data;
};

export const getLastObservation = async () => {
  const rows = await getObservations();
  return rows?.length ? rows[0] : null;
};
