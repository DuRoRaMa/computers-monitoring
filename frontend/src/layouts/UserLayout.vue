<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-title">Экспертная система</div>
        <div class="brand-subtitle">Режим пользователя</div>
      </div>

      <div class="nav-group">
        <div class="nav-group-title">Работа с системой</div>

        <RouterLink class="nav-link" to="/user/monitoring">
          Мониторинг состояния
        </RouterLink>

        <RouterLink class="nav-link" to="/user/history">
          История наблюдений
        </RouterLink>

        <RouterLink class="nav-link" to="/user/diagnosis">
          Постановка диагноза
        </RouterLink>
      </div>

      <div class="sidebar-footer">
        <button class="back-btn" @click="goBack">Сменить роль</button>
      </div>
    </aside>

    <div class="content-area">
      <header class="topbar">
        <div>
          <h1 class="page-title">Рабочее место пользователя</h1>
          <p class="page-subtitle">
            Ввод наблюдений, история и постановка диагноза
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
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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