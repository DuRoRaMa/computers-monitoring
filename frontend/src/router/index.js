import { createRouter, createWebHistory } from "vue-router";

import RoleSelectView from "../views/RoleSelectView.vue";

import ExpertLayout from "../layouts/ExpertLayout.vue";
import UserLayout from "../layouts/UserLayout.vue";

import DiagnosesPage from "../pages/expert/DiagnosesPage.vue";
import IndicatorsPage from "../pages/expert/IndicatorsPage.vue";
import SeverityNamesPage from "../pages/expert/SeverityNamesPage.vue";
import PossibleValuesPage from "../pages/expert/PossibleValuesPage.vue";
import NormalValuesPage from "../pages/expert/NormalValuesPage.vue";
import StateCharacteristicsPage from "../pages/expert/StateCharacteristicsPage.vue";
import SeverityRulesPage from "../pages/expert/SeverityRulesPage.vue";
import DiagnosisRulesPage from "../pages/expert/DiagnosisRulesPage.vue";

import MonitoringPage from "../pages/user/MonitoringPage.vue";
import ObservationHistoryPage from "../pages/user/ObservationHistoryPage.vue";
import DiagnosisPage from "../pages/user/DiagnosisPage.vue";

const routes = [
  {
    path: "/",
    redirect: "/role-select",
  },
  {
    path: "/role-select",
    name: "role-select",
    component: RoleSelectView,
  },

  {
    path: "/expert",
    component: ExpertLayout,
    children: [
      { path: "", redirect: "/expert/diagnoses" },
      { path: "diagnoses", component: DiagnosesPage },
      { path: "indicators", component: IndicatorsPage },
      { path: "severity-names", component: SeverityNamesPage },
      { path: "possible-values", component: PossibleValuesPage },
      { path: "normal-values", component: NormalValuesPage },
      { path: "state-characteristics", component: StateCharacteristicsPage },
      { path: "severity-rules", component: SeverityRulesPage },
      { path: "diagnosis-rules", component: DiagnosisRulesPage },
    ],
  },

  {
    path: "/user",
    component: UserLayout,
    children: [
      { path: "", redirect: "/user/monitoring" },
      { path: "monitoring", component: MonitoringPage },
      { path: "history", component: ObservationHistoryPage },
      { path: "diagnosis", component: DiagnosisPage },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;