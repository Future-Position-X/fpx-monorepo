<template>
  <div style="height: 100%">
    <l-map
      ref="theMap"
      :options="{preferCanvas: true}"
      :zoom="zoom"
      :center="center"
      style="height: 100vh; width: 100%"
      @update:bounds="boundsUpdate"
      @update:zoom="zoomUpdate"
    >
      <l-tile-layer :url="url" :attribution="attribution" />
      <l-geo-json
        v-for="layer in layers"
        v-bind:key="layer.id"
        :geojson="layer.geojson"
        :options="options"
        :options-style="styleFunction(layer.color)"
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
    },
    zoomUpdate(zoom) {
      if (zoom >= 16) {
        this.$refs.theMap.mapObject.pm.addControls();
      } else {
        this.$refs.theMap.mapObject.pm.Toolbar.triggerClickOnToggledButtons();
        this.$refs.theMap.mapObject.pm.removeControls();
      }
      this.$emit("zoomUpdate", zoom);
    },
    getDataBounds() {
      const map = this.$refs.theMap.mapObject;
      let swCoord = map.getBounds()._southWest;
      let neCoord = map.getBounds()._northEast;

      const swPoint = map
        .project(swCoord, map.getZoom())
        .subtract(map.getPixelOrigin());
      const nePoint = map
        .project(neCoord, map.getZoom())
        .subtract(map.getPixelOrigin());

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
        maxY: neCoord.lat
      }
    },
    styleFunction(color) {
      //const fillColor = this.fillColor; // important! need touch fillColor in computed for re-calculate when change fillColor
      return () => {
        return {
          weight: 1,
          color: "#ECEFF1",
          opacity: 1,
          fillColor: color,
          fillOpacity: 0.7
        };
      };
    }
  },
  watch: {
    geojson: {
      handler: function() {
        console.log("geojson updated, ", this.geojson);
        const layers = Object.values(this.geojson);
        this.layers = layers;
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

      map.on("pm:globaldragmodetoggled", e => {
        console.log("globaldragmodetoggled: ", e);

        if (e.enabled) {
          for (let id in e.map._layers) {
            console.log("id: ", id);
            e.map._layers[id].on("pm:edit", ev => {
              console.log("edit: ", ev);
              if (ev.target.feature != null) {
                this.$emit("itemModified", ev.target.toGeoJSON());
              }
            });
          }
        }
      });

      map.on("pm:globaleditmodetoggled", e => {
        console.log("globaleditmodetoggled: ", e);

        if (e.enabled) {
          for (let id in e.map._layers) {
            console.log("id: ", id);
            e.map._layers[id].on("pm:edit", ev => {
              console.log("edit: ", ev);
              if (ev.target.feature != null) {
                this.$emit("itemModified", ev.target.toGeoJSON());
              }
            });
          }
        }
      });

      map.on("pm:remove", layerEvent => {
        const item = layerEvent.layer.feature;

        if (item != null) {
          this.$emit("itemRemoved", item);
        }
      });

      map.on("pm:create", layerEvent => {
        let feature = layerEvent.layer.toGeoJSON();

        if (feature != null) {
          this.$emit("itemAdded", feature);
        }
      });
    });
  },
  computed: {
    options() {
      return {
        onEachFeature: this.onEachFeatureFunction
      };
    },
    onEachFeatureFunction() {
      if (!this.enableTooltip) {
        return () => {};
      }

      return () => {};

      /*
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
      */
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