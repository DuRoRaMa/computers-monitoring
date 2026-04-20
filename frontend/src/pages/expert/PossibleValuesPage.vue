<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Возможные значения</h2>
        <p>Выберите показатель и управляйте его допустимыми значениями</p>
      </div>

      <div class="controls">
        <select v-model="selectedIndicatorId" class="select-input" @change="loadValues">
          <option disabled value="">Выберите показатель</option>
          <option v-for="item in indicators" :key="item.id" :value="item.id">
            {{ item.name }}
          </option>
        </select>
      </div>

      <div class="form-row">
        <input
          v-model="newValueText"
          class="text-input"
          placeholder="Например: [0;30] или Все работают"
          @keyup.enter="handleCreate"
        />
        <button class="primary-btn" @click="handleCreate">
          Добавить
        </button>
      </div>

      <div v-if="message" class="success-message">{{ message }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Значение</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in values" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.value_text }}</td>
              <td class="actions-cell">
                <button class="danger-btn" @click="handleDelete(item.id)">
                  Удалить
                </button>
              </td>
            </tr>
            <tr v-if="!values.length">
              <td colspan="3" class="empty-cell">
                Для выбранного показателя пока нет значений
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Подсказка по формату</h3>

      <div class="hint-block">
        <div class="hint-title">Диапазоны</div>
        <div class="hint-text">[0;30]</div>
        <div class="hint-text">(30;60]</div>
        <div class="hint-text">[50;80)</div>
      </div>

      <div class="hint-block">
        <div class="hint-title">Текстовые значения</div>
        <div class="hint-text">Все работают</div>
        <div class="hint-text">Некоторые остановлены</div>
      </div>

      <div class="hint-block">
        <div class="hint-title">Текущий показатель</div>
        <div class="hint-text strong">
          {{ selectedIndicatorName || "Не выбран" }}
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import {
  createPossibleValue,
  deletePossibleValue,
  getIndicators,
  getPossibleValues,
} from "../../api/knowledge";

const indicators = ref([]);
const selectedIndicatorId = ref("");
const values = ref([]);
const newValueText = ref("");
const message = ref("");
const error = ref("");

const clearMessages = () => {
  message.value = "";
  error.value = "";
};

const selectedIndicatorName = computed(() => {
  return indicators.value.find((x) => x.id === selectedIndicatorId.value)?.name || "";
});

const loadIndicatorsData = async () => {
  try {
    indicators.value = await getIndicators();
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить показатели.";
  }
};

const loadValues = async () => {
  clearMessages();

  if (!selectedIndicatorId.value) {
    values.value = [];
    return;
  }

  try {
    values.value = await getPossibleValues(selectedIndicatorId.value);
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить возможные значения.";
  }
};

const handleCreate = async () => {
  clearMessages();

  if (!selectedIndicatorId.value) {
    error.value = "Сначала выберите показатель.";
    return;
  }

  if (!newValueText.value.trim()) {
    error.value = "Введите значение.";
    return;
  }

  try {
    await createPossibleValue(selectedIndicatorId.value, newValueText.value);
    newValueText.value = "";
    message.value = "Возможное значение добавлено.";
    await loadValues();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось добавить значение.";
  }
};

const handleDelete = async (id) => {
  clearMessages();

  try {
    await deletePossibleValue(id);
    message.value = "Значение удалено.";
    await loadValues();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось удалить значение.";
  }
};

onMounted(async () => {
  await loadIndicatorsData();
});
</script>

<style scoped>
.page-grid {
  display: grid;
  grid-template-columns: 1.45fr 0.85fr;
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
  margin: 20px 0 14px 0;
}

.select-input,
.text-input {
  width: 100%;
  min-height: 46px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 15px;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
}

.primary-btn {
  min-width: 140px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
  color: white;
  font-weight: 700;
  cursor: pointer;
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

.actions-cell {
  text-align: right;
}

.danger-btn {
  border: none;
  border-radius: 12px;
  padding: 8px 12px;
  background: #fee2e2;
  color: #b91c1c;
  font-weight: 700;
  cursor: pointer;
}

.side-card h3 {
  margin-top: 0;
}

.hint-block {
  margin-bottom: 22px;
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

.hint-text.strong {
  color: #0f172a;
  font-weight: 700;
}

.empty-cell {
  color: #64748b;
}

@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    flex-direction: column;
  }
}
</style>