<template>
  <div class="history-page">
    <div class="page-header">
      <div>
        <h2>История наблюдений</h2>
        <p>Результаты мониторинга и графики динамики состояния системы</p>
      </div>
    </div>

    <div v-if="loading" class="info-card">Загрузка истории наблюдений...</div>
    <div v-else-if="error" class="error-card">{{ error }}</div>
    <div v-else-if="!observationDetails.length" class="info-card">
      История наблюдений пуста
    </div>

    <template v-else>
      <section class="summary-grid">
        <div class="summary-card">
          <div class="summary-label">Всего наблюдений</div>
          <div class="summary-value">{{ observationDetails.length }}</div>
        </div>

        <div class="summary-card">
          <div class="summary-label">Последнее состояние</div>
          <div class="summary-value">{{ latestObservation.result.final_state }}</div>
        </div>

        <div class="summary-card">
          <div class="summary-label">Последний диагноз</div>
          <div class="summary-value">{{ latestObservation.result.diagnosis }}</div>
        </div>

        <div class="summary-card">
          <div class="summary-label">Последняя запись</div>
          <div class="summary-value">{{ formatDateTime(latestObservation.created_at) }}</div>
        </div>
      </section>

      <section class="charts-grid">
        <div class="chart-card">
          <div class="card-header">
            <h3>Динамика итогового состояния</h3>
            <p>Изменение общего состояния по наблюдениям</p>
          </div>
          <div class="chart-box">
            <canvas ref="stateChartCanvas"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="card-header with-control">
            <div>
              <h3>Динамика значений показателя</h3>
              <p>Изменение выбранного показателя по наблюдениям</p>
            </div>

            <select v-model="selectedIndicatorKey" class="select-control">
              <option
                v-for="item in indicatorOptions"
                :key="item.key"
                :value="item.key"
              >
                {{ item.label }}
              </option>
            </select>
          </div>
          <div class="chart-box">
            <canvas ref="indicatorChartCanvas"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="card-header">
            <h3>Динамика диагнозов</h3>
            <p>Как менялся диагноз по наблюдениям</p>
          </div>
          <div class="chart-box">
            <canvas ref="diagnosisChartCanvas"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="card-header">
            <h3>Распределение итоговых состояний</h3>
            <p>Структура состояний за всю историю наблюдений</p>
          </div>
          <div class="chart-box">
            <canvas ref="distributionChartCanvas"></canvas>
          </div>
        </div>
      </section>

      <section class="content-grid">
        <div class="history-list-card">
          <div class="card-header">
            <h3>Список наблюдений</h3>
            <p>Выберите запись, чтобы посмотреть детали</p>
          </div>

          <div class="history-list">
            <button
              v-for="item in observationSummaries"
              :key="item.id"
              class="history-item"
              :class="{ active: selectedObservationId === item.id }"
              @click="selectedObservationId = item.id"
            >
              <div class="history-item-top">
                <span class="history-date">{{ formatDateTime(item.created_at) }}</span>
                <span class="history-state">{{ item.final_state }}</span>
              </div>
              <div class="history-item-bottom">
                <span>{{ item.diagnosis }}</span>
                <span>{{ item.dynamics || "Без динамики" }}</span>
              </div>
            </button>
          </div>
        </div>

        <div v-if="selectedObservation" class="details-card">
          <div class="card-header">
            <h3>Детали наблюдения</h3>
            <p>{{ formatDateTime(selectedObservation.created_at) }}</p>
          </div>

          <div class="details-summary-grid">
            <div class="mini-card">
              <div class="mini-label">Итоговое состояние</div>
              <div class="mini-value">{{ selectedObservation.result.final_state }}</div>
            </div>

            <div class="mini-card">
              <div class="mini-label">Диагноз</div>
              <div class="mini-value">{{ selectedObservation.result.diagnosis }}</div>
            </div>

            <div class="mini-card">
              <div class="mini-label">Динамика</div>
              <div class="mini-value">
                {{ selectedObservation.result.dynamics || "Не определялась" }}
              </div>
            </div>

            <div class="mini-card">
              <div class="mini-label">Сервисы</div>
              <div class="mini-value">{{ selectedObservation.input.service_state }}</div>
            </div>
          </div>

          <div class="details-section">
            <h4>Пояснение</h4>
            <p class="explanation-text">{{ selectedObservation.result.explanation }}</p>
          </div>

          <div class="details-section">
            <h4>Введённые значения</h4>
            <div class="data-grid">
              <div class="data-row">
                <span>CPU загрузка</span>
                <strong>{{ selectedObservation.input.cpu_load }}</strong>
              </div>
              <div class="data-row">
                <span>RAM занятость</span>
                <strong>{{ selectedObservation.input.ram_usage }}</strong>
              </div>
              <div class="data-row">
                <span>CPU температура</span>
                <strong>{{ selectedObservation.input.cpu_temp }}</strong>
              </div>
              <div class="data-row">
                <span>Диск скорость</span>
                <strong>{{ selectedObservation.input.disk_speed }}</strong>
              </div>
              <div class="data-row">
                <span>Диск заполнение</span>
                <strong>{{ selectedObservation.input.disk_fill }}</strong>
              </div>
              <div class="data-row">
                <span>Сеть пропускная</span>
                <strong>{{ selectedObservation.input.network_bandwidth }}</strong>
              </div>
              <div class="data-row">
                <span>Процессы количество</span>
                <strong>{{ selectedObservation.input.process_count }}</strong>
              </div>
              <div class="data-row">
                <span>Предыдущее состояние</span>
                <strong>{{ selectedObservation.input.previous_state || "Не задано" }}</strong>
              </div>
            </div>
          </div>

          <div class="details-section">
            <h4>Детализация по показателям</h4>
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
                  <tr
                    v-for="item in selectedObservation.result.indicator_results"
                    :key="`${selectedObservation.id}-${item.indicator}`"
                  >
                    <td>{{ item.indicator }}</td>
                    <td>{{ item.value }}</td>
                    <td>{{ item.severity }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { Chart, registerables } from "chart.js";
import { getObservation, getObservations } from "../../api/observations";

Chart.register(...registerables);

const loading = ref(false);
const error = ref("");

const observationSummaries = ref([]);
const observationDetails = ref([]);
const selectedObservationId = ref(null);
const selectedIndicatorKey = ref("cpu_temp");

const stateChartCanvas = ref(null);
const indicatorChartCanvas = ref(null);
const diagnosisChartCanvas = ref(null);
const distributionChartCanvas = ref(null);

let stateChart = null;
let indicatorChart = null;
let diagnosisChart = null;
let distributionChart = null;

const indicatorOptions = [
  { key: "cpu_load", label: "CPU загрузка" },
  { key: "ram_usage", label: "RAM занятость" },
  { key: "cpu_temp", label: "CPU температура" },
  { key: "disk_speed", label: "Диск скорость" },
  { key: "disk_fill", label: "Диск заполнение" },
  { key: "network_bandwidth", label: "Сеть пропускная" },
  { key: "process_count", label: "Процессы количество" },
];

const indicatorLabelMap = {
  cpu_load: "CPU загрузка",
  ram_usage: "RAM занятость",
  cpu_temp: "CPU температура",
  disk_speed: "Диск скорость",
  disk_fill: "Диск заполнение",
  network_bandwidth: "Сеть пропускная",
  process_count: "Процессы количество",
};

const stateOrderMap = {
  "Оптимальное": 1,
  "Хорошее": 2,
  "Критическое": 3,
  "Критическое с риском отказа": 4,
};

const diagnosisOrderMap = {
  "Исправен": 1,
  "Требует обслуживания": 2,
};

const orderedDetails = computed(() => {
  return [...observationDetails.value].sort(
    (a, b) => new Date(a.created_at) - new Date(b.created_at)
  );
});

const latestObservation = computed(() => {
  if (!observationDetails.value.length) return null;
  return [...observationDetails.value].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  )[0];
});

