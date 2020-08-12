import { optionsMerger, propsBinder, findRealParent, LayerGroupMixin, OptionsMixin  } from "vue2-leaflet";
import { geoJSON, DomEvent } from 'leaflet';

/**
 * Easily display a geo-json on the map
 */
export default {
  name: 'GiaGeoJson',
  mixins: [LayerGroupMixin, OptionsMixin],
  props: {
    geojson: {
      type: [Object, Array],
      custom: true,
      default: () => ({}),
    },
    options: {
      type: Object,
      custom: true,
      default: () => ({}),
    },
    optionsStyle: {
      type: [Object, Function],
      custom: true,
      default: null,
    },
  },
  computed: {
    mergedOptions() {
      return optionsMerger(
        {
          ...this.layerGroupOptions,
          style: this.optionsStyle,
        },
        this
      );
    },
  },
  mounted() {
    console.debug("GiaGeoJson mounted")
    this.mapObject = geoJSON(this.geojson, this.mergedOptions);
    DomEvent.on(this.mapObject, this.$listeners);
    propsBinder(this, this.mapObject, this.$options.props);
    this.parentContainer = findRealParent(this.$parent, true);
    this.parentContainer.addLayer(this, !this.visible);
    this.$nextTick(() => {
      /**
       * Triggers when the component is ready
       * @type {object}
       * @property {object} mapObject - reference to leaflet map object
       */
      this.$emit('ready', this.mapObject);
      this.$emit("rendered", this.options.layer.id);
    });
  },
  beforeDestroy() {
    this.parentContainer.mapObject.removeLayer(this.mapObject);
  },
  methods: {
    setGeojson(newVal) {
      console.debug("setGeojson");
      this.mapObject.clearLayers();
      console.debug("setGeojson layers cleared");
      this.mapObject.addData(newVal);
      console.debug("setGeojson data added");
    },
    getGeoJSONData() {
      console.debug("getGeoJSONData")
      return this.mapObject.toGeoJSON();
    },
    getBounds() {
      console.debug("getBounds")
      return this.mapObject.getBounds();
    },
    setOptions(_newVal, _oldVal) {
      console.debug("setOptions")
      /*
      this.mapObject.clearLayers();
      console.debug("setOptions layers cleared")
      setOptions(this.mapObject, this.mergedOptions);
      console.debug("setOptions options set")
      this.mapObject.addData(this.geojson);
      console.debug("setOptions data added")
      */
    },
    setOptionsStyle(_newVal, _oldVal) {
      console.debug("setOptionsStyle")
        /*
      this.mapObject.setStyle(newVal);
      console.debug("setOptionsStyle style set")
      */
     this.$emit("rendered", this.options.layer.id);
    },
  },
  render() {
    return null;
  },
};