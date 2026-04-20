<template>
  <div class="page">
    <h2>Ввод значений показателей</h2>

    <form class="form-grid" @submit.prevent="submitForm">
      <label>
        CPU загрузка
        <input v-model.number="form.cpu_load" type="number" min="0" max="100" step="0.1" />
      </label>

      <label>
        RAM занятость
        <input v-model.number="form.ram_usage" type="number" min="0" max="100" step="0.1" />
      </label>

      <label>
        CPU температура
        <input v-model.number="form.cpu_temp" type="number" min="20" max="120" step="0.1" />
      </label>

      <label>
        Диск скорость
        <input v-model.number="form.disk_speed" type="number" min="0" max="1000" step="0.1" />
      </label>

      <label>
        Диск заполнение
        <input v-model.number="form.disk_fill" type="number" min="0" max="100" step="0.1" />
      </label>

      <label>
        Сеть пропускная
        <input v-model.number="form.network_bandwidth" type="number" min="0" max="10000" step="0.1" />
      </label>

      <label>
        Процессы количество
        <input v-model.number="form.process_count" type="number" min="0" max="1000" step="1" />
      </label>

      <label>
        Сервисы состояние
        <select v-model="form.service_state">
          <option>Все работают</option>
          <option>Некоторые остановлены</option>
          <option>Критический сервис остановлен</option>
        </select>
      </label>

      <label>
        Предыдущее состояние
        <select v-model="form.previous_state">
          <option :value="null">Не задано</option>
          <option>Оптимальное</option>
          <option>Хорошее</option>
          <option>Критическое</option>
          <option>Критическое с риском отказа</option>
        </select>
      </label>

      <button type="submit" :disabled="loading">
        {{ loading ? "Выполняется..." : "Определить состояние" }}
      </button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <section v-if="result" class="result-card">
      <h3>Результат</h3>
      <p><strong>Итоговое состояние:</strong> {{ result.final_state }}</p>
      <p><strong>Динамика:</strong> {{ result.dynamics ?? "Не определялась" }}</p>
      <p><strong>Диагноз:</strong> {{ result.diagnosis }}</p>

      <h4>Степени тяжести по показателям</h4>
      <ul>
        <li v-for="item in result.indicator_results" :key="item.indicator">
          {{ item.indicator }}: {{ item.value }} → {{ item.severity }}
        </li>
      </ul>

      <h4>Объяснение</h4>
      <p>{{ result.explanation }}</p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { evaluateMonitoring } from "../api/monitoring";

const loading = ref(false);
const error = ref("");
const result = ref(null);

const form = reactive({
  cpu_load: 20,
  ram_usage: 35,
  cpu_temp: 45,
  disk_speed: 150,
  disk_fill: 40,
  network_bandwidth: 3000,
  process_count: 80,
  service_state: "Все работают",
  previous_state: null,
});

const submitForm = async () => {
  loading.value = true;
  error.value = "";
  result.value = null;

  try {
    const payload = {
      ...form,
      previous_state: form.previous_state || null,
    };

    result.value = await evaluateMonitoring(payload);
  } catch (err) {
    console.error(err);
    error.value = "Не удалось получить результат. Проверь backend и входные данные.";
  } finally {
    loading.value = false;
  }
};
</script>