const selectedObservation = computed(() => {
  return observationDetails.value.find((x) => x.id === selectedObservationId.value) || null;
});

const formatDateTime = (value) => {
  return new Date(value).toLocaleString("ru-RU");
};

const shortDateTime = (value) => {
  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const destroyCharts = () => {
  if (stateChart) {
    stateChart.destroy();
    stateChart = null;
  }
  if (indicatorChart) {
    indicatorChart.destroy();
    indicatorChart = null;
  }
  if (diagnosisChart) {
    diagnosisChart.destroy();
    diagnosisChart = null;
  }
  if (distributionChart) {
    distributionChart.destroy();
    distributionChart = null;
  }
};

const renderStateChart = () => {
  if (!stateChartCanvas.value || !orderedDetails.value.length) return;

  const labels = orderedDetails.value.map((item) => shortDateTime(item.created_at));
  const values = orderedDetails.value.map(
    (item) => stateOrderMap[item.result.final_state] ?? null
  );

  if (!values.some((v) => v !== null)) return;

  stateChart = new Chart(stateChartCanvas.value.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Итоговое состояние",
          data: values,
          borderColor: "#2563eb",
          backgroundColor: "rgba(37, 99, 235, 0.18)",
          pointBackgroundColor: "#2563eb",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 5,
          borderWidth: 3,
          tension: 0.25,
          fill: false,
          spanGaps: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: {
          display: true,
        },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.raw;
              const pair = Object.entries(stateOrderMap).find(([, v]) => v === value);
              return pair ? ` ${pair[0]}` : ` ${value}`;
            },
          },
        },
      },
      scales: {
        x: {
          ticks: {
            maxRotation: 0,
            autoSkip: true,
          },
        },
        y: {
          min: 1,
          max: 4,
          ticks: {
            stepSize: 1,
            callback(value) {
              const pair = Object.entries(stateOrderMap).find(([, v]) => v === value);
              return pair ? pair[0] : value;
            },
          },
        },
      },
    },
  });
};

