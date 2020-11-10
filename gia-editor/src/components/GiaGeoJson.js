/* eslint-disable no-return-assign,no-param-reassign,no-underscore-dangle */
import {
  optionsMerger,
  propsBinder,
  findRealParent,
  LayerGroupMixin,
  OptionsMixin,
} from 'vue2-leaflet';
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
    console.debug('GiaGeoJson mounted');
    console.time('GiaGeoJson mount');
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
      console.timeEnd('GiaGeoJson mount');
      this.$emit('rendered', this.options.layer.id);
    });
  },
  beforeDestroy() {
    console.time('GiaGeoJson destroy');
    this.parentContainer.mapObject.removeLayer(this.mapObject);
    console.timeEnd('GiaGeoJson destroy');
  },
  watch: {
    geojson: {
      handler(val, _oldVal) {
        console.debug('GiaGeoJson geojson watch');
        this.switchLayers(val);
      },
      deep: true,
    },
  },
  methods: {
    setGeojson(_newVal) {
      console.debug('setGeojson');
      // this.switchLayers(newVal)
      // this.clearLayers(newVal)
    },
    switchLayers(newVal) {
      console.debug('switchLayers');
      console.time('switchLayers removeLayer');
      this.parentContainer.mapObject.removeLayer(this.mapObject);
      console.timeEnd('switchLayers removeLayer');
      console.time('switchLayers geoJSON');
      this.mapObject = geoJSON(newVal, this.mergedOptions);
      this.mapObject.options.pmLock = true;
      this.mapObject.pm._layers.forEach((l) => {
        l.options.pmLock = true
      });
      console.timeEnd('switchLayers geoJSON');
      DomEvent.on(this.mapObject, this.$listeners);
      console.time('switchLayers addLayer');
      this.parentContainer.addLayer(this, !this.visible);
      console.timeEnd('switchLayers addLayer');
    },
    clearLayers(newVal) {
      console.debug('setGeojson');
      console.time('GiaGeoJson clearLayers');
      this.mapObject.clearLayers();
      console.timeEnd('GiaGeoJson clearLayers');
      console.debug('setGeojson layers cleared');
      console.time('GiaGeoJson addData');
      this.mapObject.addData(newVal);
      console.timeEnd('GiaGeoJson addData');
      console.debug('setGeojson data added');
    },
    getGeoJSONData() {
      console.debug('getGeoJSONData');
      return this.mapObject.toGeoJSON();
    },
    getBounds() {
      console.debug('getBounds');
      return this.mapObject.getBounds();
    },
    setOptions(_newVal, _oldVal) {
      console.debug('setOptions', typeof this.mapObject);
      this.mapObject.options.pmLock = !_newVal.active;
      this.mapObject.pm._layers.forEach((l) => {
        l.options.pmLock = !_newVal.active
      });

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
      console.debug('setOptionsStyle');
      /*
      this.mapObject.setStyle(newVal);
      console.debug("setOptionsStyle style set")
      */
      this.$emit('rendered', this.options.layer.id);
    },
  },
  render() {
    return null;
  },
};
