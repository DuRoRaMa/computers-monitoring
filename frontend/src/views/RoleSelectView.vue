<template>
  <div class="role-page">
    <div class="role-card-wrapper">
      <div class="role-header">
        <h1>Система мониторинга состояния компьютера</h1>
        <p>Выберите режим работы</p>
      </div>

      <div class="role-cards">
        <button class="role-card expert" @click="goToExpert">
          <div class="role-title">Эксперт</div>
          <div class="role-description">
            Настройка базы знаний, показателей, диагнозов,
            степеней тяжести и правил экспертной системы.
          </div>
        </button>

        <button class="role-card user" @click="goToUser">
          <div class="role-title">Пользователь</div>
          <div class="role-description">
            Ввод наблюдений, анализ состояния компьютера
            и получение результата экспертной системы.
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const goToExpert = () => {
  router.push("/expert/diagnoses");
};

const goToUser = () => {
  router.push("/user/monitoring");
};
</script>