<template>
  <v-app>
    <v-content>
      <v-container :fluid="true" class="pa-0">
        <v-row no-gutter>
          <v-col sm="2" class="firstCol" style="height: 100vh; overflow-y: scroll; overflow-x: hidden">
            <Tree
              v-bind:sortedCollections="sortedCollections"
              @selectionUpdate="selectionUpdate"
              @activeUpdate="activeUpdate"
              ref="collectionTree"
            />

            <!-- unsaved changes dialog start -->

            <div class="my-3 export-image-button ma-3 flex-grow-0 flex-shrink-0">
              <v-dialog v-model="showUnsavedChangesDialog" persistent max-width="290" style="z-index: 999">
                <v-card>
                  <v-card-title class="headline">Unsaved changes</v-card-title>
                  <v-card-text>
                    You have unsaved changes that are about to be lost due to panning or zooming the map with auto fetch enabled.
                    Do you want to save your changes first?
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" text @click="onDenySaveChanges"
                      >No</v-btn
                    >
                    <v-btn color="primary" text @click="onConfirmSaveChanges">Yes</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </div>

            <!-- unsaved changes dialog end -->

            <div class="my-3 export-image-button ma-3 flex-grow-0 flex-shrink-0">
              <v-dialog v-model="showDeleteConfirmationDialog" persistent max-width="290" style="z-index: 999">
                <template v-slot:activator="{ on }">
                  <v-btn
                    small
                    color="primary"
                    v-on="on"
                    @click="onDeleteCollectionsClick"
                    :disabled="!authenticated || renderedCollections.length === 0"
                    block
                    >Delete selected collections</v-btn
                  >
                </template>
                <v-card>
                  <v-card-title class="headline">Delete collections?</v-card-title>
                  <v-card-text v-html="deleteConfirmationContent" />
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" text @click="showDeleteConfirmationDialog = false"
                      >No</v-btn
                    >
                    <v-btn color="primary" text @click="onConfirmDeleteCollections">Yes</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </div>
            <div class="mx-3 pa-0">
              <v-dialog v-model="showCreateCollectionDialog" width="400" style="z-index: 999">
                <template v-slot:activator="{ on }">
                  <v-btn
                    @click="showCreateCollectionDialog = true"
                    small
                    color="primary"
                    :disabled="!authenticated"
                    v-on="on"
                    >Create collection...</v-btn>
                </template>

                <v-card>
                  <v-card-text>
                    <v-card-title class="headline">Create collection</v-card-title>
                    <v-text-field v-model="collectionName" label="Collection name"></v-text-field>
                    <v-tabs v-model="selectedTab">
                      <v-tab>Empty</v-tab>
                      <v-tab>From file</v-tab>
                      <v-tab>Copy</v-tab>

                      <v-tab-item class="mt-3">
                      </v-tab-item>
                      <v-tab-item class="mt-3">
                        <v-card>
                          <v-card-text>
                            <div class="text--primary">
                              You can optionally select a zip file containing GeoJSON and/or Shapefiles
                            </div>
                            <v-file-input
                              accept=".zip"
                              show-size
                              placeholder="Select .zip file..."
                              @change="onFileSelected"
                              style="font-size: 13px; line-height: 15px"
                            ></v-file-input>
                          </v-card-text>
                        </v-card>
                      </v-tab-item>
                      <v-tab-item class="mt-3">
                        <v-card>
                          <v-card-text>
                            <div class="text--primary">
                              Select the collection from which items will be copied
                            </div>
                            <v-select
                              v-model="selectedSourceCollection"
                              :items="collections"
                              item-text="name"
                              item-value="uuid"
                              return-object
                              dense
                              outlined
                            ></v-select>
                          </v-card-text>
                        </v-card>
                      </v-tab-item>
                    </v-tabs>
                    <div class="d-flex justify-space-between ma-0 mt-3">
                      <v-checkbox
                        v-model="isPublicCollection"
                        label="Public"
                        class="ma-0 pa-0"
                      ></v-checkbox>
                      <v-btn
                        @click="onCreateCollectionClick"
                        small
                        color="primary"
                        :disabled="!authenticated"
                        >Create</v-btn
                      >
                    </div>
                  </v-card-text>
                </v-card>
              </v-dialog>
            </div>

            <!-- properties dialog start -->

            <div class="mx-3 my-3 pa-0" style="z-index: 999">
              <v-dialog v-model="showPropEditDialog" width="600">

                <v-card>
                  <v-card-text>
                    <v-card-title class="headline">Edit properties</v-card-title>

                    <PropertyEditor :properties="selectedItemProperties" @propertiesUpdate="onPropertiesUpdate"></PropertyEditor>
                    <v-row>
                      <v-col class="text-left">
                        <v-btn @click="onUpdatePropertiesClick" small color="primary">Update</v-btn>
                      </v-col>
                      <v-col class="text-right">
                        <v-btn @click="showPropEditDialog=false" small color="primary">Close</v-btn>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-dialog>
            </div>

            <!-- properties dialog end -->

            <div v-show="!authenticated">
              <div class="ma-3">
                <v-text-field v-model="email" label="Email"></v-text-field>
                <v-text-field
                  v-model="password"
                  :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="showPassword ? 'text' : 'password'"
                  @click:append="showPassword = !showPassword"
                  label="Password"
                ></v-text-field>
              </div>
              <div class="d-flex justify-space-between ma-3">
                <v-row>
                  <v-col cols="12">
                    <v-btn @click="onLoginClick" small color="primary" class="">Login</v-btn>
                  </v-col>
                  <v-col cols="12">
                    <v-btn @click="onRegisterClick" small color="primary" class="">Register</v-btn>
                  </v-col>
                </v-row>
              </div>
            </div>
            <div v-show="authenticated">
              <div class="d-flex justify-space-between ma-3">
                <v-btn @click="onLogoutClick" small color="primary" class="">Logout</v-btn>
              </div>
            </div>
            <div class="ma-3">
              <v-alert
                v-for="alert in alerts.slice().reverse()"
                :key="alert.ts"
                :type="alert.type"
                dismissible
              >
                {{ alert.message }}
              </v-alert>
            </div>
          </v-col>
          <v-col sm="7" class="mapCol" style="padding: 0px; position: relative">
            <v-progress-circular
              :indeterminate="isLoading"
              color="light-blue"
              style="position: absolute; top: 4px; right: 4px; z-index: 999"
            ></v-progress-circular>
            <v-btn @click="onManualDataFetchClick" small color="primary" style="position: absolute; top: 4px; right: 48px; z-index: 999">
              <v-icon>mdi-reload</v-icon>
            </v-btn>
            <v-checkbox label="Auto fetch" v-model="autoFetchEnabled" class="ma-0" style="position: absolute; top: 4px; right: 110px; z-index: 999"/>
            <Map
              ref="leafletMap"
              v-bind:geojson="geojson"
              v-bind:activeId="activeId"
              @geojsonUpdate="geojsonUpdateFromMap"
              @boundsUpdate="boundsUpdate"
              @itemRemoved="itemRemovedFromMap"
              @itemAdded="itemAddedToMap"
              @itemModified="itemModified"
              @zoomUpdate="zoomUpdate"
              @rendered="onRendered"
              @itemClicked="onItemClicked"
            />
            <v-btn
              @click="showPropEditDialog = true"
              small
              color="primary"
              :disabled="!selectedItem"
              style="position: absolute; bottom: 4px; left: 4px; z-index: 999"
            >Edit properties...</v-btn>
          </v-col>
          <v-col
            sm="3"
            class="codeCol"
            style="
              display: flex;
              flex-direction: column;
              background-color: #4b4b4b;
              height: 100vh;
              padding: 0;
            "
          >
            <v-tabs class="mytabs code-column">
              <v-tab>Code</v-tab>
              <v-tab-item style="display: flex; flex-direction: column; flex: 1">
                <Code ref="code" v-bind:code="code" @geojsonUpdate="geojsonUpdateFromCode" style="display: flex; flex-direction: column; flex: 1" />
              </v-tab-item>
            </v-tabs>
            <div class="selectedCollectionName">
              Collection name: <span>{{ activeCollection && activeCollection.name }}</span>
            </div>
            <div class="my-2 save-button">
              <v-btn small color="primary" @click="onSaveClick" :disabled="!authenticated || !(zoom >= 16) || !dirty"
                >Save modifications</v-btn
              >
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
/* eslint-disable no-underscore-dangle,no-restricted-syntax,no-await-in-loop */

