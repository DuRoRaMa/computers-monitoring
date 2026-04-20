<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Постановка диагноза</h2>
        <p>Выберите сохранённое наблюдение и получите диагноз по нему</p>
      </div>

      <div class="controls">
        <select v-model="selectedObservationId" class="select-input">
          <option disabled value="">Выберите наблюдение</option>
          <option v-for="item in observations" :key="item.id" :value="item.id">
            #{{ item.id }} — {{ formatDate(item.created_at) }}
          </option>
        </select>
      </div>

      <div class="action-row">
        <button class="primary-btn" @click="handleLoadDiagnosis">
          Определить диагноз
        </button>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>

      <div v-if="diagnosisData" class="result-card">
        <div class="result-block">
          <div class="label">Дата наблюдения</div>
          <div class="value">{{ formatDate(diagnosisData.created_at) }}</div>
        </div>

        <div class="result-block">
          <div class="label">Итоговое состояние</div>
          <div class="value">{{ diagnosisData.final_state }}</div>
        </div>

        <div class="result-block">
          <div class="label">Динамика</div>
          <div class="value">{{ diagnosisData.dynamics ?? "—" }}</div>
        </div>

        <div class="result-block">
          <div class="label">Диагноз</div>
          <div class="value accent">{{ diagnosisData.diagnosis }}</div>
        </div>

        <div class="result-block">
          <div class="label">Пояснение</div>
          <div class="value text-value">{{ diagnosisData.explanation }}</div>
        </div>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Как это работает</h3>

      <p class="hint-text">
        На этом экране диагноз определяется по уже сохранённому моменту наблюдения.
      </p>

      <p class="hint-text">
        Сначала сохрани наблюдение на странице
        <strong>«Мониторинг состояния»</strong>, затем выбери его здесь.
      </p>
    </aside>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import {
  getObservationDiagnosis,
  getObservations,
} from "../../api/observations";

const observations = ref([]);
const selectedObservationId = ref("");
const diagnosisData = ref(null);
const error = ref("");

const loadObservationsData = async () => {
  error.value = "";
  try {
    observations.value = await getObservations();
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить список наблюдений.";
  }
};

const handleLoadDiagnosis = async () => {
  error.value = "";
  diagnosisData.value = null;

  if (!selectedObservationId.value) {
    error.value = "Сначала выберите наблюдение.";
    return;
  }

  try {
    diagnosisData.value = await getObservationDiagnosis(selectedObservationId.value);
  } catch (err) {
    console.error(err);
    error.value = "Не удалось получить диагноз по выбранному наблюдению.";
  }
};

const formatDate = (value) => {
  return new Date(value).toLocaleString();
};

onMounted(() => {
  loadObservationsData();
});
</script>

<style scoped>
.page-grid {
  display: grid;
  grid-template-columns: 1.5fr 0.8fr;
  gap: 20px;
}

.card {
  background: white;
  border-radius: 22px;
  padding: 24px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid #e2e8f0;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
}

.card-header p {
  margin: 8px 0 0 0;
  color: #64748b;
}

.controls {
  margin: 20px 0 16px 0;
}

.select-input {
  width: 100%;
  min-height: 46px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 15px;
}

.action-row {
  display: flex;
  justify-content: flex-start;
}

.primary-btn {
  min-width: 220px;
  min-height: 48px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-weight: 800;
  cursor: pointer;
}

.error-message {
  margin-top: 16px;
  color: #dc2626;
  font-weight: 700;
}

.result-card {
  margin-top: 22px;
  padding: 22px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.result-block {
  margin-bottom: 18px;
}

.label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 6px;
}

.value {
  color: #0f172a;
  font-weight: 700;
}

.value.accent {
  color: #059669;
  font-size: 20px;
}

.text-value {
  line-height: 1.6;
  white-space: pre-wrap;
}

.side-card h3 {
  margin-top: 0;
}

.hint-text {
  color: #475569;
  line-height: 1.7;
}

@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }

  .primary-btn {
    width: 100%;
  }
}
</style>