import Vue from 'vue'
import { BootstrapVue } from 'bootstrap-vue'
import App from './App.vue'
import Vuetify from "vuetify";
import "vuetify/dist/vuetify.min.css";

Vue.use(Vuetify);
Vue.config.productionTip = false
Vue.use(BootstrapVue)
new Vue({
  vuetify: new Vuetify(),
  render: h => h(App)
}).$mount('#app')
