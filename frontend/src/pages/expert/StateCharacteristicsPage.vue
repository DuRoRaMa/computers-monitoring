<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Характеристики состояния</h2>
        <p>
          Выберите диагноз и настройте набор показателей, которые его описывают
        </p>
      </div>

      <div class="controls">
        <select v-model="selectedDiagnosisId" class="select-input" @change="loadData">
          <option disabled value="">Выберите диагноз</option>
          <option v-for="item in diagnoses" :key="item.id" :value="item.id">
            {{ item.name }}
          </option>
        </select>
      </div>

      <div v-if="message" class="success-message">{{ message }}</div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="dual-layout">
        <div class="list-card">
          <div class="list-title">Доступные показатели</div>

          <div
            v-for="item in availableIndicators"
            :key="item.id"
            class="list-item"
            :class="{ active: selectedAvailableId === item.id }"
            @click="selectedAvailableId = item.id"
          >
            {{ item.name }}
          </div>

          <div v-if="!availableIndicators.length" class="empty-list">
            Список пуст
          </div>
        </div>

        <div class="middle-actions">
          <button class="move-btn" @click="moveRight">→</button>
          <button class="move-btn" @click="moveLeft">←</button>
        </div>

        <div class="list-card">
          <div class="list-title">Выбранные показатели</div>

          <div
            v-for="item in selectedIndicators"
            :key="item.id"
            class="list-item"
            :class="{ active: selectedChosenId === item.id }"
            @click="selectedChosenId = item.id"
          >
            {{ item.name }}
          </div>

          <div v-if="!selectedIndicators.length" class="empty-list">
            Список пуст
          </div>
        </div>
      </div>

      <div class="save-row">
        <button class="primary-btn" @click="handleSave">
          Сохранить изменения
        </button>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Контекст</h3>

      <div class="info-block">
        <div class="label">Текущий диагноз</div>
        <div class="value">{{ selectedDiagnosisName || "Не выбран" }}</div>
      </div>

      <div class="info-block">
        <div class="label">Выбрано показателей</div>
        <div class="value">{{ selectedIds.length }}</div>
      </div>

      <p class="hint-text">
        После изменения состава характеристик нажмите кнопку
        <strong>«Сохранить изменения»</strong>.
      </p>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import {
  getDiagnoses,
  getIndicators,
  getStateCharacteristics,
  saveStateCharacteristics,
} from "../../api/knowledge";

const diagnoses = ref([]);
const indicators = ref([]);
const selectedDiagnosisId = ref("");
const selectedIds = ref([]);

const selectedAvailableId = ref(null);
const selectedChosenId = ref(null);

const message = ref("");
const error = ref("");

const clearMessages = () => {
  message.value = "";
  error.value = "";
};

const selectedDiagnosisName = computed(() => {
  return diagnoses.value.find((x) => x.id === selectedDiagnosisId.value)?.name || "";
});

const availableIndicators = computed(() => {
  const selectedSet = new Set(selectedIds.value);
  return indicators.value.filter((x) => !selectedSet.has(x.id));
});

const selectedIndicators = computed(() => {
  const selectedSet = new Set(selectedIds.value);
  return indicators.value.filter((x) => selectedSet.has(x.id));
});

const loadBaseData = async () => {
  try {
    diagnoses.value = await getDiagnoses();
    indicators.value = await getIndicators();
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить справочные данные.";
  }
};

const loadData = async () => {
  clearMessages();

  if (!selectedDiagnosisId.value) {
    selectedIds.value = [];
    return;
  }

  try {
    const data = await getStateCharacteristics(selectedDiagnosisId.value);
    selectedIds.value = data.selected_indicator_ids || [];
    selectedAvailableId.value = null;
    selectedChosenId.value = null;
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить характеристики состояния.";
  }
};

const moveRight = () => {
  if (!selectedAvailableId.value) return;
  if (!selectedIds.value.includes(selectedAvailableId.value)) {
    selectedIds.value = [...selectedIds.value, selectedAvailableId.value];
  }
  selectedAvailableId.value = null;
};

const moveLeft = () => {
  if (!selectedChosenId.value) return;
  selectedIds.value = selectedIds.value.filter((id) => id !== selectedChosenId.value);
  selectedChosenId.value = null;
};

const handleSave = async () => {
  clearMessages();

  if (!selectedDiagnosisId.value) {
    error.value = "Сначала выберите диагноз.";
    return;
  }

  try {
    await saveStateCharacteristics(selectedDiagnosisId.value, selectedIds.value);
    message.value = "Характеристики состояния сохранены.";
    await loadData();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось сохранить характеристики состояния.";
  }
};

onMounted(async () => {
  await loadBaseData();
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

.hint-text {
  color: #475569;
  line-height: 1.6;
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

  .save-row {
    justify-content: stretch;
  }

  .primary-btn {
    width: 100%;
  }
}
</style>