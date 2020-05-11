<template>
  <div style="height: 100%">
    <l-map
      ref="theMap"
      :zoom="zoom"
      :center="center"
      style="height: 100vh; width: 100%"
      @update:bounds="boundsUpdate"
    >
      <l-tile-layer :url="url" :attribution="attribution" />
      <l-geo-json
        v-for="layer in layers"
        v-bind:key="layer.id"
        :geojson="layer.geojson"
        :options="options"
        :options-style="styleFunction"
      />
    </l-map>
  </div>
</template>

<script>
import { LMap, LTileLayer, LGeoJson } from "vue2-leaflet";
import "leaflet/dist/leaflet.css";

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
    LGeoJson
  },
  props: ["geojson"],
  data() {
    return {
      zoom: 16,
      center: [60.675744, 17.1402],
      layers: [],
      fillColor: "#e4ce7f",
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution:
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    };
  },
  methods: {
    boundsUpdate(bounds) {
      this.$emit("boundsUpdate", bounds);
    }
  },
  watch: {
    geojson: {
      handler: function() {
        console.log("geojson updated, ", this.geojson);
        //const layers = Object.values(this.geojson);
        for (let collectionId in this.geojson) {
          if (!this.layers.some(l => l.id == collectionId)) {
            this.layers.push(this.geojson[collectionId]);
          }
        }
        //this.layers = layers;
      },
      deep: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      const map = this.$refs.theMap.mapObject;
      map.pm.addControls({
        position: "topleft",
        drawCircle: false
      });

      map.on("pm:remove", layerEvent => {
        const item = layerEvent.layer.feature;

        if (item != null) {
          this.$emit("itemRemoved", item);
        }
      });

      map.on("pm:create", layerEvent => {
        let feature;
        let latlng;
        let coords;

        switch (layerEvent.shape) {
          case "Marker":
          case "CircleMarker":
            latlng = layerEvent.layer._latlng;

            feature = {
              type: "Feature",
              geometry: {
                type: "Point",
                coordinates: [latlng.lng, latlng.lat]
              },
              properties: {}
            };
            break;

          case "Line":
            coords = layerEvent.layer._latlngs.map(latlng => [
              latlng.lng,
              latlng.lat
            ]);

            feature = {
              type: "Feature",
              geometry: {
                type: "LineString",
                coordinates: coords
              },
              properties: {}
            };
            break;

          case "Rectangle":
          case "Polygon":
            coords = layerEvent.layer._latlngs[0].map(latlng => [
              latlng.lng,
              latlng.lat
            ]);

            feature = {
              type: "Feature",
              geometry: {
                type: "Polygon",
                coordinates: [[coords]]
              },
              properties: {}
            };
            break;
        }

        this.$emit("itemAdded", feature);
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
        /*
        layer.on('pm:update', args => {
            console.log("pm:update", args);
            const geojsonData = this.$refs.geojsonChild.getGeoJSONData();
            console.log(geojsonData);
            this.$emit('geojsonUpdate', geojsonData)
        });
        */
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