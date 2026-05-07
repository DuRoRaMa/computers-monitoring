<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Нормальные значения</h2>
        <p>Заполните нормальное значение для каждого показателя. Значение должно входить в заданное возможное значение показателя.</p>
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
            <div>
              <span>{{ row.indicator_name }}</span>
              <div class="possible-line">
                Возможные значения:
                <b>{{ possibleValuesText(row) }}</b>
              </div>
            </div>
            <span class="row-type">
              {{ row.indicator_value_type === "numeric" ? "Только диапазон" : "Только текст" }}
            </span>
          </div>

          <ValueEditor
            :model-value="row.editor"
            :allow-empty="false"
            :show-errors="row.touched || submitted"
            :forced-mode="forcedModeFor(row)"
            @update:modelValue="(value) => handleRowChange(row, value)"
          />
        </div>
      </div>

      <div class="save-row">
        <button class="primary-btn" @click="handleSave">
          Сохранить нормальные значения
        </button>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Подсказка</h3>

      <div class="hint-block">
        <div class="hint-title">Числовые показатели</div>
        <div class="hint-text">Для них вводится диапазон, например [0;30]</div>
      </div>

      <div class="hint-block">
        <div class="hint-title">Категориальные показатели</div>
        <div class="hint-text">Для них вводится текстовое значение</div>
      </div>

      <div class="hint-block">
        <div class="hint-title">Ограничение</div>
        <div class="hint-text">Нормальное значение должно входить в возможное значение показателя</div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import ValueEditor from "../../components/ValueEditor.vue";
import { getAllNormalValues, saveNormalValues } from "../../api/knowledge";
import {
  parseValueText,
  formatValueEditor,
  validateValueEditor,
} from "../../utils/valueEditor";

const rows = ref([]);
const message = ref("");
const error = ref("");
const submitted = ref(false);

const clearMessages = () => {
  message.value = "";
  error.value = "";
};

const forcedModeFor = (row) => {
  if (row.indicator_value_type === "numeric") return "range";
  if (row.indicator_value_type === "categorical") return "scalar";
  return null;
};

const getPossibleValues = (row) => {
  if (Array.isArray(row.possible_values)) {
    return row.possible_values;
  }

  if (row.possible_value_text) {
    return row.possible_value_text
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return [];
};

const possibleValuesText = (row) => {
  const values = getPossibleValues(row);

  if (!values.length) {
    return "не заданы";
  }

  return values.join(", ");
};

const loadRows = async () => {
  clearMessages();
  submitted.value = false;

  try {
    const data = await getAllNormalValues();
    rows.value = (data.rows || []).map((row) => ({
      ...row,
      editor: parseValueText(row.value_text),
      touched: false,
    }));
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить нормальные значения.";
  }
};

const handleRowChange = (row, value) => {
  row.editor = value;
  row.touched = true;
};

const validateRow = (row) => {
  return validateValueEditor(row.editor, { allowEmpty: false });
};

const handleSave = async () => {
  clearMessages();
  submitted.value = true;

  const rowWithoutPossibleValue = rows.value.find(
    (row) => !getPossibleValues(row).length
  );

  if (rowWithoutPossibleValue) {
    error.value = `Сначала задайте возможное значение для показателя: ${rowWithoutPossibleValue.indicator_name}`;
    return;
  }

  const invalidRow = rows.value.find((row) => !validateRow(row).valid);

  if (invalidRow) {
    error.value = `Исправьте неверное нормальное значение для показателя: ${invalidRow.indicator_name}`;
    return;
  }

  try {
    await saveNormalValues(
      rows.value.map((row) => ({
        indicator_id: row.indicator_id,
        value_text: formatValueEditor(row.editor),
      }))
    );

    message.value = "Нормальные значения сохранены.";
    submitted.value = false;
    await loadRows();
  } catch (err) {
    console.error(err);
    error.value = err?.response?.data?.detail || "Не удалось сохранить нормальные значения.";
  }
};

onMounted(async () => {
  await loadRows();
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
}

.card-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.card-header p {
  margin: 0 0 18px;
  color: #64748b;
}

.success-message,
.error-message {
  margin-bottom: 14px;
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 14px;
}

.success-message {
  background: #ecfdf5;
  color: #047857;
}

.error-message {
  background: #fef2f2;
  color: #b91c1c;
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
  background: #fff7f7;
}

.row-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 12px;
  font-weight: 700;
}

.row-type {
  flex-shrink: 0;
  border-radius: 999px;
  padding: 6px 10px;
  background: #eef2ff;
  color: #3730a3;
  font-size: 12px;
  font-weight: 700;
}

.possible-line {
  margin-top: 6px;
  color: #64748b;
  font-size: 13px;
  font-weight: 400;
}

.possible-line b {
  color: #334155;
}

.save-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.primary-btn {
  border: 0;
  border-radius: 14px;
  padding: 12px 18px;
  background: #2563eb;
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.primary-btn:hover {
  background: #1d4ed8;
}

.side-card h3 {
  margin: 0 0 16px;
}

.hint-block {
  padding: 14px;
  border-radius: 16px;
  background: #f8fafc;
  margin-bottom: 12px;
}

.hint-title {
  font-weight: 700;
  margin-bottom: 6px;
}

.hint-text {
  color: #64748b;
  font-size: 14px;
}

@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }
}
</style>
