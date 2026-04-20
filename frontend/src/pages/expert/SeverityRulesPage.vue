<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Правила степеней тяжести</h2>
        <p>
          Выберите степень тяжести и задайте для каждого показателя его значение
        </p>
      </div>

      <div class="controls">
        <select v-model="selectedSeverityId" class="select-input" @change="loadRows">
          <option disabled value="">Выберите степень тяжести</option>
          <option v-for="item in severityNames" :key="item.id" :value="item.id">
            {{ item.name }}
          </option>
        </select>
      </div>

      <div v-if="message" class="success-message">{{ message }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Показатель</th>
              <th>Значение показателя</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.indicator_id">
              <td>{{ row.indicator_name }}</td>
              <td>
                <input
                  v-model="row.value_text"
                  class="table-input"
                  placeholder="[0;30] или Все работают"
                />
              </td>
            </tr>
            <tr v-if="!rows.length">
              <td colspan="2" class="empty-cell">
                Выберите степень тяжести, чтобы загрузить правила
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="save-row">
        <button class="primary-btn" @click="handleSave">
          Сохранить правила
        </button>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Контекст</h3>

      <div class="info-block">
        <div class="label">Выбранная степень тяжести</div>
        <div class="value">{{ selectedSeverityName || "Не выбрана" }}</div>
      </div>

      <div class="info-block">
        <div class="label">Количество строк</div>
        <div class="value">{{ rows.length }}</div>
      </div>

      <div class="hint-block">
        <div class="hint-title">Примеры формата</div>
        <div class="hint-text">[0;30]</div>
        <div class="hint-text">(30;60]</div>
        <div class="hint-text">Все работают</div>
      </div>

      <p class="hint-note">
        Пустые значения не сохраняются. Если правило не нужно,
        просто оставь поле пустым.
      </p>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import {
  getSeverityNames,
  getSeverityValues,
  saveSeverityValues,
} from "../../api/knowledge";

const severityNames = ref([]);
const selectedSeverityId = ref("");
const rows = ref([]);

const message = ref("");
const error = ref("");

const clearMessages = () => {
  message.value = "";
  error.value = "";
};

const selectedSeverityName = computed(() => {
  return severityNames.value.find((x) => x.id === selectedSeverityId.value)?.name || "";
});

const loadSeverityNamesData = async () => {
  try {
    severityNames.value = await getSeverityNames();
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить степени тяжести.";
  }
};

const loadRows = async () => {
  clearMessages();

  if (!selectedSeverityId.value) {
    rows.value = [];
    return;
  }

  try {
    const data = await getSeverityValues(selectedSeverityId.value);
    rows.value = data.rows || [];
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить правила степени тяжести.";
  }
};

const handleSave = async () => {
  clearMessages();

  if (!selectedSeverityId.value) {
    error.value = "Сначала выберите степень тяжести.";
    return;
  }

  try {
    await saveSeverityValues(selectedSeverityId.value, rows.value);
    message.value = "Правила степени тяжести сохранены.";
    await loadRows();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось сохранить правила.";
  }
};

onMounted(async () => {
  await loadSeverityNamesData();
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

.select-input,
.table-input {
  width: 100%;
  min-height: 46px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 15px;
}

.success-message {
  margin-bottom: 14px;
  color: #0f766e;
  font-weight: 700;
}

.error-message {
  margin-bottom: 14px;
  color: #dc2626;
  font-weight: 700;
}

.table-wrap {
  overflow: auto;
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

.save-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.primary-btn {
  min-width: 220px;
  min-height: 48px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.side-card h3 {
  margin-top: 0;
}

.info-block {
  margin-bottom: 22px;
}

.label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 6px;
}

.value {
  color: #0f172a;
  font-weight: 800;
  font-size: 18px;
}

.hint-block {
  margin-bottom: 18px;
}

.hint-title {
  font-size: 14px;
  font-weight: 800;
  color: #334155;
  margin-bottom: 10px;
}

.hint-text {
  color: #64748b;
  margin-bottom: 6px;
}

.hint-note,
.empty-cell {
  color: #64748b;
  line-height: 1.6;
}

@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }

  .save-row {
    justify-content: stretch;
  }

  .primary-btn {
    width: 100%;
  }
}
</style>