import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue'
import App from './App.vue'
import Vuetify from 'vuetify/lib'

//import './styles/overrides.sass';

Vue.use(Vuetify);
Vue.config.productionTip = false
new Vue({
  vuetify: new Vuetify({
    theme: {
      themes: {
        light: {
          primary: '#333',
          secondary: '#999',
          anchor: '#000',
        }
      },
    },
  }),  
  render: h => h(App)
}).$mount('#app')
