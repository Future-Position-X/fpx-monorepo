<template>
  <div style="height: 100%">
    <l-map
      ref="theMap"
      :options="{ preferCanvas: true }"
      :zoom="zoom"
      :center="center"
      style="height: 100vh; width: 100%"
      @update:bounds="boundsUpdate"
      @update:zoom="zoomUpdate"
    >
      <l-tile-layer :url="url" :attribution="attribution" />
      <gia-geo-json
        v-for="layer in layers"
        v-bind:key="layer.id"
        :geojson="layer.geojson"
        :options="geoJsonOptions(layer, activeId)"
        :options-style="styleFunction(layer)"
        @rendered="onRendered"
        @edit="onEdit"
      />
    </l-map>
  </div>
</template>

<script>
/* eslint-disable no-underscore-dangle, guard-for-in, no-restricted-syntax,global-require */
import * as L from 'leaflet';
import { LMap, LTileLayer } from 'vue2-leaflet';
import svgMarker from '../vendor/svg-icon';

import GiaGeoJson from './GiaGeoJson';

import 'leaflet/dist/leaflet.css';

import '@geoman-io/leaflet-geoman-free';
import '@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css';

import '../vendor/pmLock';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

export default {
  name: 'Map',
  components: {
    LMap,
    LTileLayer,
    GiaGeoJson,
  },
  props: ['geojson', 'activeId'],
  data() {
    return {
      zoom: 16,
      center: [60.675744, 17.1402],
      layers: [],
      fillColor: '#e4ce7f',
      // url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      url: 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      toolbarOptions: {
        drawCircle: false,
        drawCircleMarker: false,
      }
    };
  },
  methods: {
    onRendered(id) {
      this.$emit('rendered', id);
    },
    onEdit(e) {
      console.debug(e);
      this.$emit('itemModified', e.sourceTarget.toGeoJSON());
    },
    boundsUpdate(bounds) {
      this.$emit('boundsUpdate', bounds);
    },
    zoomUpdate(zoom) {
      console.debug("zoomUpdate");
      if (this.$refs.theMap.mapObject.pm !== undefined) {
        if (zoom >= 16 && (this.layers && this.layers.length >= 1)) {
          this.$refs.theMap.mapObject.pm.addControls(this.toolbarOptions);
        } else {
          this.$refs.theMap.mapObject.pm.Toolbar.triggerClickOnToggledButtons();
          this.$refs.theMap.mapObject.pm.removeControls();
        }
      }
      this.$emit('zoomUpdate', zoom);
    },
    getDataBounds() {
      const map = this.$refs.theMap.mapObject;
      let swCoord = map.getBounds()._southWest;
      let neCoord = map.getBounds()._northEast;

      const swPoint = map.project(swCoord, map.getZoom()).subtract(map.getPixelOrigin());
      const nePoint = map.project(neCoord, map.getZoom()).subtract(map.getPixelOrigin());

      swPoint.x -= 300;
      swPoint.y += 300;
      nePoint.x += 300;
      nePoint.y -= 300;

      swCoord = map.layerPointToLatLng(swPoint);
      neCoord = map.layerPointToLatLng(nePoint);

      return {
        minX: swCoord.lng,
        minY: swCoord.lat,
        maxX: neCoord.lng,
        maxY: neCoord.lat,
      };
    },
    pointStyle(layer) {
      return {
        weight: 1,
        color: layer.color,
        opacity: 0.5,
        fillColor: layer.color,
        fillOpacity: 0.3 + Math.random() * 0.05,
        iconOptions: { color: layer.color },
      };
    },
    style(layer) {
      return {
        weight: 1,
        color: '#333',
        opacity: 0.5,
        fillColor: layer.color,
        fillOpacity: 0.3 + Math.random() * 0.05,
      };
    },
    hslToHex(hslText) {
      const csv = hslText.replace(" ", "").replace("hsl(", "").replace("%", "").replace(")", "");
      const values = csv.split(",");
      const h = parseFloat(values[0]);
      const s = parseInt(values[1], 10);
      const l = parseInt(values[2], 10) / 100;
      const a = s * Math.min(l, 1 - l) / 100;
      const f = n => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color).toString(16).padStart(2, '0');   // convert to Hex and prefix "0" if needed
      };
      return `#${f(0)}${f(8)}${f(4)}`;
    },
    invertColor(hexColor) {
      const hex = hexColor.length === 4
        ? hexColor[1] + hexColor[1] + hexColor[2] + hexColor[2] + hexColor[3] + hexColor[3]
        : hexColor;

      let r = (255 - parseInt(hex.slice(1, 3), 16)).toString(16);
      let g = (255 - parseInt(hex.slice(3, 5), 16)).toString(16);
      let b = (255 - parseInt(hex.slice(5, 7), 16)).toString(16);
      
      if (r.length === 1)
        r = `0${r}`;

      if (g.length === 1)
        g = `0${g}`;

      if (b.length === 1)
        b = `0${b}`;

      return `#${r}${g}${b}`;
    },
    getSelectedLayers() {
      return Object.entries(this.$refs.theMap.mapObject._layers)
        .map(([_, v]) => v)
        .filter(l => l.selectionInfo != null && l.selectionInfo.selected);
    },
    onEachFeatureFunction(feature, layer) {
      const properties = Object.entries(feature.properties).reduce((acc, [key, value])=>{
        if(["boolean", "number", "bigint", "string"].includes(typeof value)) {
          acc[key] = value;
        } else {
          acc[key] = typeof value;
        }
        return acc;
      }, {});
      let content = "<table class='tooltip-table'><tr><th>key</th><th>value</th></tr>\n";
      Object.entries(properties).forEach(([key, value]) => {
        content += `<tr><td>${key}</td><td>${value}</td></tr>\n`;
      });
      content += "</table>";
      layer.bindTooltip(content,
        { permanent: false, sticky: true }
      );

      if (feature.geometry.type !== "Polygon" && feature.geometry.type !== "MultiPolygon")
        return;
      
      layer.on("click", (e) => {
        if (e.target.selectionInfo == null) {
          e.target.selectionInfo = {
            selected: false,
            originalColor: e.target.options.color,
            originalWeight: e.target.options.weight
          };
        }

        e.target.selectionInfo.selected = !e.target.selectionInfo.selected;
        const styleOptions = {};

        if (e.target.selectionInfo.selected) {
          styleOptions.color = this.invertColor(this.hslToHex(e.target.options.fillColor));
          styleOptions.weight = 6;
        } else {
          styleOptions.color = e.target.selectionInfo.originalColor;
          styleOptions.weight = e.target.selectionInfo.originalWeight;
        }

        e.target.setStyle(styleOptions);
      });
    },
    geoJsonOptions(layer, activeId) {
      console.debug("geoJsonOptions", layer);
      return {
        onEachFeature: this.onEachFeatureFunction,
        pointToLayer: (feature, latlng) => {
          return svgMarker(latlng, this.pointStyle(layer));
        },
        layer,
        active: layer.id === activeId,
      };
    },
    styleFunction(layer) {
      return () => {
        if (layer.geojson.features[0].geometry.type === 'Point') {
          return this.pointStyle(layer);
        }
        return this.style(layer);
      };
    },
  },
  watch: {
    activeId: {
      handler() {
        if(this.$refs.theMap.mapObject.pm !== undefined) {
          this.$refs.theMap.mapObject.pm.disableGlobalEditMode();
        }
      }
    },
    geojson: {
      handler() {
        console.debug('map.watch.geojson.handler');
        const layers = Object.values(this.geojson);
        this.layers = layers;
        if (this.$refs.theMap.mapObject.pm !== undefined) {
          if (this.$refs.theMap.mapObject.getZoom() >= 16 && (this.layers && this.layers.length >= 1)) {
            this.$refs.theMap.mapObject.pm.addControls(this.toolbarOptions);
          } else {
            this.$refs.theMap.mapObject.pm.Toolbar.triggerClickOnToggledButtons();
            this.$refs.theMap.mapObject.pm.removeControls();
          }
        }
      },
      deep: true,
    },
  },
  mounted() {
    console.debug('Map mounted');
    this.$nextTick(() => {
      const map = this.$refs.theMap.mapObject;

      // eslint-disable-next-line no-unused-vars
      const pmLock = new L.PMLock(map, {showControl: false})

      map.on('pm:remove', (layerEvent) => {
        console.debug(layerEvent)
        const item = layerEvent.layer.feature;

        if (item != null) {
          this.$emit('itemRemoved', item);
        }
      });

      map.on('pm:create', (layerEvent) => {
        const feature = layerEvent.layer.toGeoJSON();

        if (feature != null) {
          this.$emit('itemAdded', feature);
        }
        map.removeLayer(layerEvent.layer);
      });
    });
  },
  computed: {},
};
</script>
<style>
  table.tooltip-table {
    border-collapse: collapse;
  }
  table.tooltip-table th, table.tooltip-table td {
    border: 1px solid #acacac;
    padding: 5px;
  }
</style>