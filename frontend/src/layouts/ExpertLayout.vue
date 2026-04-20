<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-title">Экспертная система</div>
        <div class="brand-subtitle">Режим эксперта</div>
      </div>

      <div class="nav-group">
        <div class="nav-group-title">Справочники</div>

        <RouterLink class="nav-link" to="/expert/diagnoses">
          Диагнозы
        </RouterLink>

        <RouterLink class="nav-link" to="/expert/indicators">
          Показатели
        </RouterLink>

        <RouterLink class="nav-link" to="/expert/severity-names">
          Степени тяжести
        </RouterLink>
      </div>

      <div class="nav-group">
        <div class="nav-group-title">Настройка знаний</div>

        <RouterLink class="nav-link" to="/expert/possible-values">
          Возможные значения
        </RouterLink>

        <RouterLink class="nav-link" to="/expert/normal-values">
          Нормальные значения
        </RouterLink>

        <RouterLink class="nav-link" to="/expert/state-characteristics">
          Характеристики состояния
        </RouterLink>
      </div>

      <div class="nav-group">
        <div class="nav-group-title">Правила</div>

        <RouterLink class="nav-link" to="/expert/severity-rules">
          Правила степеней тяжести
        </RouterLink>

        <RouterLink class="nav-link" to="/expert/diagnosis-rules">
          Правила диагнозов
        </RouterLink>
      </div>

      <div class="sidebar-footer">
        <button class="back-btn" @click="goBack">Сменить роль</button>
      </div>
    </aside>

    <div class="content-area">
      <header class="topbar">
        <div>
          <h1 class="page-title">Редактор базы знаний</h1>
          <p class="page-subtitle">
            Управление сущностями экспертной системы
          </p>
        </div>
      </header>

      <main class="page-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from "vue-router";

const router = useRouter();

const goBack = () => {
  router.push("/role-select");
};
</script>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px 1fr;
  background: #f8fafc;
}

.sidebar {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: white;
  padding: 24px 18px;
  display: flex;
  flex-direction: column;
}

.brand {
  margin-bottom: 28px;
}

.brand-title {
  font-size: 22px;
  font-weight: 800;
}

.brand-subtitle {
  margin-top: 6px;
  color: #cbd5e1;
  font-size: 14px;
}

.nav-group {
  margin-bottom: 28px;
}

.nav-group-title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin-bottom: 12px;
}

.nav-link {
  display: block;
  padding: 12px 14px;
  margin-bottom: 8px;
  border-radius: 14px;
  color: #e2e8f0;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
  color: white;
}

.sidebar-footer {
  margin-top: auto;
}

.back-btn {
  width: 100%;
  border: none;
  border-radius: 14px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.12);
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.content-area {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 24px 32px;
}

.page-title {
  margin: 0;
  font-size: 28px;
  color: #0f172a;
}

.page-subtitle {
  margin: 8px 0 0 0;
  color: #64748b;
}

.page-content {
  padding: 28px 32px;
}

@media (max-width: 900px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    padding: 18px;
  }

  .page-content {
    padding: 18px;
  }
}
</style>