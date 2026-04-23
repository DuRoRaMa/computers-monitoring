import http from "./http";

/* ------------------ Seed ------------------ */
export const seedBasicKnowledge = async () => {
  const response = await http.post("/knowledge/seed-basic");
  return response.data;
};

export const seedRules = async () => {
  const response = await http.post("/knowledge/seed-rules");
  return response.data;
};

/* ------------------ Diagnoses ------------------ */
export const getDiagnoses = async () => {
  const response = await http.get("/knowledge/diagnoses");
  return response.data;
};

export const createDiagnosis = async (name) => {
  const response = await http.post("/knowledge/diagnoses", { name });
  return response.data;
};

export const deleteDiagnosis = async (id) => {
  const response = await http.delete(`/knowledge/diagnoses/${id}`);
  return response.data;
};

/* ------------------ Indicators ------------------ */
export const getIndicators = async () => {
  const response = await http.get("/knowledge/indicators");
  return response.data;
};

export const createIndicator = async (name, valueType) => {
  const response = await http.post("/knowledge/indicators", {
    name,
    value_type: valueType,
  });
  return response.data;
};

export const deleteIndicator = async (id) => {
  const response = await http.delete(`/knowledge/indicators/${id}`);
  return response.data;
};

/* ------------------ Severity names ------------------ */
export const getSeverityNames = async () => {
  const response = await http.get("/knowledge/severity-names");
  return response.data;
};

export const createSeverityName = async (name) => {
  const response = await http.post("/knowledge/severity-names", { name });
  return response.data;
};

export const deleteSeverityName = async (id) => {
  const response = await http.delete(`/knowledge/severity-names/${id}`);
  return response.data;
};

/* ------------------ Possible values ------------------ */
export const getPossibleValues = async (indicatorId) => {
  const response = await http.get("/knowledge/possible-values", {
    params: { indicator_id: indicatorId },
  });
  return response.data;
};

export const createPossibleValue = async (indicatorId, valueText) => {
  const response = await http.post("/knowledge/possible-values", {
    indicator_id: indicatorId,
    value_text: valueText,
  });
  return response.data;
};

export const deletePossibleValue = async (id) => {
  const response = await http.delete(`/knowledge/possible-values/${id}`);
  return response.data;
};

/* ------------------ Normal values ------------------ */
export const getNormalValues = async (indicatorId) => {
  const response = await http.get("/knowledge/normal-values", {
    params: { indicator_id: indicatorId },
  });
  return response.data;
};

export const createNormalValue = async (indicatorId, valueText) => {
  const response = await http.post("/knowledge/normal-values", {
    indicator_id: indicatorId,
    value_text: valueText,
  });
  return response.data;
};

export const deleteNormalValue = async (id) => {
  const response = await http.delete(`/knowledge/normal-values/${id}`);
  return response.data;
};

/* ------------------ State characteristics ------------------ */
export const getStateCharacteristics = async (diagnosisId) => {
  const response = await http.get("/knowledge/state-characteristics", {
    params: { diagnosis_id: diagnosisId },
  });
  return response.data;
};

export const saveStateCharacteristics = async (diagnosisId, indicatorIds) => {
  const response = await http.put("/knowledge/state-characteristics", {
    diagnosis_id: diagnosisId,
    indicator_ids: indicatorIds,
  });
  return response.data;
};

/* ------------------ Severity values ------------------ */
export const getSeverityValues = async (severityId) => {
  const response = await http.get("/knowledge/severity-values", {
    params: { severity_id: severityId },
  });
  return response.data;
};

export const saveSeverityValues = async (severityId, rows) => {
  const response = await http.put("/knowledge/severity-values", {
    severity_id: severityId,
    rows,
  });
  return response.data;
};

/* ------------------ Diagnosis values ------------------ */
export const getDiagnosisValues = async (diagnosisId) => {
  const response = await http.get("/knowledge/diagnosis-values", {
    params: { diagnosis_id: diagnosisId },
  });
  return response.data;
};

export const saveDiagnosisValues = async (diagnosisId, rows) => {
  const response = await http.put("/knowledge/diagnosis-values", {
    diagnosis_id: diagnosisId,
    rows,
  });
  return response.data;
};