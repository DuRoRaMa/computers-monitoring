<template>
  <div class="monitoring-page">
    <section class="input-card">
      <div class="section-header">
        <h2>Мониторинг состояния</h2>
        <p>
          Вводимые значения проверяются по возможным значениям из базы знаний.
          При полном наборе признаков итоговый ответ даёт экспертная система,
          при неполном — модуль машинного обучения.
        </p>
      </div>

      <div v-if="constraintsError" class="warning-message">
        {{ constraintsError }}
      </div>

      <div class="form-grid">
        <label v-for="field in numericFields" :key="field.key" class="field-card">
          <span>{{ field.label }}</span>

          <input
            v-model="form[field.key]"
            class="number-input"
            :class="{ invalid: isFieldInvalid(field) }"
            type="number"
            :min="fieldMin(field)"
            :max="fieldMax(field)"
            step="1"
            :placeholder="fieldPlaceholder(field)"
          />

          <small class="field-hint">
            Возможное значение: {{ possibleValuesText(field.label) }}
          </small>
        </label>

        <label class="field-card">
          <span>Сервисы состояние</span>

          <select v-model="form.service_state">
            <option value="">Не указано</option>
            <option
              v-for="value in serviceStateOptions"
              :key="value"
              :value="value"
            >
              {{ value }}
            </option>
          </select>

          <small class="field-hint">
            Возможные значения: {{ possibleValuesText("Сервисы состояние") }}
          </small>
        </label>

        <div class="field-card readonly-card">
          <span>Предыдущее состояние</span>
          <div class="readonly-value">
            <template v-if="historyLoading">
              Загрузка предыдущего состояния...
            </template>
            <template v-else-if="lastFinalState">
              {{ lastFinalState }}
            </template>
            <template v-else>
              Не задано — первое наблюдение
            </template>
          </div>
          <small class="field-hint">
            При первом прогоне предыдущее состояние не учитывается
          </small>
        </div>
      </div>

      <div class="actions-row">
        <button
          class="primary-btn"
          @click="runMonitoringAndSave"
          :disabled="loading || constraintsLoading"
        >
          {{ loading ? "Выполняется..." : "Проанализировать и сохранить" }}
        </button>
      </div>

      <div v-if="success" class="success-message">{{ success }}</div>
      <div v-if="warning" class="warning-message">{{ warning }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </section>

    <section v-if="result" class="details-card">
      <div class="section-header">
        <h3>Итоговый ответ системы</h3>
      </div>

      <div class="result-grid">
        <div class="result-card">
          <div class="result-label">Источник итогового ответа</div>
          <div class="result-value">
            {{ result.final_source === "expert" ? "Экспертная система" : "Модуль МО" }}
          </div>
        </div>

        <div class="result-card">
          <div class="result-label">Итоговое состояние</div>
          <div class="result-value">{{ result.final_state }}</div>
        </div>

        <div class="result-card">
          <div class="result-label">Диагноз</div>
          <div class="result-value">{{ result.diagnosis }}</div>
        </div>
      </div>

      <p class="explanation-text">{{ result.explanation }}</p>
    </section>

    <section
      v-if="result?.missing_indicators && result.missing_indicators.length"
      class="details-card"
    >
      <div class="section-header">
        <h3>Пропущенные показатели</h3>
      </div>

      <div class="tag-list">
        <span
          v-for="item in result.missing_indicators"
          :key="item"
          class="tag"
        >
          {{ item }}
        </span>
      </div>
    </section>

    <section v-if="result?.expert_result" class="details-card">
      <div class="section-header">
        <h3>Результат экспертной системы</h3>
      </div>

      <div class="result-grid inner-grid">
        <div class="result-card small">
          <div class="result-label">Состояние</div>
          <div class="result-value">{{ result.expert_result.final_state }}</div>
        </div>

        <div class="result-card small">
          <div class="result-label">Динамика</div>
          <div class="result-value">
            {{ result.expert_result.dynamics ?? "Не учитывалась" }}
          </div>
        </div>

        <div class="result-card small">
          <div class="result-label">Диагноз</div>
          <div class="result-value">{{ result.expert_result.diagnosis }}</div>
        </div>
      </div>

      <p class="explanation-text">{{ result.expert_result.explanation }}</p>
    </section>

    <section
      v-if="result?.indicator_results && result.indicator_results.length"
      class="details-card"
    >
      <div class="section-header">
        <h3>Детализация по показателям</h3>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Показатель</th>
              <th>Значение</th>
              <th>Степень тяжести</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in result.indicator_results" :key="item.indicator">
              <td>{{ item.indicator }}</td>
              <td>{{ item.value }}</td>
              <td>{{ item.severity }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="result?.ml_result" class="details-card">
      <div class="section-header">
        <h3>Результат модуля машинного обучения</h3>
      </div>

      <div class="result-grid inner-grid">
        <div class="result-card small">
          <div class="result-label">Состояние</div>
          <div class="result-value">{{ result.ml_result.final_state }}</div>
        </div>

        <div class="result-card small">
          <div class="result-label">Динамика</div>
          <div class="result-value">
            {{ result.ml_result.dynamics ?? "Не учитывалась" }}
          </div>
        </div>

        <div class="result-card small">
          <div class="result-label">Диагноз</div>
          <div class="result-value">{{ result.ml_result.diagnosis }}</div>
        </div>
      </div>

      <p class="explanation-text">{{ result.ml_result.explanation }}</p>

      <div v-if="result.ml_result.probabilities?.length" class="probability-list">
        <div
          v-for="item in result.ml_result.probabilities"
          :key="item.label"
          class="probability-card"
        >
          <div class="probability-name">{{ item.label }}</div>
          <div class="probability-value">{{ Math.round(item.value * 100) }}%</div>
          <div class="probability-bar">
            <div
              class="probability-fill"
              :style="{ width: `${Math.round(item.value * 100)}%` }"
            />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { getAllPossibleValues } from "../../api/knowledge";
import { evaluateMonitoring } from "../../api/monitoring";
import { createObservation, getObservations } from "../../api/observations";

const loading = ref(false);
const historyLoading = ref(false);
const constraintsLoading = ref(false);
const error = ref("");
const warning = ref("");
const success = ref("");
const constraintsError = ref("");
const result = ref(null);
const lastFinalState = ref(null);
const possibleValuesByIndicatorName = ref({});

const numericFields = [
  { key: "cpu_load", label: "CPU загрузка", min: 0, max: 100, unit: "%" },
  { key: "ram_usage", label: "RAM занятость", min: 0, max: 100, unit: "%" },
  { key: "cpu_temp", label: "CPU температура", min: 20, max: 120, unit: "°C" },
  { key: "disk_speed", label: "Диск скорость", min: 0, max: 1000, unit: "МБ/с" },
  { key: "disk_fill", label: "Диск заполнение", min: 0, max: 100, unit: "%" },
  { key: "network_bandwidth", label: "Сеть пропускная", min: 0, max: 10000, unit: "Мбит/с" },
  { key: "process_count", label: "Процессы количество", min: 0, max: 1000, unit: "" },
];

const defaultServiceStateOptions = [
  "Все работают",
  "Некоторые остановлены",
  "Критический сервис остановлен",
];

const form = reactive({
  cpu_load: "",
  ram_usage: "",
  cpu_temp: "",
  disk_speed: "",
  disk_fill: "",
  network_bandwidth: "",
  process_count: "",
  service_state: "",
});

const isEmpty = (value) => value === "" || value === null || value === undefined;

const serviceStateOptions = computed(() => {
  const values = possibleValuesByIndicatorName.value["Сервисы состояние"] || [];
  return values.length ? values : defaultServiceStateOptions;
});

const loadKnowledgeConstraints = async () => {
  constraintsLoading.value = true;
  constraintsError.value = "";

  try {
    const rows = await getAllPossibleValues();

    const grouped = {};

    for (const row of rows) {
      const indicatorName = row.indicator_name;
      const valueText = row.value_text;

      if (!indicatorName || !valueText) {
        continue;
      }

      if (!grouped[indicatorName]) {
        grouped[indicatorName] = [];
      }

      grouped[indicatorName].push(valueText);
    }

    possibleValuesByIndicatorName.value = grouped;
  } catch (err) {
    console.error(err);
    constraintsError.value =
      err?.response?.data?.detail ||
      "Не удалось загрузить возможные значения из базы знаний.";
    possibleValuesByIndicatorName.value = {};
  } finally {
    constraintsLoading.value = false;
  }
};

const loadLastObservationState = async () => {
  historyLoading.value = true;

  try {
    const rows = await getObservations();
    lastFinalState.value = rows?.length ? rows[0].final_state : null;
  } catch (err) {
    console.error(err);
    lastFinalState.value = null;
  } finally {
    historyLoading.value = false;
  }
};

const parseRange = (valueText) => {
  const text = String(valueText || "").trim();

  if (
    text.length < 5 ||
    !["[", "("].includes(text[0]) ||
    !["]", ")"].includes(text[text.length - 1]) ||
    !text.includes(";")
  ) {
    return null;
  }

  const [left, right] = text.slice(1, -1).split(";");

  const min = Number(String(left).replace(",", ".").trim());
  const max = Number(String(right).replace(",", ".").trim());

  if (Number.isNaN(min) || Number.isNaN(max)) {
    return null;
  }

  return {
    min,
    max,
    minInclusive: text[0] === "[",
    maxInclusive: text[text.length - 1] === "]",
  };
};

const numberInRange = (value, range) => {
  const leftOk = range.minInclusive ? value >= range.min : value > range.min;
  const rightOk = range.maxInclusive ? value <= range.max : value < range.max;
  return leftOk && rightOk;
};

const possibleValues = (indicatorName) =>
  possibleValuesByIndicatorName.value[indicatorName] || [];

const possibleValuesText = (indicatorName) => {
  const values = possibleValues(indicatorName);
  return values.length ? values.join(", ") : "не заданы";
};

const possibleRanges = (indicatorName) =>
  possibleValues(indicatorName)
    .map(parseRange)
    .filter(Boolean);

const fieldMin = (field) => {
  const ranges = possibleRanges(field.label);

  if (!ranges.length) {
    return field.min;
  }

  return Math.min(...ranges.map((range) => range.min));
};

const fieldMax = (field) => {
  const ranges = possibleRanges(field.label);

  if (!ranges.length) {
    return field.max;
  }

  return Math.max(...ranges.map((range) => range.max));
};

const fieldPlaceholder = (field) => {
  const text = possibleValuesText(field.label);

  if (text === "не заданы") {
    return `${field.min}–${field.max} ${field.unit}`.trim();
  }

  return `${text} ${field.unit}`.trim();
};

const isFieldInvalid = (field) => {
  if (isEmpty(form[field.key])) {
    return false;
  }

  const value = Number(form[field.key]);

  if (Number.isNaN(value) || !Number.isInteger(value)) {
    return true;
  }

  const ranges = possibleRanges(field.label);

  if (!ranges.length) {
    return true;
  }

  return !ranges.some((range) => numberInRange(value, range));
};

const validateForm = () => {
  const hasAtLeastOneValue =
    numericFields.some((field) => !isEmpty(form[field.key])) ||
    !isEmpty(form.service_state);

  if (!hasAtLeastOneValue) {
    return "Введите хотя бы один показатель для анализа.";
  }

  for (const field of numericFields) {
    if (isEmpty(form[field.key])) {
      continue;
    }

    const value = Number(form[field.key]);

    if (Number.isNaN(value) || !Number.isInteger(value)) {
      return `Показатель «${field.label}» должен быть целым числом.`;
    }

    const ranges = possibleRanges(field.label);

    if (!ranges.length) {
      return `Для показателя «${field.label}» сначала задайте возможное значение.`;
    }

    if (!ranges.some((range) => numberInRange(value, range))) {
      return `Показатель «${field.label}» должен входить в возможное значение: ${possibleValuesText(field.label)}.`;
    }
  }

  if (!isEmpty(form.service_state)) {
    const allowedServices = possibleValues("Сервисы состояние");

    if (!allowedServices.length) {
      return "Для показателя «Сервисы состояние» сначала задайте возможное значение.";
    }

    if (!allowedServices.includes(form.service_state)) {
      return `Показатель «Сервисы состояние» должен входить в возможное значение: ${allowedServices.join(", ")}.`;
    }
  }

  return null;
};

const buildPayload = () => {
  const payload = {
    previous_state: lastFinalState.value || null,
  };

  for (const field of numericFields) {
    if (!isEmpty(form[field.key])) {
      payload[field.key] = Number(form[field.key]);
    }
  }

  if (!isEmpty(form.service_state)) {
    payload.service_state = form.service_state;
  }

  return payload;
};

const runMonitoringAndSave = async () => {
  loading.value = true;
  error.value = "";
  warning.value = "";
  success.value = "";
  result.value = null;

  try {
    const validationError = validateForm();

    if (validationError) {
      error.value = validationError;
      return;
    }

    const payload = buildPayload();
    const monitoringResult = await evaluateMonitoring(payload);
    result.value = monitoringResult;

    try {
      const resolvedInput = monitoringResult.resolved_input || payload;

      await createObservation({
        ...resolvedInput,
        previous_state: lastFinalState.value || null,
        final_state: monitoringResult.final_state,
        dynamics: monitoringResult.dynamics,
        diagnosis: monitoringResult.diagnosis,
        explanation: monitoringResult.explanation,
        indicator_results: (monitoringResult.indicator_results || []).map((item) => ({
          indicator: item.indicator,
          value: String(item.value),
          severity: item.severity,
        })),
      });

      success.value = "Наблюдение успешно сохранено в историю.";
      lastFinalState.value = monitoringResult.final_state;
    } catch (saveErr) {
      console.error(saveErr);
      warning.value =
        saveErr?.response?.data?.detail ||
        "Анализ выполнен, но сохранить наблюдение в историю не удалось.";
    }
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось выполнить анализ.";
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await Promise.all([
    loadKnowledgeConstraints(),
    loadLastObservationState(),
  ]);
});
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-card,
.details-card {
  background: white;
  border-radius: 22px;
  padding: 24px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
}

.section-header h2,
.section-header h3 {
  margin: 0;
  color: #0f172a;
}

.section-header p {
  margin: 8px 0 0 0;
  color: #64748b;
  line-height: 1.5;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 22px;
}

.field-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  background: #f8fafc;
}

.field-card span {
  font-weight: 700;
  color: #0f172a;
}

.number-input,
select {
  min-height: 42px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 0 12px;
  font-size: 14px;
  background: white;
}

.number-input.invalid {
  border-color: #ef4444;
  background: #fef2f2;
}

.field-hint {
  color: #64748b;
  line-height: 1.4;
}

.readonly-card {
  background: #f1f5f9;
}

.readonly-value {
  min-height: 42px;
  display: flex;
  align-items: center;
  color: #334155;
}

.actions-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.primary-btn {
  border: 0;
  border-radius: 14px;
  padding: 12px 18px;
  background: #0f172a;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message,
.warning-message,
.error-message {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 14px;
}

.success-message {
  background: #ecfdf5;
  color: #047857;
}

.warning-message {
  background: #fffbeb;
  color: #92400e;
}

.error-message {
  background: #fef2f2;
  color: #b91c1c;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 1fr));
  gap: 14px;
  margin-top: 16px;
}

.inner-grid {
  grid-template-columns: repeat(3, minmax(140px, 1fr));
}

.result-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 14px;
}

.result-card.small {
  padding: 12px;
}

.result-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 6px;
}

.result-value {
  color: #0f172a;
  font-weight: 800;
}

.explanation-text {
  color: #334155;
  line-height: 1.6;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.tag {
  background: #e0f2fe;
  color: #075985;
  border-radius: 999px;
  padding: 8px 12px;
  font-weight: 700;
}

.table-wrap {
  overflow-x: auto;
  margin-top: 14px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  border-bottom: 1px solid #e2e8f0;
  padding: 12px;
  text-align: left;
}

.data-table th {
  color: #475569;
  background: #f8fafc;
}

.probability-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.probability-card {
  display: grid;
  grid-template-columns: 1fr 60px 2fr;
  gap: 12px;
  align-items: center;
}

.probability-name {
  font-weight: 700;
}

.probability-value {
  color: #475569;
}

.probability-bar {
  height: 10px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}

.probability-fill {
  height: 100%;
  background: #0f172a;
}

@media (max-width: 900px) {
  .form-grid,
  .result-grid,
  .inner-grid {
    grid-template-columns: 1fr;
  }

  .probability-card {
    grid-template-columns: 1fr;
  }
}
</style>

