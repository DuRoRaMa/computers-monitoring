<template>
  <div class="monitoring-page">
    <section class="input-card">
      <div class="section-header">
        <h2>Мониторинг состояния</h2>
        <p>Введите значения показателей, запустите анализ и сохраните наблюдение</p>
      </div>

      <div class="form-grid">
        <label class="field">
          <span>CPU загрузка</span>
          <input v-model.number="form.cpu_load" type="number" />
        </label>

        <label class="field">
          <span>RAM занятость</span>
          <input v-model.number="form.ram_usage" type="number" />
        </label>

        <label class="field">
          <span>CPU температура</span>
          <input v-model.number="form.cpu_temp" type="number" />
        </label>

        <label class="field">
          <span>Диск скорость</span>
          <input v-model.number="form.disk_speed" type="number" />
        </label>

        <label class="field">
          <span>Диск заполнение</span>
          <input v-model.number="form.disk_fill" type="number" />
        </label>

        <label class="field">
          <span>Сеть пропускная</span>
          <input v-model.number="form.network_bandwidth" type="number" />
        </label>

        <label class="field">
          <span>Процессы количество</span>
          <input v-model.number="form.process_count" type="number" />
        </label>

        <label class="field">
          <span>Сервисы состояние</span>
          <select v-model="form.service_state">
            <option>Все работают</option>
            <option>Некоторые остановлены</option>
            <option>Критический сервис остановлен</option>
          </select>
        </label>

        <label class="field field-wide">
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
        <button class="primary-btn" @click="runMonitoringAndSave" :disabled="loading">
          {{ loading ? "Выполняется..." : "Проанализировать и сохранить" }}
        </button>
      </div>

      <div v-if="success" class="success-message">{{ success }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </section>

    <section v-if="result" class="result-grid">
      <div class="result-card">
        <div class="result-label">Итоговое состояние</div>
        <div class="result-value">{{ result.final_state }}</div>
      </div>

      <div class="result-card">
        <div class="result-label">Динамика</div>
        <div class="result-value">
          {{ result.dynamics ?? "Не определялась" }}
        </div>
      </div>

      <div class="result-card">
        <div class="result-label">Диагноз</div>
        <div class="result-value">{{ result.diagnosis }}</div>
      </div>
    </section>

    <section v-if="result" class="details-card">
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

    <section v-if="result" class="details-card">
      <div class="section-header">
        <h3>Объяснение системы</h3>
      </div>

      <p class="explanation-text">
        {{ result.explanation }}
      </p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { evaluateMonitoring } from "../../api/monitoring";
import { createObservation } from "../../api/observations";

const loading = ref(false);
const error = ref("");
const success = ref("");
const result = ref(null);

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

const runMonitoringAndSave = async () => {
  loading.value = true;
  error.value = "";
  success.value = "";
  result.value = null;

  try {
    const payload = {
      ...form,
      previous_state: form.previous_state || null,
    };

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
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail ||
      "Не удалось выполнить анализ и сохранить наблюдение.";
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 22px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field span {
  font-size: 14px;
  font-weight: 700;
  color: #334155;
}

.field input,
.field select {
  min-height: 46px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 15px;
}

.field-wide {
  grid-column: 1 / -1;
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

@media (max-width: 980px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>