<template>
  <v-app>
    <v-content>
      <v-container :fluid="true">
        <v-row no-gutter>
          <v-col sm="2">
            <Tree v-bind:collections="collections" @selectionUpdate="selectionUpdate" />
          </v-col>
          <v-col sm="7">
            <Map
              ref="leafletMap"
              v-bind:geojson="geojson"
              @geojsonUpdate="geojsonUpdateFromMap"
              @boundsUpdate="boundsUpdate"
              @itemRemoved="itemRemovedFromMap"
              @itemAdded="itemAddedToMap"
            />
          </v-col>
          <v-col sm="3">
            <v-tabs>
              <v-tab>Code</v-tab>
              <v-tab>Table</v-tab>
              <v-tab-item>
                <v-select
                  :items="renderedCollectionIds"
                  label="Collection"
                  @change="dropDownChange"
                  v-model="selectedCollectionId"
                ></v-select>
                <Code v-bind:code="code" />
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
      collections: [],
      geojson: {},
      renderedCollectionIds: [],
      selectedCollectionId: null,
      bounds: null,
      fetchedBounds: null
    };
  },
  watch: {
    selectedCollectionId(val) {
      this.code = val == null ? {} : this.geojson[val].geojson;
    }
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
      let index = -1;

      this.renderedCollectionIds.forEach(id => {
        if (!ids.includes(id)) {
          if (this.selectedCollectionId == id) {
            this.selectedCollectionId = null;
          }

          index = this.renderedCollectionIds.indexOf(id);
          this.$delete(this.geojson, id);
        }
      });

      this.renderedCollectionIds.splice(index, 1);
      this.fetchGeoJson(
        ids.filter(id => !this.renderedCollectionIds.includes(id))
      );
    },
    dropDownChange(selected) {
      console.log("selected: ", selected);
      this.code = this.geojson[selected].geojson;
    },
    boundsUpdate(bounds) {
      this.bounds = {
        minX: bounds._southWest.lng,
        minY: bounds._southWest.lat,
        maxX: bounds._northEast.lng,
        maxY: bounds._northEast.lat
      };

      if (this.renderedCollectionIds.length > 0) {
        if (this.fetchedBounds != null) {
          const boundsExceeded =
            this.fetchedBounds.minX > this.bounds.minX ||
            this.fetchedBounds.minY > this.bounds.minY ||
            this.fetchedBounds.maxX < this.bounds.maxX ||
            this.fetchedBounds.maxY < this.bounds.maxY;

          if (boundsExceeded) {
            console.log("fetched bounds exceeded");
            this.fetchGeoJson(this.renderedCollectionIds);
          } else {
            console.log("still within fetched bounds");
          }
        }
      }
    },
    itemRemovedFromMap(item) {
      const fc = this.geojson[this.selectedCollectionId].geojson;
      const i = fc.features.indexOf(item);
      fc.features.splice(i, 1);
      this.code = fc;
    },
    itemAddedToMap(item) {
      const fc = this.geojson[this.selectedCollectionId].geojson;
      fc.features.push(item);
      this.code = fc;
    },
    async fetchGeoJson(ids) {
      const centerX = (this.bounds.minX + this.bounds.maxX) / 2;
      const centerY = (this.bounds.minY + this.bounds.maxY) / 2;
      const minX = this.bounds.minX - (centerX - this.bounds.minX);
      const minY = this.bounds.minY - (centerY - this.bounds.minY);
      const maxX = this.bounds.maxX + (this.bounds.maxX - centerX);
      const maxY = this.bounds.maxY + (this.bounds.maxY - centerY);

      this.fetchedBounds = {
        minX: minX,
        minY: minY,
        maxX: maxX,
        maxY: maxY
      };

      for (let id of ids) {
        const response = await fetch(
          `https://dev.gia.fpx.se/collections/${id}/items/geojson?limit=10000&spatial_filter=within&spatial_filter.envelope.xmin=${minX}&spatial_filter.envelope.ymin=${minY}&spatial_filter.envelope.xmax=${maxX}&spatial_filter.envelope.ymax=${maxY}`,
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
          geojson: data
        });
      }

      this.renderedCollectionIds = ids;
      this.selectedCollectionId = ids[0];
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
