<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Правила степеней тяжести</h2>
        <p>
          Для каждого показателя задаётся значение с учётом его типа
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

      <div class="rows-list">
        <div
          v-for="row in rows"
          :key="row.indicator_id"
          class="row-card"
          :class="{ invalid: (row.touched || submitted) && !validateRow(row).valid }"
        >
          <div class="row-title">
            <span>{{ row.indicator_name }}</span>
            <span class="row-type">
              {{
                row.indicator_value_type === "numeric"
                  ? "Только диапазон"
                  : row.indicator_value_type === "categorical"
                  ? "Только текст"
                  : "Любой тип"
              }}
            </span>
          </div>

          <ValueEditor
            :model-value="row.editor"
            :allow-empty="true"
            :show-errors="row.touched || submitted"
            :forced-mode="
              row.indicator_value_type === 'numeric'
                ? 'range'
                : row.indicator_value_type === 'categorical'
                ? 'scalar'
                : null
            "
            @update:modelValue="(value) => handleRowChange(row, value)"
          />
        </div>
      </div>

      <div class="save-row">
        <button class="primary-btn" @click="handleSave">
          Сохранить правила
        </button>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Подсказка</h3>

      <div class="hint-block">
        <div class="hint-title">Числовые показатели</div>
        <div class="hint-text">Для них доступен только диапазон</div>
      </div>

      <div class="hint-block">
        <div class="hint-title">Категориальные показатели</div>
        <div class="hint-text">Для них доступен только текст</div>
      </div>

      <div class="hint-block">
        <div class="hint-title">Пустое значение</div>
        <div class="hint-text">Означает, что правило не задано</div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import ValueEditor from "../../components/ValueEditor.vue";
import {
  getSeverityNames,
  getSeverityValues,
  saveSeverityValues,
} from "../../api/knowledge";
import {
  parseValueText,
  formatValueEditor,
  validateValueEditor,
} from "../../utils/valueEditor";

const severityNames = ref([]);
const selectedSeverityId = ref("");
const rows = ref([]);

const message = ref("");
const error = ref("");
const submitted = ref(false);

const clearMessages = () => {
  message.value = "";
  error.value = "";
};

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
  submitted.value = false;

  if (!selectedSeverityId.value) {
    rows.value = [];
    return;
  }

  try {
    const data = await getSeverityValues(selectedSeverityId.value);
    rows.value = (data.rows || []).map((row) => ({
      ...row,
      editor: parseValueText(row.value_text),
      touched: false,
    }));
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить правила степени тяжести.";
  }
};

const handleRowChange = (row, value) => {
  row.editor = value;
  row.touched = true;
};

const validateRow = (row) => {
  return validateValueEditor(row.editor, { allowEmpty: true });
};

const handleSave = async () => {
  clearMessages();
  submitted.value = true;

  if (!selectedSeverityId.value) {
    error.value = "Сначала выберите степень тяжести.";
    return;
  }

  const invalidRow = rows.value.find((row) => !validateRow(row).valid);
  if (invalidRow) {
    error.value = `Исправьте неверное значение для показателя: ${invalidRow.indicator_name}`;
    return;
  }

  try {
    await saveSeverityValues(
      selectedSeverityId.value,
      rows.value.map((row) => ({
        indicator_id: row.indicator_id,
        value_text: formatValueEditor(row.editor),
      }))
    );

    message.value = "Правила степени тяжести сохранены.";
    submitted.value = false;
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

.select-input {
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

.rows-list {
  display: grid;
  gap: 14px;
}

.row-card {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 16px;
  background: #f8fafc;
}

.row-card.invalid {
  border-color: #ef4444;
  background: #fef2f2;
}

.row-title {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 12px;
}

.row-type {
  font-size: 12px;
  color: #64748b;
  font-weight: 700;
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

  .row-title {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>