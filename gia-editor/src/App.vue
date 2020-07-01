<template>
  <v-app>
    <v-content>
      <v-container :fluid="true" style="padding: 0px">
        <v-row no-gutter>
          <v-col sm="2" style="height: 100vh; overflow-y: scroll; overflow-x: hidden;">
            <Tree
              v-bind:sortedCollections="sortedCollections"
              @selectionUpdate="selectionUpdate"
              ref="collectionTree"
            />
            <div class="my-2 export-image-button">
              <v-dialog v-model="showDeleteConfirmationDialog" persistent max-width="290">
                <template v-slot:activator="{ on }">
                  <v-btn
                    small
                    color="primary"
                    v-on="on"
                    @click="onDeleteCollectionsClick"
                    :disabled="!authenticated"
                  >Delete selected collections</v-btn>
                </template>
                <v-card>
                  <v-card-title class="headline">Delete collections?</v-card-title>
                  <v-card-text v-html="deleteConfirmationContent" />
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" text @click="showDeleteConfirmationDialog = false">No</v-btn>
                    <v-btn color="primary" text @click="onConfirmDeleteCollections">Yes</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </div>

            <div style="background-color: #EEE">
              <v-text-field v-model="collectionName" label="Collection name"></v-text-field>
              <v-checkbox
                v-model="isPublicCollection"
                label="Public"
                style="width: 100px; float: left;"
              ></v-checkbox>
              <v-btn
                @click="onCreateCollectionClick"
                small
                color="primary"
                style="width: 100px; float: right;"
                :disabled="!authenticated"
              >Create</v-btn>
              <br clear="both" />
            </div>
            <v-btn
                @click="onLoginClick"
                small
                color="primary"
                style="width: 100px; float: right;"
              >Login</v-btn>
          </v-col>
          <v-col sm="7" style="padding: 0px;">
            <Map
              v-show="!showDeleteConfirmationDialog"
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
              <v-btn small color="primary" @click="onSaveClick" :disabled="!authenticated">Save modifications</v-btn>
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
import collection from "./services/collection";
import modify from "./services/modify";
import session from "./services/session";

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
      fetchController: null,
      isFetchingItems: false,
      collectionName: null,
      isPublicCollection: false,
      collectionColors: {},
      modCtx: modify.createContext(),
      showDeleteConfirmationDialog: false,
      deleteConfirmationContent: null,
      authenticated: false
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
    async selectionUpdate(ids) {
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
      ).then(() => this.updateFetchedCollections(ids));
    },
    updateFetchedCollections(ids) {
        this.renderedCollections = this.collections.filter(c =>
          ids.some(id => id == c.uuid)
        );
        this.selectedCollection = this.collections.filter(
          c => c.uuid == ids[ids.length - 1]
        )[0];
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
    itemRemovedFromMap(item) {
      modify.onItemRemoved(this.modCtx, item);
      const fc = this.geojson[this.selectedCollection.uuid].geojson;
      let i = fc.features.indexOf(item);
      fc.features.splice(i, 1);
      this.code = fc;
    },
    itemAddedToMap(item) {
      modify.onItemAdded(this.modCtx, item);
      const fc = this.geojson[this.selectedCollection.uuid].geojson;
      fc.features.push(item);
      this.code = fc;
    },
    itemModified(item) {
      modify.onItemModified(this.modCtx, item);
    },
    async onSaveClick() {
      await modify.commit(this.modCtx, this.selectedCollection.uuid)
        .then(() => this.modCtx = modify.createContext())
        .catch((error) => console.error("backend error: ", error));
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
    onDeleteCollectionsClick() {
      this.deleteConfirmationContent = `Are you sure you want to delete the following collections?</br></br>${this.renderedCollections
        .map(c => c.name)
        .join("</br>")}</br></br>This cannot be undone.`;
      this.showDeleteConfirmationDialog = true;
    },
    async onConfirmDeleteCollections() {
      this.showDeleteConfirmationDialog = false;

      for (let coll of this.renderedCollections) {
        await collection.remove(coll.uuid);
        this.$refs.collectionTree.removeCollection(coll);
      }
    },
    async onCreateCollectionClick() {
      await collection.create(this.collectionName, this.isPublicCollection)
      .then((coll) => this.$refs.collectionTree.addCollection(coll))
      .catch((error) => console.error("backend error: ", error));
    },
    async showAvailableCollections(){
      this.collections = await collection.fetchCollections();
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
    },
    async onLoginClick() {
      await session.create()
      .then(() => {
        this.authenticated = true;
        return this.showAvailableCollections();
      })
      .catch((error) => console.error("backend error: ", error));
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
          const data = await collection.fetchItems(
            signal,
            id,
            this.dataBounds,
            simplify
          );
          
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
      this.isFetchingItems = false;
    }
  },
  async created() {
    await this.showAvailableCollections();
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

.v-select__slot {
  background-color: #999;
}
</style>
