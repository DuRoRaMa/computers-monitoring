<template>
  <div class="page-grid">
    <section class="card">
      <div class="card-header">
        <h2>Степени тяжести</h2>
        <p>Справочник уровней тяжести состояния системы</p>
      </div>

      <div class="form-row">
        <input
          v-model="newSeverityName"
          class="text-input"
          placeholder="Введите название степени тяжести"
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
              <th>Порядок</th>
              <th>Название</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in severityNames"
              :key="item.id"
              :class="{ active: selectedSeverity?.id === item.id }"
              @click="selectedSeverity = item"
            >
              <td>{{ item.id }}</td>
              <td>{{ item.order_number }}</td>
              <td>{{ item.name }}</td>
              <td class="actions-cell">
                <button class="danger-btn" @click.stop="handleDelete(item.id)">
                  Удалить
                </button>
              </td>
            </tr>
            <tr v-if="!severityNames.length">
              <td colspan="4" class="empty-cell">
                Степени тяжести пока не добавлены
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <aside class="card side-card">
      <h3>Карточка степени тяжести</h3>

      <template v-if="selectedSeverity">
        <div class="info-block">
          <div class="label">Идентификатор</div>
          <div class="value">{{ selectedSeverity.id }}</div>
        </div>

        <div class="info-block">
          <div class="label">Порядок</div>
          <div class="value">{{ selectedSeverity.order_number }}</div>
        </div>

        <div class="info-block">
          <div class="label">Название</div>
          <div class="value">{{ selectedSeverity.name }}</div>
        </div>
      </template>

      <template v-else>
        <p class="hint-text">
          Выберите степень тяжести в таблице, чтобы посмотреть её данные.
        </p>
      </template>
    </aside>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import {
  createSeverityName,
  deleteSeverityName,
  getSeverityNames,
} from "../../api/knowledge";

const severityNames = ref([]);
const selectedSeverity = ref(null);
const newSeverityName = ref("");
const message = ref("");
const error = ref("");

const clearMessages = () => {
  message.value = "";
  error.value = "";
};

const loadSeverityNames = async () => {
  clearMessages();
  try {
    severityNames.value = await getSeverityNames();

    if (
      selectedSeverity.value &&
      !severityNames.value.find((x) => x.id === selectedSeverity.value.id)
    ) {
      selectedSeverity.value = null;
    }
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить степени тяжести.";
  }
};

const handleCreate = async () => {
  clearMessages();

  if (!newSeverityName.value.trim()) {
    error.value = "Введите название степени тяжести.";
    return;
  }

  try {
    await createSeverityName(newSeverityName.value);
    newSeverityName.value = "";
    message.value = "Степень тяжести успешно добавлена.";
    await loadSeverityNames();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось добавить степень тяжести.";
  }
};

const handleDelete = async (id) => {
  clearMessages();

  try {
    await deleteSeverityName(id);
    message.value = "Степень тяжести удалена.";
    await loadSeverityNames();
  } catch (err) {
    console.error(err);
    error.value =
      err?.response?.data?.detail || "Не удалось удалить степень тяжести.";
  }
};

onMounted(() => {
  loadSeverityNames();
});
</script>

<style scoped>
.page-grid {
  display: grid;
  grid-template-columns: 1.5fr 0.9fr;
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

.form-row {
  display: flex;
  gap: 12px;
  margin: 20px 0;
}

.text-input {
  flex: 1;
  min-height: 46px;
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 0 14px;
  font-size: 15px;
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

.data-table th {
  color: #475569;
  font-size: 14px;
}

.data-table tbody tr {
  cursor: pointer;
}

.data-table tbody tr.active {
  background: #eff6ff;
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
  color: #0f172a;
}

.info-block {
  margin-bottom: 18px;
}

.label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 6px;
}

.value {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.hint-text,
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