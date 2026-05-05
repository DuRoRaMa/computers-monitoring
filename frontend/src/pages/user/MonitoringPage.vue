<template>
  <div class="monitoring-page">
    <section class="input-card">
      <div class="section-header">
        <h2>Мониторинг состояния</h2>
        <p>
          Экспертная система и модуль машинного обучения рассчитываются всегда.
          При полном наборе признаков итоговый ответ даёт экспертная система,
          при неполном — модуль машинного обучения.
        </p>
      </div>

      <div class="form-grid">
        <label v-for="field in numericFields" :key="field.key" class="field-card">
          <span>{{ field.label }}</span>
          <input
            v-model="form[field.key]"
            class="number-input"
            :class="{ invalid: isFieldInvalid(field) }"
            type="number"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            :placeholder="`${field.min}–${field.max} ${field.unit}`"
          />
          <small class="field-hint">Диапазон: {{ field.min }}–{{ field.max }} {{ field.unit }}</small>
        </label>

        <label class="field-card">
          <span>Сервисы состояние</span>
          <select v-model="form.service_state">
            <option value="">Не указано</option>
            <option>Все работают</option>
            <option>Некоторые остановлены</option>
            <option>Критический сервис остановлен</option>
          </select>
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
        <button class="primary-btn" @click="runMonitoringAndSave" :disabled="loading">
          {{ loading ? "Выполняется..." : "Проанализировать и сохранить" }}
        </button>
      </div>

      <div v-if="success" class="success-message">{{ success }}</div>
      <div v-if="warning" class="warning-message">{{ warning }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </section>

    <!-- Итог -->
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

    <!-- Пропущенные признаки -->
    <section
      v-if="result?.missing_indicators && result.missing_indicators.length"
      class="details-card"
    >
      <div class="section-header">
        <h3>Незаполненные показатели</h3>
      </div>

      <p class="explanation-text">
        Пользователь не ввёл следующие показатели:
        {{ result.missing_indicators.join(", ") }}.
      </p>
    </section>

    <!-- Результат ЭС -->
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

    <!-- Детализация ЭС -->
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

    <!-- Результат МО -->
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
import { onMounted, reactive, ref } from "vue";
import { evaluateMonitoring } from "../../api/monitoring";
import { createObservation, getObservations } from "../../api/observations";

const loading = ref(false);
const historyLoading = ref(false);
const error = ref("");
const warning = ref("");
const success = ref("");
const result = ref(null);
const lastFinalState = ref(null);

const numericFields = [
  { key: "cpu_load", label: "CPU загрузка", min: 0, max: 100, step: 1, unit: "%" },
  { key: "ram_usage", label: "RAM занятость", min: 0, max: 100, step: 1, unit: "%" },
  { key: "cpu_temp", label: "CPU температура", min: 20, max: 120, step: 1, unit: "°C" },
  { key: "disk_speed", label: "Диск скорость", min: 0, max: 1000, step: 1, unit: "МБ/с" },
  { key: "disk_fill", label: "Диск заполнение", min: 0, max: 100, step: 1, unit: "%" },
  { key: "network_bandwidth", label: "Сеть пропускная", min: 0, max: 10000, step: 10, unit: "Мбит/с" },
  { key: "process_count", label: "Процессы количество", min: 0, max: 1000, step: 1, unit: "" },
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

const isFieldInvalid = (field) => {
  if (isEmpty(form[field.key])) return false;

  const value = Number(form[field.key]);
  return Number.isNaN(value) || value < field.min || value > field.max;
};

const validateForm = () => {
  const invalidField = numericFields.find((field) => isFieldInvalid(field));
  if (invalidField) {
    return `Показатель «${invalidField.label}» должен быть в диапазоне от ${invalidField.min} до ${invalidField.max}.`;
  }

  const hasAtLeastOneValue =
    numericFields.some((field) => !isEmpty(form[field.key])) || !isEmpty(form.service_state);

  if (!hasAtLeastOneValue) {
    return "Введите хотя бы один показатель для анализа.";
  }

  return null;
};

const buildPayload = () => {
  const payload = {
    previous_state: lastFinalState.value || null,
  };

  for (const field of numericFields) {
    if (!isEmpty(form[field.key])) {
      payload[field.key] =
        field.key === "process_count"
          ? Math.round(Number(form[field.key]))
          : Number(form[field.key]);
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
  await loadLastObservationState();
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
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 22px;
}

.field-card {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 16px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-card span {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.number-input,
.field-card select,
.readonly-value {
  width: 100%;
  min-height: 46px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 15px;
  background: white;
}

.number-input.invalid {
  border-color: #ef4444;
  background: #fef2f2;
}

.readonly-value {
  display: flex;
  align-items: center;
  color: #0f172a;
  font-weight: 700;
}

.field-hint {
  font-size: 13px;
  color: #64748b;
}

.actions-row {
  margin-top: 22px;
  display: flex;
  justify-content: flex-end;
}

.primary-btn {
  border: none;
  border-radius: 14px;
  min-height: 48px;
  padding: 0 20px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-weight: 800;
  cursor: pointer;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.success-message {
  margin-top: 14px;
  color: #0f766e;
  font-weight: 700;
}

.warning-message {
  margin-top: 14px;
  color: #b45309;
  font-weight: 700;
}

.error-message {
  margin-top: 14px;
  color: #dc2626;
  font-weight: 700;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.inner-grid {
  margin-top: 18px;
}

.result-card {
  background: white;
  border-radius: 22px;
  padding: 22px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
}

.result-card.small {
  padding: 18px;
}

.result-label {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 10px;
}

.result-value {
  color: #0f172a;
  font-size: 22px;
  font-weight: 800;
}

.table-wrap {
  overflow: auto;
  margin-top: 18px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.data-table th {
  color: #475569;
  font-size: 14px;
}

.explanation-text {
  margin: 18px 0 0 0;
  line-height: 1.7;
  color: #334155;
}

.probability-list {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.probability-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  background: #f8fafc;
}

.probability-name {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.probability-value {
  color: #059669;
  font-weight: 800;
  margin-bottom: 8px;
}

.probability-bar {
  width: 100%;
  height: 10px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}

.probability-fill {
  height: 100%;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

@media (max-width: 980px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }

  .actions-row {
    justify-content: stretch;
  }

  .primary-btn {
    width: 100%;
  }
}
</style>
