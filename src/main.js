import { createApp } from 'vue';
import App from './App.vue';
import { createRouter, createWebHistory } from 'vue-router';
import EvaluationHistory from './components/EvaluationHistory.vue'; // 修改名称

const routes = [
  { path: '/', component: App },
  { path: '/history', component: EvaluationHistory } // 修改名称
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

const app = createApp(App);
app.use(router);
app.mount('#app');
