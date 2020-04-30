<template>
  <div style="height: 100%">
    <div>
      <span v-if="loading">Loading...</span>
      <!--
      <label for="checkbox">GeoJSON Visibility</label>
      <input id="checkbox" v-model="show" type="checkbox" />
      <label for="checkboxTooltip">Enable tooltip</label>
      <input id="checkboxTooltip" v-model="enableTooltip" type="checkbox" />
      <input v-model="fillColor" type="color" />
      <br />
      -->
    </div>
    <l-map ref="theMap" :zoom="zoom" :center="center" style="height: 100vh; width: 100%">
      <l-tile-layer :url="url" :attribution="attribution" />
      <l-geo-json ref="geojsonChild" v-if="show" :geojson="geojson" :options="options" :options-style="styleFunction" />
    </l-map>
  </div>
</template>

<script>
import { LMap, LTileLayer, LGeoJson } from "vue2-leaflet";
import 'leaflet/dist/leaflet.css';

import "@geoman-io/leaflet-geoman-free";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";

import { Icon } from "leaflet";

delete Icon.Default.prototype._getIconUrl;
Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});

export default {
  name: "Map",
  components: {
    LMap,
    LTileLayer,
    LGeoJson,
  },
  props: ["loading", "show", "geojson"],
  data() {
    return {
      //loading: false,
      //show: true,
      enableTooltip: true,
      zoom: 16,
      center: [60.675744, 17.1402],
      //geojson: null,
      fillColor: "#e4ce7f",
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution:
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    };
  },
  mounted() {
    this.$nextTick(() => {
      const map = this.$refs.theMap.mapObject;
      map.pm.addControls({
        position: "topleft",
        drawCircle: false
      });

      map.on("pm:create", args => {
        console.log("pm:create", args);
      });
    });
  },
  computed: {
    options() {
      return {
        onEachFeature: this.onEachFeatureFunction
      };
    },
    styleFunction() {
      const fillColor = this.fillColor; // important! need touch fillColor in computed for re-calculate when change fillColor
      return () => {
        return {
          weight: 1,
          color: "#ECEFF1",
          opacity: 1,
          fillColor: fillColor,
          fillOpacity: 1
        };
      };
    },
    onEachFeatureFunction() {
      if (!this.enableTooltip) {
        return () => {};
      }
      return (feature, layer) => {
        layer.on('pm:update', args => {
            console.log("pm:update", args);
            const geojsonData = this.$refs.geojsonChild.getGeoJSONData();
            console.log(geojsonData);
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
    }
  }
  /*
  async created() {
    this.loading = true;
    const response = await fetch("https://dev.gia.fpx.se/collections/by_name/obstacles/items/geojson?offset=0&limit=1000", {
        headers: {
            Authorization: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI"
        }
    })
    const data = await response.json();
    this.geojson = data;
    this.loading = false;
  }
  */
};
</script>