// import Table from "./components/Table.vue";
import leafletImage from 'leaflet-image';
import debounce from 'debounce-async';
import cloneDeep from 'lodash.clonedeep';
import { v4 as uuidv4 } from 'uuid';
import PropertyEditor from "./components/PropertyEditor.vue";
import Map from './components/Map.vue';
import Code from './components/Code.vue';
import Tree from './components/Tree.vue';
import collection from './services/collection';
import modify from './services/modify';
import session from './services/session';
import user from './services/user';

function groupBy(xs, key) {
  return xs.reduce((rv, x) => {
    // eslint-disable-next-line no-param-reassign
    (rv[x[key]] = rv[x[key]] || []).push(x);
    return rv;
  }, {});
}

function selectColor(colorNum, colors) {
  // eslint-disable-next-line no-param-reassign
  if (colors < 1) colors = 1; // defaults to one color - avoid divide by zero
  // const saturation = 60 + (colorNum % 5) * 10;
  const saturation = 100;
  return `hsl(${(colorNum * (360 / colors)) % 360},${saturation}%,50%)`;
}

export default {
  name: 'App',
  components: {
    PropertyEditor,
    // Table,
    Map,
    Code,
    Tree,
  },
  data() {
    return {
      activeCollection: null,
      activeId: null,
      alerts: [],
      authenticated: false,
      bounds: null,
      code: '',
      collectionColors: {},
      collectionName: null,
      collections: [],
      dataBounds: null,
      deleteConfirmationContent: null,
      dirty: false,
      email: null,
      fetchController: null,
      geojson: {},
      isLoading: false,
      isLoadingUuids: new Set(),
      isPublicCollection: false,
      orgGeojson: {},
      password: null,
      renderedCollections: [],
      showDeleteConfirmationDialog: false,
      showPassword: false,
      sortedCollections: [],
      zoom: 16,
      file: null,
      showCreateCollectionDialog: false,
      selectedTab: null,
      selectedSourceCollection: null,
      selectedItem: null,
      selectedItemProperties: null,
      showPropEditDialog: false,
      autoFetchEnabled: true,
      showUnsavedChangesDialog: false,
    };
  },
  watch: {

  },
  methods: {
    async onConfirmSaveChanges() {
      this.showUnsavedChangesDialog = false;
      await this.saveChanges();
      this.fetchGeoJson(this.renderedCollections.map((c) => c.uuid));
    },
    onDenySaveChanges() {
      this.showUnsavedChangesDialog = false;
      this.fetchGeoJson(this.renderedCollections.map((c) => c.uuid));
    },
    onManualDataFetchClick() {
      this.fetchGeoJson(this.renderedCollections.map((c) => c.uuid));
    },
    onPropertiesUpdate(properties) {
      this.selectedItemProperties = properties
    },
    onUpdatePropertiesClick() {
      this.selectedItem.properties = cloneDeep(this.selectedItemProperties);
      this.itemModified(this.selectedItem);
    },
    onItemClicked(layer) {
      if (layer.selectionInfo == null || !layer.selectionInfo.selected) {
        this.$refs.code.find(layer.feature.id);
        this.selectedItem = layer.feature;
        this.selectedItemProperties = layer.feature.properties;
      } else {
        this.selectedItem = null;
        this.selectedItemProperties = null;
      }
    },
    onFileSelected(file) {
      console.debug("onFileSelected: ", file);
      this.file = file;
    },
    geojsonUpdateFromCode(geojson) {
      console.debug('geojsonUpdateFromCode');
      this.geojson[this.activeId].geojson = geojson;
      this.dirty = true
    },
    geojsonUpdateFromMap(geojson) {
      console.debug('geojsonUpdateFromMap');
      this.updateCodeView(geojson);
    },
    onRendered(id) {
      console.debug('onRendered', id);
      this.isLoadingUuids.delete(id);
      this.isLoading = this.isLoadingUuids.size > 0;
    },
    updateCodeView(val) {
      console.debug('update code view');
      const dataLength = JSON.stringify(val).length;
      if (dataLength > 1000 * 1000) {
        this.code = `Data too big, ${dataLength}`;
      } else {
        this.code = val;
      }
    },
    setGeoJson(id, geojson) {
      this.$set(this.geojson, id, {
        id,
        color: this.collectionColors[id],
        geojson,
      });
      this.orgGeojson[id] = cloneDeep(geojson);
      console.debug('$set geojson');
    },
    deleteGeoJson(id) {
      this.$delete(this.geojson, id);
      delete this.orgGeojson[id];
    },
    async selectionUpdate(ids) {
      console.debug('selectionUpdate', ids);
      let index = -1;
      this.renderedCollections.forEach((c) => {
        if (!ids.includes(c.uuid)) {
          index = this.renderedCollections.indexOf(c);
          this.deleteGeoJson(c.uuid)
        }
      });
      this.renderedCollections.splice(index, 1);
      await this.fetchGeoJson(
        ids.filter((id) => !this.renderedCollections.some((c) => c.uuid === id))
      );
      this.updateFetchedCollections(ids);
    },
    async activeUpdate(id) {
      console.debug("activeUpdate", id);
      this.activeId = id;
      if(id === null) {
        this.activeCollection = null;
        this.updateCodeView({});
        return;
      }
      if(this.isLoadingUuids.size > 0) return;
      this.activeCollection = this.collections.find((c) => c.uuid === id);
      this.updateCodeView(this.geojson[id].geojson);
    },
    updateFetchedCollections(ids) {
      console.debug('updateFetchedCollections');
      this.renderedCollections = this.collections.filter((c) => ids.some((id) => id === c.uuid));
    },
    zoomUpdate(zoom) {
      if (this.zoom !== zoom) {
        console.debug('zoomUpdate');
        if (this.autoFetchEnabled) {
          this.fetchGeoJson(this.renderedCollections.map((c) => c.uuid));
        }
      }
      this.zoom = zoom;
      /*
      if (Math.abs(this.zoom - zoom) >= 2) {
        console.debug("fetched zoom exceeded");
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
        maxY: bounds._northEast.lat,
      };

      if (this.renderedCollections.length > 0) {
        if (this.dataBounds != null) {
          const boundsExceeded =
            this.dataBounds.minX > this.bounds.minX ||
            this.dataBounds.minY > this.bounds.minY ||
            this.dataBounds.maxX < this.bounds.maxX ||
            this.dataBounds.maxY < this.bounds.maxY;

          if (boundsExceeded) {
            console.debug('data bounds exceeded');
            if (this.autoFetchEnabled) {
              if (this.dirty) {
                this.showUnsavedChangesDialog = true;
              } else {
                this.fetchGeoJson(this.renderedCollections.map((c) => c.uuid));
              }
            }
          } else {
            console.debug('still within fetched bounds');
          }
        }
      }
    },
    itemRemovedFromMap(item) {
      console.debug("itemRemovedFromMap");
      const fc = this.geojson[this.activeId].geojson;
      const i = fc.features.indexOf(item);
      fc.features.splice(i, 1);
      this.dirty = true;
    },
    itemAddedToMap(item) {
      console.debug("itemAddedToMap")
      const fc = this.geojson[this.activeId].geojson;
      fc.features.push({...item, id: `tmp_${uuidv4()}`});
      this.dirty = true;
    },
    itemModified(item) {
      console.debug("itemModified", item);
      const fc = this.geojson[this.activeId].geojson;
      if(item.id) {
        const oldItem = fc.features.find((f) => f.id === item.id);
        if (oldItem) {
          oldItem.type = item.type;
          oldItem.geometry = item.geometry;
          oldItem.properties = item.properties;
        }
      }
      this.dirty = true;
    },
    async saveChanges() {
      if (this.authenticated && this.zoom >= 16 && this.dirty) {
        await modify.commit(this.orgGeojson[this.activeId], this.geojson[this.activeId].geojson, this.activeId).catch((error) => console.error('backend error: ', error));
        await this.fetchGeoJson([this.activeId]);
      }
    },
    async onSaveClick() {
      await this.saveChanges();
    },
    onExportImageClick() {
      const map = this.$refs.leafletMap.$refs.theMap.mapObject;

      leafletImage(map, (err, canvas) => {
        const a = document.createElement('a');
        a.download = 'image.png';
        a.href = canvas.toDataURL('image/png');
        a.click();
      });
    },
    onDeleteCollectionsClick() {
      this.deleteConfirmationContent = `Are you sure you want to delete the following collections?</br></br>${this.renderedCollections
        .map((c) => c.name)
        .join('</br>')}</br></br>This cannot be undone.`;
      this.showDeleteConfirmationDialog = true;
    },
    async onConfirmDeleteCollections() {
      this.showDeleteConfirmationDialog = false;

      for (const coll of this.renderedCollections) {
        await collection.removeCollectionItems(coll.uuid);
        await collection.remove(coll.uuid);

        if (this.activeId === coll.uuid)
          this.activeId = null;

        this.$refs.collectionTree.removeCollection(coll);
      }
    },
    async onCreateCollectionClick() {
      let createPromise;

      this.showCreateCollectionDialog = false;

      switch (this.selectedTab) {
        case 0:
          createPromise = collection.create(this.collectionName, this.isPublicCollection);
          break;
        case 1:
          createPromise = collection.createFromFile(this.collectionName, this.isPublicCollection, this.file);
          break;
        case 2:
          createPromise = collection.createFromCollection(this.selectedSourceCollection, this.collectionName, this.isPublicCollection);
          break;
        default:
          throw new Error("invalid selectedTab, should not happen");
      }

      await createPromise
        .then((coll) => {
          this.collections.push(coll);
          const color = selectColor(Object.keys(this.sortedCollections).length, Object.keys(this.sortedCollections).length + 1);
          // eslint-disable-next-line no-param-reassign
          coll.color = color;
          this.collectionColors[coll.uuid] = color;

          if (this.sortedCollections[coll.name] != null) {
            this.sortedCollections[coll.name].push(coll);
          } else {
            this.sortedCollections[coll.name] = [coll];
          }

          this.$refs.collectionTree.addCollection(coll);
          this.addAlert({ type: 'success', message: `Created ${this.collectionName} successfully` });
          this.collectionName = null;
          this.isPublicCollection = false;
        })
        .catch((error) => {
          console.error('backend error: ', error);
          this.addAlert({ type: 'error', message: `Creating ${this.collectionName} failed` });
        });
    },
    async showAvailableCollections() {
      this.collections = await collection.fetchCollections();
      const sortedCollections = groupBy(this.collections, 'name');
      const len = Object.keys(sortedCollections).length;
      let i = 1;
      for (let value of Object.values(sortedCollections)) {
        const color = selectColor(i, len);
        value = value.map((c) => {
          // eslint-disable-next-line no-param-reassign
          c.color = color;
          this.collectionColors[c.uuid] = color;
          return c;
        });
        i += 1;
      }

      this.sortedCollections = sortedCollections;
      console.debug('sorted collections');
    },
    addAlert(alert) {
      this.alerts.push({ ...alert, ...{ ts: Date() } });
    },
    async onLoginClick() {
      await session
        .create(this.email, this.password)
        .then(() => {
          this.addAlert({ type: 'success', message: 'Login successful' });
          this.authenticated = true;
          return this.showAvailableCollections();
        })
        .catch((error) => {
          console.error('backend error: ', error);
          this.addAlert({ type: 'error', message: 'Could not login! Check credentials' });
        });
    },
    async onLogoutClick() {
      session.clear();
      this.authenticated = false;
      return this.showAvailableCollections();
    },
    async onRegisterClick() {
      await user
        .create(this.email, this.password)
        .then(() => {
          this.addAlert({ type: 'success', message: 'Register successful' });
          session.create(this.email, this.password).then(() => {
            this.addAlert({ type: 'success', message: 'Login successful' });
            this.authenticated = true;
            return this.showAvailableCollections();
          });
        })
        .catch((error) => {
          console.error('backend error: ', error);
          this.addAlert({ type: 'error', message: error.message });
        });
    },
    async fetchGeoJson(ids) {
      console.debug('fetchGeoJson');
      this.isLoading = ids.length > 0 || this.isLoading;
      ids.forEach((id) => this.isLoadingUuids.add(id));
      if (this.debouncedDoFetchGeoJson === undefined) {
        this.debouncedDoFetchGeoJson = debounce(this.doFetchGeoJson, 100);
      }
      try {
        await this.debouncedDoFetchGeoJson(ids);
      } catch (err) {
        console.error(err);
      }

    },
    async doFetchGeoJson(ids) {
      console.debug('doFetchGeoJson');
      if (this.fetchController) {
        this.fetchController.abort();
      }

      this.fetchController = new AbortController();
      const { signal } = this.fetchController;
      const dataBounds = this.$refs.leafletMap.getDataBounds();
      const simplify = this.zoom >= 16 ? 0.0 : Math.abs(dataBounds.maxX - dataBounds.minX) / 2500;

      for (const id of ids) {
        try {
          const data = await collection.fetchItems(signal, id, dataBounds, simplify);
          this.setGeoJson(id, data);
        } catch (err) {
          console.error(err);
          this.isLoadingUuids.delete(id);
          return;
        }
      }
      this.dataBounds = dataBounds;
      this.dirty = false;
      if(this.activeId !== null) {
        this.activeCollection = this.collections.find((c) => c.uuid === this.activeId);
        this.updateCodeView(this.geojson[this.activeId].geojson);
      }
    },
  },

  async created() {
    if (process.env.NODE_ENV === 'development') {
      this.email = process.env.VUE_APP_EMAIL;
      this.password = process.env.VUE_APP_PASSWORD;
    }
    session.load();
    this.authenticated = session.authenticated();
    await this.showAvailableCollections();
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.firstCol .v-btn, .codeCol .v-btn {
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

.selectedCollectionName {
  text-align: center;
  font-size: 14px;
  padding: 10px 10px 0px;
  color: white;
}
.selectedCollectionName span{
  font-weight: bold;
}
</style>
