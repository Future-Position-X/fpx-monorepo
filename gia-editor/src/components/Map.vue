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
        :options="options(layer)"
        :options-style="styleFunction(layer)"
      />
    </l-map>
  </div>
</template>

<script>

import * as L from "leaflet";
import { svgMarker } from "../vendor/svg-icon";

import { LMap, LTileLayer, LGeoJson } from "vue2-leaflet";

import "leaflet/dist/leaflet.css";

//import "@geoman-io/leaflet-geoman-free";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";

import glify from 'leaflet.glify';

console.log(glify)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png")
});

const fromHex = function (hex) {
  console.log(hex);
    if (hex.length < 6) return null;
    hex = hex.toLowerCase();

    if (hex[0] === '#') {
      hex = hex.substring(1, hex.length);
    }

    const r = parseInt(hex[0] + hex[1], 16)
      , g = parseInt(hex[2] + hex[3], 16)
      , b = parseInt(hex[4] + hex[5], 16)
      ;
    return { r: r / 255, g: g / 255, b: b / 255 };
  };
const hslToHex = function(hslStr) {
  console.log(hslStr);
  let {res, h, s, l} = hslStr.match(/hsl\((?<h>\d+.?\d*),(?<s>\d+.?\d*)%,(?<l>\d+.?\d*)%\)/).groups
  console.log(res,h,s,l);
  h /= 360;
  s /= 100;
  l /= 100;
  let r, g, b;
  if (s === 0) {
    r = g = b = l; // achromatic
  } else {
    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1 / 3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1 / 3);
  }
  const toHex = x => {
    const hex = Math.round(x * 255).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

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
      //url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      url: "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
      attribution:
        '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    };
  },
  methods: {
    boundsUpdate(bounds) {
      this.$emit("boundsUpdate", bounds);
    },
    zoomUpdate(zoom) {
      /*
      if (zoom >= 16) {
        this.$refs.theMap.mapObject.pm.addControls();
      } else {
        this.$refs.theMap.mapObject.pm.Toolbar.triggerClickOnToggledButtons();
        this.$refs.theMap.mapObject.pm.removeControls();
      }
      */
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
    pointStyle(layer) {
          return {
            weight: 1,
            color: layer.color,
            opacity: 0.5,
            fillColor: layer.color,
            fillOpacity: 0.3 + Math.random() * 0.05,
            iconOptions: { color: layer.color }
          };
    },
    style(layer) {
          return {
            weight: 1,
            color: "#333",
            opacity: 0.5,
            fillColor: layer.color,
            fillOpacity: 0.3 + Math.random() * 0.05,
          };
    },
    options(layer) {
      return {
        onEachFeature: this.onEachFeatureFunction,
        pointToLayer: (feature, latlng) => {
          return svgMarker(latlng, this.pointStyle(layer))
        }
      };
    },
    styleFunction(layer) {
      return () => {
        if(layer.geojson.features[0].geometry.type == 'Point') {
          return this.pointStyle(layer)
        } else {
          return this.style(layer)
        }
      };
    }
  },
  watch: {
    geojson: {
      handler: function() {
        console.log("geojson updated, ", this.geojson);
        const layers = Object.values(this.geojson);
        glify.Shapes.instances.forEach(element => {
          element.remove();
        });
        glify.Shapes.instances =[];
        glify.Points.instances.forEach(element => {
          element.remove();
        });
        glify.Points.instances =[];
        glify.Lines.instances.forEach(element => {
          element.remove();
        });
        glify.Lines.instances =[];

        for (let layer of layers) {
          console.log(layer.geojson.features[0].geometry.type);
          if(layer.geojson.features[0].geometry.type == 'Point') {
            glify.points({
              size: 10,
              latitudeKey: 1,
              longitudeKey: 0,
              map: this.$refs.theMap.mapObject,
              data: layer.geojson,
              color: fromHex(hslToHex(layer.color)),
            });
          } else if(['LineString', 'MultiLineString'].includes(layer.geojson.features[0].geometry.type)) {
            glify.lines({
              size: 0.1,
              latitudeKey: 1,
              longitudeKey: 0,
              map: this.$refs.theMap.mapObject,
              data: layer.geojson,
              color: fromHex(hslToHex(layer.color)),
            });
          } else {
            glify.shapes({
              map: this.$refs.theMap.mapObject, 
              data: layer.geojson,
              color: fromHex(hslToHex(layer.color)),
            });
          }
        }
        // this.layers = layers;
      },
      deep: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      /*
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
      */
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