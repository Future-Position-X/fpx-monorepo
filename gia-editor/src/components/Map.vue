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
// import * as turf from '@turf/turf';
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
    onMergePolygonsClick() {
      const selectedLayers = this.getSelectedLayers();
      const selectedFeatures = selectedLayers.map((l) => l.toGeoJSON());
      const coordinates = [[]];
      let properties = [];
      for(const feature of selectedFeatures) {
        if(feature.geometry.type === "Polygon") {
          coordinates[0].push(feature.geometry.coordinates[0])
          properties.push(feature.properties);
        } else if(feature.geometry.type === "MultiPolygon") {
          for (const polygon of feature.geometry.coordinates[0]) {
            coordinates[0].push(polygon)
          }
          if(feature.properties._merged_properties) {
            properties = properties.concat(feature.properties._merged_properties)
          } else {
            properties.push(feature.properties)
          }
        }
      }
      const feature = {
        type: "Feature",
        properties: {
          _merged_properties: properties
        },
        geometry: {
          type: "MultiPolygon",
          coordinates
        }
      }
      console.debug("merged", feature);
      selectedLayers.forEach(l => {
        this.$emit('itemRemoved', l.feature);
      });
      this.$emit('itemAdded', feature);
    },
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
        .filter(l => l.selectionInfo != null && l.selectionInfo.selected && l.options.pmLock !== true);
    },
    onEachFeatureFunction(feature, layer) {
      if (feature.properties.color !== undefined) {
        layer.setStyle({fillColor: feature.properties.color});
      }

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
        this.$emit("itemClicked", e.target);

        if (e.target.options.pmLock === true)
          return;

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
      const that = this;
      const map = this.$refs.theMap.mapObject;
      map.pm.Toolbar.createCustomControl({
        name: "Merge",
        block: "custom",
        title: "Merge selected polygons",
        actions: [
          { text: 'Merge selected polygons', onClick: that.onMergePolygonsClick}
        ],
        className: "leaflet-pm-icon-polygon-merge",
      });
      map.pm.removeControls();

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
  .leaflet-pm-icon-polygon-merge {
    background-image: url("data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8' standalone='no'%3F%3E%3Csvg xmlns:dc='http://purl.org/dc/elements/1.1/' xmlns:cc='http://creativecommons.org/ns%23' xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns%23' xmlns:svg='http://www.w3.org/2000/svg' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:sodipodi='http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd' xmlns:inkscape='http://www.inkscape.org/namespaces/inkscape' width='29' height='29' viewBox='0 0 29 29' version='1.1' id='svg16' sodipodi:docname='test.svg' inkscape:version='0.92.5 (2060ec1f9f, 2020-04-08)'%3E%3Cmetadata id='metadata20'%3E%3Crdf:RDF%3E%3Ccc:Work rdf:about=''%3E%3Cdc:format%3Eimage/svg+xml%3C/dc:format%3E%3Cdc:type rdf:resource='http://purl.org/dc/dcmitype/StillImage' /%3E%3Cdc:title%3E%3C/dc:title%3E%3C/cc:Work%3E%3C/rdf:RDF%3E%3C/metadata%3E%3Csodipodi:namedview pagecolor='%23ffffff' bordercolor='%23666666' borderopacity='1' objecttolerance='10' gridtolerance='10' guidetolerance='10' inkscape:pageopacity='0' inkscape:pageshadow='2' inkscape:window-width='1920' inkscape:window-height='1031' id='namedview18' showgrid='false' inkscape:zoom='9.8333333' inkscape:cx='7.779661' inkscape:cy='10.983051' inkscape:window-x='0' inkscape:window-y='25' inkscape:window-maximized='1' inkscape:current-layer='svg16' /%3E%3Cdefs id='defs3'%3E%3Cpath id='polygon-a' d='M 19.420689,9.1650973 C 19.152368,8.6699291 19,8.1027583 19,7.5 19,5.5670034 20.567003,4 22.5,4 24.432997,4 26,5.5670034 26,7.5 c 0,1.763236 -1.303853,3.221941 -3,3.464556 v 8.070888 c 1.696147,0.242615 3,1.70132 3,3.464556 0,1.932997 -1.567003,3.5 -3.5,3.5 -1.763236,0 -3.221941,-1.303853 -3.464556,-3 H 10.964556 C 10.721941,24.696147 9.263236,26 7.5,26 5.5670034,26 4,24.432997 4,22.5 4,20.567003 5.5670034,19 7.5,19 c 0.6027583,0 1.1699291,0.152368 1.6650973,0.420689 z m 1.414218,1.4142087 -10.255596,10.255597 c 0.02936,0.05419 0.05734,0.109234 0.08387,0.165097 h 8.673632 C 19.682577,20.272154 20.272154,19.682577 21,19.336816 v -8.673632 c -0.05586,-0.02654 -0.110911,-0.05451 -0.165097,-0.08387 z M 22.5,9 C 23.328427,9 24,8.3284271 24,7.5 24,6.6715729 23.328427,6 22.5,6 21.671573,6 21,6.6715729 21,7.5 21,8.3284271 21.671573,9 22.5,9 Z m 0,15 C 23.328427,24 24,23.328427 24,22.5 24,21.671573 23.328427,21 22.5,21 21.671573,21 21,21.671573 21,22.5 c 0,0.828427 0.671573,1.5 1.5,1.5 z m -15,0 C 8.3284271,24 9,23.328427 9,22.5 9,21.671573 8.3284271,21 7.5,21 6.6715729,21 6,21.671573 6,22.5 6,23.328427 6.6715729,24 7.5,24 Z' inkscape:connector-curvature='0' /%3E%3C/defs%3E%3Cg transform='translate(2.10044,2.2)' id='g14' style='fill:none;fill-rule:evenodd'%3E%3Cmask id='polygon-b' fill='%23fff'%3E%3Cuse xlink:href='%23polygon-a' id='use5' x='0' y='0' width='100%25' height='100%25' /%3E%3C/mask%3E%3Cuse xlink:href='%23polygon-a' id='use8' style='fill:%235b5b5b;fill-rule:nonzero' x='0' y='0' width='100%25' height='100%25' /%3E%3Cg mask='url(%23polygon-b)' id='g12' style='fill:%235b5b5b'%3E%3Crect width='30' height='30' id='rect10' x='0' y='0' /%3E%3C/g%3E%3C/g%3E%3Cg style='fill:none;fill-rule:evenodd' id='g32' transform='rotate(-180,13.457,13.50678)'%3E%3Cmask fill='%23fff' id='mask24'%3E%3Cuse height='100%25' width='100%25' y='0' x='0' id='use22' xlink:href='%23polygon-a' /%3E%3C/mask%3E%3Cuse height='100%25' width='100%25' y='0' x='0' style='fill:%235b5b5b;fill-rule:nonzero' id='use26' xlink:href='%23polygon-a' /%3E%3Cg style='fill:%235b5b5b' id='g30' mask='url(%23polygon-b)'%3E%3Crect y='0' x='0' id='rect28' height='30' width='30' /%3E%3C/g%3E%3C/g%3E%3C/svg%3E%0A");
  }
</style>