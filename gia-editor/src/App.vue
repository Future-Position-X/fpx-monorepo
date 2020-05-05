<template>
  <v-app>
    <v-content>
      <v-container :fluid="true">
        <v-row no-gutter>
          <v-col sm="2">
            <Tree v-bind:collections="collections" />
          </v-col>
          <v-col sm="7">
            <Map
              v-bind:geojson="geojson"
              v-bind:loading="loading"
              v-bind:show="show"
              @geojsonUpdate="geojsonUpdateFromMap"
            />
          </v-col>
          <v-col sm="3">
            <v-tabs>
              <v-tab>Code</v-tab>
              <v-tab>Table</v-tab>
              <v-tab-item>
                <Code v-bind:code="code" @geojsonUpdate="geojsonUpdateFromCode" />
              </v-tab-item>
              <v-tab-item>
                <Table />
              </v-tab-item>
            </v-tabs>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import Table from "./components/Table.vue";
import Map from "./components/Map.vue";
import Code from "./components/Code.vue";
import Tree from "./components/Tree.vue";

export default {
  name: "App",
  components: {
    Table,
    Map,
    Code,
    Tree
  },
  data() {
    return {
      code: "",
      geojson: null,
      show: true,
      loading: false,
      collections: []
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

  /* async created() {
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
  }*/
  async created() {
    //this.loading = true;
    const response = await fetch("https://dev.gia.fpx.se/collections", {
      headers: {
        Authorization:
          "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
      }
    });
    const data = await response.json();
    this.collections = data;
    //this.loading = false;
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
</style>
