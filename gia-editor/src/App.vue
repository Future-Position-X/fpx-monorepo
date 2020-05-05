<template>
  <v-app>
    <v-content>
      <v-container :fluid="true">
        <v-row no-gutter>
          <v-col sm="2">
            <Tree v-bind:collections="collections" @selectionUpdate="selectionUpdate" />
          </v-col>
          <v-col sm="7">
            <Map v-bind:geojson="geojson" @geojsonUpdate="geojsonUpdateFromMap" />
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
      show: true,
      loading: false,
      collections: [],
      geojson: {},
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
    },
    selectionUpdate(ids) {
      this.fetchGeoJson(ids);
    },
    async fetchGeoJson(ids) {
      const idsToShow = Object.keys(this.geojson).filter(function(key) {
        return ids.includes(key);
      });
      for (let key in this.geojson) {
        this.$set(this.geojson[key], "show", idsToShow.includes(key));
      }

      const newIds = ids.filter(id => !Object.keys(this.geojson).includes(id));
      console.log(newIds);
      for (let id of newIds) {
        const response = await fetch(
          `https://dev.gia.fpx.se/collections/${id}/items/geojson?offset=0&limit=10000`,
          {
            headers: {
              Authorization:
                "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
            }
          }
        );
        const data = await response.json();

        this.$set(this.geojson, id, {
          id: id,
          geojson: data,
          show: true
        });
      }
    }
  },
  async created() {
    const response = await fetch("https://dev.gia.fpx.se/collections", {
      headers: {
        Authorization:
          "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
      }
    });
    const data = await response.json();
    this.collections = data;
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