const renderIndicatorChart = () => {
  if (!indicatorChartCanvas.value || !orderedDetails.value.length) return;

  const key = selectedIndicatorKey.value || "cpu_temp";
  const labels = orderedDetails.value.map((item) => shortDateTime(item.created_at));
  const values = orderedDetails.value.map((item) => item.input[key]);

  if (!values.some((v) => v !== null && v !== undefined)) return;

  indicatorChart = new Chart(indicatorChartCanvas.value.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: indicatorLabelMap[key],
          data: values,
          borderColor: "#0ea5e9",
          backgroundColor: "rgba(14, 165, 233, 0.18)",
          pointBackgroundColor: "#0ea5e9",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 5,
          borderWidth: 3,
          tension: 0.25,
          fill: false,
          spanGaps: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: {
          display: true,
        },
      },
    },
  });
};

const renderDiagnosisChart = () => {
  if (!diagnosisChartCanvas.value || !orderedDetails.value.length) return;

  const labels = orderedDetails.value.map((item) => shortDateTime(item.created_at));
  const values = orderedDetails.value.map(
    (item) => diagnosisOrderMap[item.result.diagnosis] ?? null
  );

  if (!values.some((v) => v !== null)) return;

  diagnosisChart = new Chart(diagnosisChartCanvas.value.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Диагноз",
          data: values,
          borderColor: "#7c3aed",
          backgroundColor: "rgba(124, 58, 237, 0.18)",
          pointBackgroundColor: "#7c3aed",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 5,
          borderWidth: 3,
          stepped: true,
          fill: false,
          spanGaps: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: {
          display: true,
        },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.raw;
              const pair = Object.entries(diagnosisOrderMap).find(([, v]) => v === value);
              return pair ? ` ${pair[0]}` : ` ${value}`;
            },
          },
        },
      },
      scales: {
        x: {
          ticks: {
            maxRotation: 0,
            autoSkip: true,
          },
        },
        y: {
          min: 1,
          max: 2,
          ticks: {
            stepSize: 1,
            callback(value) {
              const pair = Object.entries(diagnosisOrderMap).find(([, v]) => v === value);
              return pair ? pair[0] : value;
            },
          },
        },
      },
    },
  });
};

