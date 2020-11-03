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
        :options="geoJsonOptions(layer)"
        :options-style="styleFunction(layer)"
        @rendered="onRendered"
      />
    </l-map>
  </div>
</template>

<script>
import * as L from 'leaflet';
import { LMap, LTileLayer } from 'vue2-leaflet';
import svgMarker from '../vendor/svg-icon';

import GiaGeoJson from './GiaGeoJson';

import 'leaflet/dist/leaflet.css';

import '@geoman-io/leaflet-geoman-free';
import '@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css';

// eslint-disable-next-line no-underscore-dangle
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  // eslint-disable-next-line global-require
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  // eslint-disable-next-line global-require
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  // eslint-disable-next-line global-require
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

export default {
  name: 'Map',
  components: {
    LMap,
    LTileLayer,
    GiaGeoJson,
  },
  props: ['geojson'],
  data() {
    return {
      zoom: 16,
      center: [60.675744, 17.1402],
      layers: [],
      fillColor: '#e4ce7f',
      // url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      url: 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    };
  },
  methods: {
    onRendered(id) {
      this.$emit('rendered', id);
    },
    boundsUpdate(bounds) {
      this.$emit('boundsUpdate', bounds);
    },
    zoomUpdate(zoom) {
      if (this.$refs.theMap.mapObject.pm !== undefined) {
        if (zoom >= 16 && (this.layers && this.layers.length >= 1)) {
          this.$refs.theMap.mapObject.pm.addControls();
        } else {
          this.$refs.theMap.mapObject.pm.Toolbar.triggerClickOnToggledButtons();
          this.$refs.theMap.mapObject.pm.removeControls();
        }
      }
      this.$emit('zoomUpdate', zoom);
    },
    getDataBounds() {
      const map = this.$refs.theMap.mapObject;
      // eslint-disable-next-line no-underscore-dangle
      let swCoord = map.getBounds()._southWest;
      // eslint-disable-next-line no-underscore-dangle
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
    geoJsonOptions(layer) {
      return {
        // onEachFeature: this.onEachFeatureFunction,
        pointToLayer: (feature, latlng) => {
          return svgMarker(latlng, this.pointStyle(layer));
        },
        layer,
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
    geojson: {
      handler() {
        console.debug('geojson updated');
        const layers = Object.values(this.geojson);
        this.layers = layers;
        if (this.$refs.theMap.mapObject.pm !== undefined) {
          if (this.$refs.theMap.mapObject.getZoom() >= 16 && (this.layers && this.layers.length >= 1)) {
            this.$refs.theMap.mapObject.pm.addControls();
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
      map.on('pm:globaldragmodetoggled', (e) => {
        console.debug('globaldragmodetoggled: ', e);

        if (e.enabled) {
          // TODO: Fix this
          // eslint-disable-next-line guard-for-in,no-restricted-syntax,no-underscore-dangle
          for (const id in e.map._layers) {
            console.debug('id: ', id);
            // eslint-disable-next-line no-underscore-dangle
            e.map._layers[id].on('pm:edit', (ev) => {
              console.debug('edit: ', ev);
              if (ev.target.feature != null) {
                this.$emit('itemModified', ev.target.toGeoJSON());
              }
            });
          }
        }
      });

      map.on('pm:globaleditmodetoggled', (e) => {
        console.debug('globaleditmodetoggled: ', e);

        if (e.enabled) {
          // TODO: Fix this
          // eslint-disable-next-line guard-for-in,no-restricted-syntax,no-underscore-dangle
          for (const id in e.map._layers) {
            console.debug('id: ', id);
            // eslint-disable-next-line no-underscore-dangle
            e.map._layers[id].on('pm:edit', (ev) => {
              console.debug('edit: ', ev);
              if (ev.target.feature != null) {
                this.$emit('itemModified', ev.target.toGeoJSON());
              }
            });
          }
        }
      });

      map.on('pm:remove', (layerEvent) => {
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
      });
    });
  },
  computed: {
    onEachFeatureFunction() {
      /*
      if (!this.enableTooltip) {
        return () => {};
      }
      */
      return () => {};

      /*
      return (feature, layer) => {
        layer.on('pm:update', args => {
            console.debug("pm:update", args);
            const geojsonData = this.$refs.geojsonChild.getGeoJSONData();
            console.debug(geojsonData);
            this.$emit('geojsonUpdate', geojsonData)
        });
        
        layer.bindTooltip(
          "<div>id:" +
            feature.properties.id +
            "</div><div>name: " +
            feature.properties.name +
            "</div>",
          { permanent: false, sticky: true }
        );
        
      };
      */
    },
  },
};
</script>
