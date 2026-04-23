<template>
  <div class="monitoring-page">
    <section class="input-card">
      <div class="section-header">
        <h2>Мониторинг состояния</h2>
        <p>
          Выберите режим анализа, задайте значения показателей и запустите проверку
        </p>
      </div>

      <div class="mode-switch">
        <button
          class="mode-btn"
          :class="{ active: analysisMode === 'expert' }"
          @click="analysisMode = 'expert'"
        >
          Экспертная система
        </button>

        <button
          class="mode-btn"
          :class="{ active: analysisMode === 'ml' }"
          @click="analysisMode = 'ml'"
        >
          Машинное обучение
        </button>
      </div>

      <div class="form-grid">
        <div
          v-for="field in numericFields"
          :key="field.key"
          class="metric-card"
          :class="{ invalid: isFieldInvalid(field) }"
        >
          <div class="metric-header">
            <div>
              <div class="metric-title">{{ field.label }}</div>
              <div class="metric-hint">
                Диапазон: {{ field.min }}–{{ field.max }} {{ field.unit }}
              </div>
            </div>

            <div class="metric-value">
              {{ form[field.key] }}{{ field.unit ? " " + field.unit : "" }}
            </div>
          </div>

          <input
            v-model.number="form[field.key]"
            class="range-input"
            type="range"
            :min="field.min"
            :max="field.max"
            :step="field.step"
          />

          <input
            v-model.number="form[field.key]"
            class="number-input"
            :class="{ invalid: isFieldInvalid(field) }"
            type="number"
            :min="field.min"
            :max="field.max"
            :step="field.step"
          />

          <div v-if="isFieldInvalid(field)" class="field-error">
            Введите значение от {{ field.min }} до {{ field.max }}
            {{ field.unit }}
          </div>
        </div>

        <label class="field-card">
          <span>Сервисы состояние</span>
          <select v-model="form.service_state">
            <option>Все работают</option>
            <option>Некоторые остановлены</option>
            <option>Критический сервис остановлен</option>
          </select>
        </label>

        <label class="field-card">
          <span>Предыдущее состояние</span>
          <select v-model="form.previous_state">
            <option :value="null">Не задано</option>
            <option>Оптимальное</option>
            <option>Хорошее</option>
            <option>Критическое</option>
            <option>Критическое с риском отказа</option>
          </select>
        </label>
      </div>

      <div class="actions-row">
        <button class="primary-btn" @click="runAnalysis" :disabled="loading">
          {{
            loading
              ? "Выполняется..."
              : analysisMode === "expert"
              ? "Проанализировать и сохранить"
              : "Запустить ML-заглушку"
          }}
        </button>
      </div>

      <div v-if="success" class="success-message">{{ success }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </section>

    <section v-if="result" class="result-grid">
      <div class="result-card">
        <div class="result-label">Режим</div>
        <div class="result-value">
          {{ analysisMode === "expert" ? "Экспертная система" : "ML-заглушка" }}
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
    </section>

    <section v-if="result" class="details-card">
      <div class="section-header">
        <h3>Объяснение результата</h3>
      </div>

      <p class="explanation-text">{{ result.explanation }}</p>

      <div v-if="result.model_message" class="stub-note">
        {{ result.model_message }}
      </div>
    </section>

    <section
      v-if="result && result.indicator_results && result.indicator_results.length"
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

    <section
      v-if="result && result.probabilities && result.probabilities.length"
      class="details-card"
    >
      <div class="section-header">
        <h3>Демонстрационные вероятности ML-модуля</h3>
      </div>

      <div class="probability-list">
        <div
          v-for="item in result.probabilities"
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
import { reactive, ref } from "vue";
import {
  evaluateMonitoring,
  evaluateMonitoringMlStub,
} from "../../api/monitoring";
import { createObservation } from "../../api/observations";

const analysisMode = ref("expert");
const loading = ref(false);
const error = ref("");
const success = ref("");
const result = ref(null);

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
  cpu_load: 20,
  ram_usage: 35,
  cpu_temp: 45,
  disk_speed: 150,
  disk_fill: 40,
  network_bandwidth: 3000,
  process_count: 80,
  service_state: "Все работают",
  previous_state: null,
});

const isFieldInvalid = (field) => {
  const value = Number(form[field.key]);
  return Number.isNaN(value) || value < field.min || value > field.max;
};

const hasInvalidFields = () => {
  return numericFields.some((field) => isFieldInvalid(field));
};

const buildPayload = () => ({
  cpu_load: Number(form.cpu_load),
  ram_usage: Number(form.ram_usage),
  cpu_temp: Number(form.cpu_temp),
  disk_speed: Number(form.disk_speed),
  disk_fill: Number(form.disk_fill),
  network_bandwidth: Number(form.network_bandwidth),
  process_count: Math.round(Number(form.process_count)),
  service_state: form.service_state,
  previous_state: form.previous_state || null,
});

const runAnalysis = async () => {
  loading.value = true;
  error.value = "";
  success.value = "";
  result.value = null;

  try {
    if (hasInvalidFields()) {
      error.value = "Исправьте поля, выделенные красным.";
      return;
    }

    const payload = buildPayload();

    if (analysisMode.value === "expert") {
      const monitoringResult = await evaluateMonitoring(payload);
      result.value = monitoringResult;

      await createObservation({
        ...payload,
        final_state: monitoringResult.final_state,
        dynamics: monitoringResult.dynamics,
        diagnosis: monitoringResult.diagnosis,
        explanation: monitoringResult.explanation,
        indicator_results: monitoringResult.indicator_results,
      });

      success.value = "Наблюдение успешно сохранено в историю.";
    } else {
      const monitoringResult = await evaluateMonitoringMlStub(payload);
      result.value = monitoringResult;
      success.value = "Показан демонстрационный результат ML-модуля.";
    }
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail ||
      "Не удалось выполнить анализ. Проверь backend и корректность данных.";
  } finally {
    loading.value = false;
  }
};
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

.mode-switch {
  display: flex;
  gap: 12px;
  margin-top: 22px;
  margin-bottom: 22px;
  flex-wrap: wrap;
}

.mode-btn {
  border: 1px solid #cbd5e1;
  background: white;
  color: #334155;
  padding: 12px 16px;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
}

.mode-btn.active {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-color: transparent;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 16px;
}

.metric-card,
.field-card {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 16px;
  background: #f8fafc;
}

.metric-card.invalid {
  border-color: #ef4444;
  background: #fef2f2;
}

.metric-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.metric-title {
  font-weight: 800;
  color: #0f172a;
}

.metric-hint {
  margin-top: 4px;
  font-size: 13px;
  color: #64748b;
}

.metric-value {
  font-weight: 800;
  color: #059669;
  white-space: nowrap;
}

.range-input {
  width: 100%;
  margin-bottom: 12px;
}

.number-input,
.field-card select {
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

.field-error {
  margin-top: 10px;
  color: #dc2626;
  font-size: 13px;
  font-weight: 700;
}

.field-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-card span {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
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

.result-card {
  background: white;
  border-radius: 22px;
  padding: 22px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
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

.stub-note {
  margin-top: 16px;
  background: #fff7ed;
  border: 1px solid #fdba74;
  color: #9a3412;
  padding: 14px 16px;
  border-radius: 14px;
  font-weight: 600;
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