const renderDistributionChart = () => {
  if (!distributionChartCanvas.value || !orderedDetails.value.length) return;

  const distribution = orderedDetails.value.reduce((acc, item) => {
    const state = item.result.final_state;
    acc[state] = (acc[state] || 0) + 1;
    return acc;
  }, {});

  const labels = Object.keys(distribution);
  const values = Object.values(distribution);

  if (!labels.length) return;

  distributionChart = new Chart(distributionChartCanvas.value.getContext("2d"), {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: [
            "#16a34a",
            "#2563eb",
            "#f59e0b",
            "#dc2626",
          ],
          borderColor: "#ffffff",
          borderWidth: 3,
          hoverOffset: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        legend: {
          display: true,
          position: "bottom",
        },
      },
    },
  });
};

const renderAllCharts = async () => {
  await nextTick();
  await new Promise((resolve) => requestAnimationFrame(resolve));

  destroyCharts();

  if (!orderedDetails.value.length) return;

  renderStateChart();
  renderIndicatorChart();
  renderDiagnosisChart();
  renderDistributionChart();
};

const loadHistory = async () => {
  loading.value = true;
  error.value = "";

  try {
    const summaries = await getObservations();
    observationSummaries.value = summaries || [];

    const details = await Promise.all(
      observationSummaries.value.map((item) => getObservation(item.id))
    );

    observationDetails.value = details || [];

    if (!selectedIndicatorKey.value) {
      selectedIndicatorKey.value = "cpu_temp";
    }

    if (observationSummaries.value.length) {
      selectedObservationId.value = observationSummaries.value[0].id;
    }

    loading.value = false;
    await renderAllCharts();
    return;
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось загрузить историю наблюдений.";
  } finally {
    loading.value = false;
  }
};

watch(selectedIndicatorKey, async () => {
  if (loading.value) return;

  await nextTick();
  await new Promise((resolve) => requestAnimationFrame(resolve));

  if (indicatorChart) {
    indicatorChart.destroy();
    indicatorChart = null;
  }

  renderIndicatorChart();
});

onMounted(async () => {
  await loadHistory();
});

onBeforeUnmount(() => {
  destroyCharts();
});
</script>

<style scoped>
.history-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 28px;
}

.page-header p {
  margin: 8px 0 0 0;
  color: #64748b;
}

.info-card,
.error-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.error-card {
  color: #b91c1c;
  background: #fef2f2;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-card,
.chart-card,
.history-list-card,
.details-card {
  background: white;
  border-radius: 22px;
  padding: 22px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.summary-label {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 10px;
}

.summary-value {
  color: #0f172a;
  font-size: 22px;
  font-weight: 800;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-box {
  position: relative;
  width: 100%;
  height: 320px;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  color: #0f172a;
}

.card-header p {
  margin: 6px 0 0 0;
  color: #64748b;
}

.with-control {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.select-control {
  min-width: 220px;
  min-height: 42px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 0 12px;
  background: white;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 820px;
  overflow-y: auto;
}

.history-item {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #f8fafc;
  padding: 14px;
  text-align: left;
  cursor: pointer;
}

.history-item.active {
  background: #eff6ff;
  border-color: #60a5fa;
}

.history-item-top,
.history-item-bottom {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.history-item-top {
  margin-bottom: 8px;
}

.history-date {
  font-size: 13px;
  color: #64748b;
}

.history-state {
  font-weight: 700;
  color: #0f172a;
}

.history-item-bottom {
  font-size: 13px;
  color: #475569;
}

.details-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.mini-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
}

.mini-label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 8px;
}

.mini-value {
  color: #0f172a;
  font-size: 18px;
  font-weight: 800;
}

.details-section {
  margin-top: 22px;
}

.details-section h4 {
  margin: 0 0 12px 0;
  color: #0f172a;
}

.explanation-text {
  color: #334155;
  line-height: 1.65;
  margin: 0;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.data-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: #f8fafc;
}

.table-wrap {
  overflow-x: auto;
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

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .details-summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 760px) {
  .summary-grid,
  .details-summary-grid,
  .data-grid {
    grid-template-columns: 1fr;
  }

  .with-control {
    flex-direction: column;
  }

  .select-control {
    width: 100%;
  }
}
</style>
