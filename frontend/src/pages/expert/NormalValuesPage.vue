<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Нормальное значение</h2>
        <p>Для каждого показателя может быть задано только одно нормальное значение</p>
      </div>

      <div class="controls">
        <select v-model="selectedIndicatorId" class="select-input" @change="loadData">
          <option disabled value="">Выберите показатель</option>
          <option v-for="item in indicators" :key="item.id" :value="item.id">
            {{ item.name }}
          </option>
        </select>
      </div>

      <div v-if="message" class="success-message">{{ message }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="dual-layout">
        <div class="list-card">
          <div class="list-title">Возможные значения</div>

          <div
            v-for="item in possibleValues"
            :key="item.id"
            class="list-item"
            :class="{ active: selectedPossibleId === item.id }"
            @click="selectedPossibleId = item.id"
          >
            {{ item.value_text }}
          </div>

          <div v-if="!possibleValues.length" class="empty-list">
            Для показателя нет возможных значений
          </div>
        </div>

        <div class="middle-actions">
          <button
            class="move-btn"
            :disabled="!selectedPossibleId || !!normalValue"
            @click="handleSetNormal"
          >
            →
          </button>

          <button
            class="move-btn"
            :disabled="!normalValue"
            @click="handleRemoveNormal"
          >
            ←
          </button>
        </div>

        <div class="list-card">
          <div class="list-title">Нормальное значение</div>

          <div
            v-if="normalValue"
            class="list-item active"
            @click="selectedNormalId = normalValue.id"
          >
            {{ normalValue.value_text }}
          </div>

          <div v-else class="empty-list">
            Нормальное значение не задано
          </div>
        </div>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Контекст</h3>

      <div class="info-block">
        <div class="label">Текущий показатель</div>
        <div class="value">{{ selectedIndicatorName || "Не выбран" }}</div>
      </div>

      <div class="info-block">
        <div class="label">Возможных значений</div>
        <div class="value">{{ possibleValues.length }}</div>
      </div>

      <div class="info-block">
        <div class="label">Нормальное значение</div>
        <div class="value">{{ normalValue ? "Задано" : "Не задано" }}</div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import {
  createNormalValue,
  deleteNormalValue,
  getIndicators,
  getNormalValues,
  getPossibleValues,
} from "../../api/knowledge";

const indicators = ref([]);
const selectedIndicatorId = ref("");
const possibleValues = ref([]);
const normalValues = ref([]);

const selectedPossibleId = ref(null);
const selectedNormalId = ref(null);

const message = ref("");
const error = ref("");

const clearMessages = () => {
  message.value = "";
  error.value = "";
};

const selectedIndicatorName = computed(() => {
  return indicators.value.find((x) => x.id === selectedIndicatorId.value)?.name || "";
});

const normalValue = computed(() => {
  return normalValues.value.length ? normalValues.value[0] : null;
});

const loadIndicatorsData = async () => {
  try {
    indicators.value = await getIndicators();
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить показатели.";
  }
};

const loadData = async () => {
  clearMessages();

  if (!selectedIndicatorId.value) {
    possibleValues.value = [];
    normalValues.value = [];
    selectedPossibleId.value = null;
    selectedNormalId.value = null;
    return;
  }

  try {
    possibleValues.value = await getPossibleValues(selectedIndicatorId.value);
    normalValues.value = await getNormalValues(selectedIndicatorId.value);
    selectedPossibleId.value = null;
    selectedNormalId.value = normalValue.value?.id || null;
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить значения.";
  }
};

const handleSetNormal = async () => {
  clearMessages();

  if (!selectedIndicatorId.value) {
    error.value = "Сначала выберите показатель.";
    return;
  }

  if (!selectedPossibleId.value) {
    error.value = "Выберите возможное значение.";
    return;
  }

  if (normalValue.value) {
    error.value = "Для этого показателя уже задано нормальное значение.";
    return;
  }

  const source = possibleValues.value.find((x) => x.id === selectedPossibleId.value);
  if (!source) {
    error.value = "Не удалось определить выбранное значение.";
    return;
  }

  try {
    await createNormalValue(selectedIndicatorId.value, source.value_text);
    message.value = "Нормальное значение установлено.";
    await loadData();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось установить нормальное значение.";
  }
};

const handleRemoveNormal = async () => {
  clearMessages();

  if (!normalValue.value) {
    error.value = "Нормальное значение не выбрано.";
    return;
  }

  try {
    await deleteNormalValue(normalValue.value.id);
    message.value = "Нормальное значение удалено.";
    await loadData();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось удалить нормальное значение.";
  }
};

onMounted(async () => {
  await loadIndicatorsData();
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
.dual-layout {
  display: grid;
  grid-template-columns: 1fr 80px 1fr;
  gap: 18px;
  align-items: stretch;
}
.list-card {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  overflow: hidden;
  min-height: 360px;
}
.list-title {
  background: #f8fafc;
  padding: 14px 16px;
  font-weight: 800;
  border-bottom: 1px solid #e2e8f0;
}
.list-item {
  padding: 14px 16px;
  border-bottom: 1px solid #eef2f7;
  cursor: pointer;
}
.list-item.active {
  background: #eff6ff;
  color: #0f172a;
  font-weight: 700;
}
.empty-list {
  padding: 16px;
  color: #64748b;
}
.middle-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}
.move-btn {
  min-height: 48px;
  border: none;
  border-radius: 14px;
  background: #e2e8f0;
  font-size: 22px;
  cursor: pointer;
  font-weight: 800;
}
.move-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
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
@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }
  .dual-layout {
    grid-template-columns: 1fr;
  }
  .middle-actions {
    flex-direction: row;
  }
}
</style>
