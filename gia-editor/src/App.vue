<template>
  <div id="app" class="container-fluid">
    <div class="row">
      <div class="col-md-2">Sidepane</div>
      <div class="col-md-6">
        <Map
          v-bind:geojson="geojson"
          v-bind:loading="loading"
          v-bind:show="show"
          @geojsonUpdate="geojsonUpdateFromMap"
        />
      </div>
      <div class="col-md-4">
        <b-tabs content-class="mt-3">
          <b-tab title="Code" active>
            <div class="codeTab">
              <Code v-bind:code="code" @geojsonUpdate="geojsonUpdateFromCode" />
            </div>
          </b-tab>
          <b-tab title="Table">
            <v-client-table v-model="tableData" :columns="columns" :options="options"></v-client-table>
          </b-tab>
        </b-tabs>
      </div>
    </div>
  </div>
</template>

<script>
import Map from "./components/Map.vue";
import Code from "./components/Code.vue";

import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

export default {
  name: "App",
  components: {
    Map,
    Code
  },
  data() {
    return {
      code: "",
      geojson: null,
      show: true,
      loading: false,
      columns: ["id", "name", "age"],
      tableData: [
        { id: 1, name: "John", age: "20" },
        { id: 2, name: "Jane", age: "24" },
        { id: 3, name: "Susan", age: "16" },
        { id: 4, name: "Chris", age: "55" },
        { id: 5, name: "Dan", age: "40" }
      ],
      options: {
        editableColumns: ['age']
      }
    };
  },
  methods: {
    geojsonUpdateFromCode(geojson) {
      console.log("geojsonUpdateFromCode");
      this.geojson = geojson;
    },
    geojsonUpdateFromMap(geojson) {
      console.log("geojsonUpdateFromMap");
      this.code = JSON.stringify(geojson, null, "  ");
    }
  },
  async created() {
    this.loading = true;
    const response = await fetch(
      "https://dev.gia.fpx.se/collections/by_name/obstacles/items/geojson?offset=0&limit=1000",
      {
        headers: {
          Authorization:
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
        }
      }
    );
    const data = await response.json();
    this.geojson = data;
    this.code = JSON.stringify(data, null, "  ");
    this.loading = false;
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.codeTab {
  position: absolute;
  top: 40px;
  bottom: 0;
  width: 100%;
  overflow: auto;
}
</style>
