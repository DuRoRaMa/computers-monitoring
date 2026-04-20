<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>История наблюдений</h2>
        <p>Сохранённые результаты мониторинга</p>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Дата</th>
              <th>Состояние</th>
              <th>Диагноз</th>
              <th>Динамика</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in observations"
              :key="item.id"
              :class="{ active: selectedObservation?.id === item.id }"
              @click="handleSelect(item.id)"
            >
              <td>{{ item.id }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
              <td>{{ item.final_state }}</td>
              <td>{{ item.diagnosis }}</td>
              <td>{{ item.dynamics ?? "—" }}</td>
            </tr>
            <tr v-if="!observations.length">
              <td colspan="5" class="empty-cell">История пока пуста</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Подробности наблюдения</h3>

      <template v-if="selectedObservation">
        <div class="info-block">
          <div class="label">Дата</div>
          <div class="value">{{ formatDate(selectedObservation.created_at) }}</div>
        </div>

        <div class="info-block">
          <div class="label">Итоговое состояние</div>
          <div class="value">{{ selectedObservation.result.final_state }}</div>
        </div>

        <div class="info-block">
          <div class="label">Диагноз</div>
          <div class="value">{{ selectedObservation.result.diagnosis }}</div>
        </div>

        <div class="info-block">
          <div class="label">Динамика</div>
          <div class="value">{{ selectedObservation.result.dynamics ?? "—" }}</div>
        </div>

        <div class="info-block">
          <div class="label">Пояснение</div>
          <div class="value text-value">{{ selectedObservation.result.explanation }}</div>
        </div>
      </template>

      <template v-else>
        <p class="hint-text">
          Выберите наблюдение из таблицы, чтобы посмотреть детали.
        </p>
      </template>
    </aside>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { getObservation, getObservations } from "../../api/observations";

const observations = ref([]);
const selectedObservation = ref(null);
const error = ref("");

const loadObservations = async () => {
  error.value = "";
  try {
    observations.value = await getObservations();
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить историю наблюдений.";
  }
};

const handleSelect = async (id) => {
  error.value = "";
  try {
    selectedObservation.value = await getObservation(id);
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить выбранное наблюдение.";
  }
};

const formatDate = (value) => {
  return new Date(value).toLocaleString();
};

onMounted(() => {
  loadObservations();
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

.error-message {
  margin: 18px 0;
  color: #dc2626;
  font-weight: 700;
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

.data-table tbody tr {
  cursor: pointer;
}

.data-table tbody tr.active {
  background: #ecfdf5;
}

.side-card h3 {
  margin-top: 0;
}

.info-block {
  margin-bottom: 20px;
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

.text-value {
  line-height: 1.6;
  white-space: pre-wrap;
}

.hint-text,
.empty-cell {
  color: #64748b;
}

@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }
}
</style>