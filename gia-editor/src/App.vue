<template>
  <v-app>
    <v-content>
      <v-container :fluid="true">
        <v-row>
          <div class="my-2">
            <v-btn small color="primary" @click="onSaveClick">Save modifications</v-btn>
          </div>
          <div class="my-2">
            <v-btn small color="primary" @click="onExportImageClick">Export image</v-btn>
          </div>
          <v-progress-circular v-if="isFetchingItems" indeterminate color="primary"></v-progress-circular>
        </v-row>
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
              @itemModified="itemModified"
              @zoomUpdate="zoomUpdate"
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
import leafletImage from "leaflet-image";

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
      zoom: 16,
      collections: [],
      geojson: {},
      renderedCollectionIds: [],
      selectedCollectionId: null,
      bounds: null,
      dataBounds: null,
      addedItems: [],
      modifiedItems: [],
      removedItems: [],
      fetchController: null,
      isFetchingItems: false
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
    zoomUpdate(zoom) {
      if (Math.abs(this.zoom - zoom) >= 2) {
        console.log("fetched zoom exceeded");
        this.zoom = zoom;
        this.fetchGeoJson(this.renderedCollectionIds);
      }
    },
    boundsUpdate(bounds) {
      this.bounds = {
        minX: bounds._southWest.lng,
        minY: bounds._southWest.lat,
        maxX: bounds._northEast.lng,
        maxY: bounds._northEast.lat
      };

      if (this.renderedCollectionIds.length > 0) {
        if (this.dataBounds != null) {
          const boundsExceeded =
            this.dataBounds.minX > this.bounds.minX ||
            this.dataBounds.minY > this.bounds.minY ||
            this.dataBounds.maxX < this.bounds.maxX ||
            this.dataBounds.maxY < this.bounds.maxY;

          if (boundsExceeded) {
            console.log("data bounds exceeded");
            this.fetchGeoJson(this.renderedCollectionIds);
          } else {
            console.log("still within fetched bounds");
          }
        }
      }
    },
    async putAddedItems() {
      await fetch(
        `https://dev.gia.fpx.se/collections/${this.selectedCollectionId}/items/geojson`,
        {
          method: "PUT",
          mode: "cors",
          headers: {
            "Content-Type": "application/json",
            Authorization:
              "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
          },
          body: JSON.stringify({
            type: "FeatureCollection",
            features: this.addedItems
          })
        }
      );
    },
    async removeItems() {
      for (const item of this.removedItems) {
        await fetch(`https://dev.gia.fpx.se/items/${item.id}`, {
          method: "DELETE",
          mode: "cors",
          headers: {
            "Content-Type": "application/json",
            Authorization:
              "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
          }
        });
      }
    },
    async modifyItems() {
      await fetch(`https://dev.gia.fpx.se/items/geojson`, {
        method: "PUT",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
          Authorization:
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
        },
        body: JSON.stringify({
          type: "FeatureCollection",
          features: this.modifiedItems
        })
      });
    },
    itemRemovedFromMap(item) {
      let i;

      for (i = this.addedItems.length - 1; i >= 0; i--) {
        if (this.addedItems[i] == item) {
          this.addedItems.splice(i, 1);
        }
      }

      for (i = this.modifiedItems.length - 1; i >= 0; i--) {
        if (this.modifiedItems[i].id == item.id) {
          this.modifiedItems.splice(i, 1);
        }
      }

      this.removedItems.push(item);
      const fc = this.geojson[this.selectedCollectionId].geojson;
      i = fc.features.indexOf(item);
      fc.features.splice(i, 1);
      this.code = fc;
    },
    itemAddedToMap(item) {
      this.addedItems.push(item);
      const fc = this.geojson[this.selectedCollectionId].geojson;
      fc.features.push(item);
      this.code = fc;
    },
    itemModified(item) {
      this.modifiedItems.push(item);
    },
    async onSaveClick() {
      if (this.addedItems.length > 0) {
        await this.putAddedItems();
        this.addedItems = [];
      }

      if (this.removedItems.length > 0) {
        await this.removeItems();
        this.removedItems = [];
      }

      if (this.modifiedItems.length > 0) {
        await this.modifyItems();
        this.modifiedItems = [];
      }
    },
    onExportImageClick() {
      const map = this.$refs.leafletMap.$refs.theMap.mapObject;

      leafletImage(map, function(err, canvas) {
        var a = document.createElement("a");
        a.download = "image.png";
        a.href = canvas.toDataURL("image/png");
        a.click();
      });
    },
    async fetchGeoJson(ids) {
      if (this.fetchController) {
        this.fetchController.abort();
      }

      this.isFetchingItems = true;
      this.fetchController = new AbortController();
      const { signal } = this.fetchController;
      this.dataBounds = this.$refs.leafletMap.getDataBounds();
      const simplify =
        this.zoom >= 16
          ? 0.0
          : Math.abs(this.dataBounds.maxX - this.dataBounds.minX) / 2500;

      for (let id of ids) {
        try {
          const response = await fetch(
            `https://dev.gia.fpx.se/collections/${id}/items/geojson?limit=100000&spatial_filter=intersect&spatial_filter.envelope.xmin=${this.dataBounds.minX}&spatial_filter.envelope.ymin=${this.dataBounds.minY}&spatial_filter.envelope.xmax=${this.dataBounds.maxX}&spatial_filter.envelope.ymax=${this.dataBounds.maxY}&simplify=${simplify}`,
            {
              headers: {
                Authorization:
                  "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
              },
              signal: signal
            }
          );
          const data = await response.json();

          this.$set(this.geojson, id, {
            id: id,
            geojson: data
          });
        } catch (err) {
          console.log(err);
          return;
        }
      }
      this.renderedCollectionIds = ids;
      this.selectedCollectionId = ids[0];
      this.isFetchingItems = false;
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
