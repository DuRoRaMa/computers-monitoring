<template>
  <div class="page">
    <h2>База знаний</h2>

    <div class="actions">
      <button @click="handleSeedBasic" :disabled="loading">
        Заполнить базовые знания
      </button>
      <button @click="handleSeedRules" :disabled="loading">
        Заполнить правила
      </button>
      <button @click="loadKnowledge" :disabled="loading">
        Обновить данные
      </button>
    </div>

    <p v-if="message" class="success">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div class="knowledge-grid">
      <section class="knowledge-card">
        <h3>Показатели</h3>
        <ul>
          <li v-for="item in indicators" :key="item.id">
            {{ item.name }}
          </li>
        </ul>
      </section>

      <section class="knowledge-card">
        <h3>Диагнозы</h3>
        <ul>
          <li v-for="item in diagnoses" :key="item.id">
            {{ item.name }}
          </li>
        </ul>
      </section>

      <section class="knowledge-card">
        <h3>Названия степеней тяжести</h3>
        <ul>
          <li v-for="item in severityNames" :key="item.id">
            {{ item.order_number }}. {{ item.name }}
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import {
  getDiagnoses,
  getIndicators,
  getSeverityNames,
  seedBasicKnowledge,
  seedRules,
} from "../api/knowledge";

const loading = ref(false);
const message = ref("");
const error = ref("");

const indicators = ref([]);
const diagnoses = ref([]);
const severityNames = ref([]);

const loadKnowledge = async () => {
  loading.value = true;
  message.value = "";
  error.value = "";

  try {
    const [indicatorsData, diagnosesData, severityData] = await Promise.all([
      getIndicators(),
      getDiagnoses(),
      getSeverityNames(),
    ]);

    indicators.value = indicatorsData;
    diagnoses.value = diagnosesData;
    severityNames.value = severityData;
  } catch (err) {
    console.error(err);
    error.value = "Не удалось загрузить данные базы знаний.";
  } finally {
    loading.value = false;
  }
};

const handleSeedBasic = async () => {
  loading.value = true;
  message.value = "";
  error.value = "";

  try {
    const data = await seedBasicKnowledge();
    message.value = data.message;
    await loadKnowledge();
  } catch (err) {
    console.error(err);
    error.value = "Не удалось заполнить базовые знания.";
  } finally {
    loading.value = false;
  }
};

const handleSeedRules = async () => {
  loading.value = true;
  message.value = "";
  error.value = "";

  try {
    const data = await seedRules();
    message.value = data.message;
  } catch (err) {
    console.error(err);
    error.value = "Не удалось заполнить правила.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadKnowledge();
});
</script>