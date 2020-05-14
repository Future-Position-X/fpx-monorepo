<template>
  <v-app>
    <v-content>
      <v-container :fluid="true" style="padding: 0px">
        <v-row no-gutter>
          <v-col sm="2" style="height: 100vh; overflow: scroll">
            <v-text-field v-model="collectionName" label="Collection name"></v-text-field>
            <v-checkbox v-model="isPublicCollection" label="Public"></v-checkbox>
            <v-btn @click="onCreateCollectionClick" small color="primary">Create</v-btn>
            <Tree v-bind:sortedCollections="sortedCollections" @selectionUpdate="selectionUpdate" />
          </v-col>
          <v-col sm="7" style="padding: 0px;">
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
          <v-col
            sm="3"
            style="display: flex; flex-direction:column; background-color: #4b4b4b; height: 100vh; padding: 0;"
          >
            <v-tabs class="mytabs code-column">
              <v-tab>Code</v-tab>
              <!--<v-tab>Table</v-tab>-->
              <v-tab-item style="display: flex;flex-direction:column; flex:1;">
                <v-select
                  :items="renderedCollections"
                  label="Collection"
                  @change="dropDownChange"
                  v-model="selectedCollection"
                  class="select-collection"
                  item-text="name"
                  return-object
                ></v-select>
                <Code v-bind:code="code" style="display: flex;flex-direction:column; flex:1;" />
              </v-tab-item>
              <!--
              <v-tab-item>
                <Table />
              </v-tab-item>
              -->
            </v-tabs>
            <div class="my-2 save-button">
              <v-btn small color="primary" @click="onSaveClick">Save modifications</v-btn>
            </div>
            <div class="my-2 export-image-button">
              <v-btn small color="primary" @click="onExportImageClick">Export image</v-btn>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
//import Table from "./components/Table.vue";
import Map from "./components/Map.vue";
import Code from "./components/Code.vue";
import Tree from "./components/Tree.vue";
import leafletImage from "leaflet-image";

export default {
  name: "App",
  components: {
    //Table,
    Map,
    Code,
    Tree
  },
  data() {
    return {
      code: "",
      zoom: 16,
      collections: [],
      sortedCollections: [],
      geojson: {},
      renderedCollections: [],
      selectedCollection: null,
      bounds: null,
      dataBounds: null,
      addedItems: [],
      modifiedItems: [],
      removedItems: [],
      fetchController: null,
      isFetchingItems: false,
      collectionName: null,
      isPublicCollection: false,
      collectionColors: {}
    };
  },
  watch: {
    selectedCollection(val) {
      this.code = val == null ? {} : this.geojson[val.uuid].geojson;
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

      this.renderedCollections.forEach(c => {
        if (!ids.includes(c.uuid)) {
          if (this.selectedCollection == c) {
            this.selectedCollection = null;
          }

          index = this.renderedCollections.indexOf(c);
          this.$delete(this.geojson, c.uuid);
        }
      });

      this.renderedCollections.splice(index, 1);
      this.fetchGeoJson(
        ids.filter(id => !this.renderedCollections.some(c => c.uuid == id))
      );
    },
    dropDownChange(selected) {
      console.log("selected: ", selected);
      this.code = this.geojson[selected.uuid].geojson;
    },
    zoomUpdate(zoom) {
      if (this.zoom != zoom) {
        this.fetchGeoJson(this.renderedCollections.map(c => c.uuid));
      }
      this.zoom = zoom;
      /*
      if (Math.abs(this.zoom - zoom) >= 2) {
        console.log("fetched zoom exceeded");
        this.zoom = zoom;
        this.fetchGeoJson(this.renderedCollectionIds);
      }
      */
    },
    boundsUpdate(bounds) {
      this.bounds = {
        minX: bounds._southWest.lng,
        minY: bounds._southWest.lat,
        maxX: bounds._northEast.lng,
        maxY: bounds._northEast.lat
      };

      if (this.renderedCollections.length > 0) {
        if (this.dataBounds != null) {
          const boundsExceeded =
            this.dataBounds.minX > this.bounds.minX ||
            this.dataBounds.minY > this.bounds.minY ||
            this.dataBounds.maxX < this.bounds.maxX ||
            this.dataBounds.maxY < this.bounds.maxY;

          if (boundsExceeded) {
            console.log("data bounds exceeded");
            this.fetchGeoJson(this.renderedCollections.map(c => c.uuid));
          } else {
            console.log("still within fetched bounds");
          }
        }
      }
    },
    async putAddedItems() {
      await fetch(
        `https://dev.gia.fpx.se/collections/${this.selectedCollection.uuid}/items/geojson`,
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
      const fc = this.geojson[this.selectedCollection.uuid].geojson;
      i = fc.features.indexOf(item);
      fc.features.splice(i, 1);
      this.code = fc;
    },
    itemAddedToMap(item) {
      this.addedItems.push(item);
      const fc = this.geojson[this.selectedCollection.uuid].geojson;
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
    async onCreateCollectionClick() {
      await fetch(`https://dev.gia.fpx.se/collections`, {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
          Authorization:
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
        },
        body: JSON.stringify({
          name: this.collectionName,
          is_public: this.isPublicCollection
        })
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
            color: this.collectionColors[id],
            geojson: data
          });
        } catch (err) {
          console.log(err);
          this.isFetchingItems = false;
          return;
        }
      }
      this.renderedCollections = this.collections.filter(c =>
        ids.some(id => id == c.uuid)
      );
      this.selectedCollectionId = this.collections.filter(
        c => c.uuid == ids[0]
      )[0];
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
    let sortedCollections = groupBy(this.collections, "name");
    const len = Object.keys(sortedCollections).length;
    let i = 1;
    for (let [key, value] of Object.entries(sortedCollections)) {
      console.log(key);
      let color = selectColor(i, len);
      value = value.map(c => {
        c.color = color;
        this.collectionColors[c.uuid] = color;
        return c;
      });
      i++;
    }

    this.sortedCollections = sortedCollections;
    console.log("sorted collections", this.sortedCollections);
  }
};

const groupBy = function(xs, key) {
  return xs.reduce(function(rv, x) {
    (rv[x[key]] = rv[x[key]] || []).push(x);
    return rv;
  }, {});
};
const selectColor = function(colorNum, colors) {
  if (colors < 1) colors = 1; // defaults to one color - avoid divide by zero
  //const saturation = 60 + (colorNum % 5) * 10;
  const saturation = 100;
  return (
    "hsl(" + ((colorNum * (360 / colors)) % 360) + "," + saturation + "%,50%)"
  );
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.save-button button,
.export-image-button button {
  padding: 0;
  width: 100%;
}
.theme--light.v-tabs.mytabs > .v-tabs-bar {
  background: transparent;
}

.code-column,
.code-column .v-tabs-items,
.code-column .v-window__container {
  background: #4b4b4b;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.code-column .select-collection {
  flex: 0 1 auto;
  background-color: #4b4b4b;
  padding: 5px;
}

.code-column .v-tabs-bar {
  display: none;
}
</style>
