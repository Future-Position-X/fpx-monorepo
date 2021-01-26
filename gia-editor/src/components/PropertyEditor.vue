<template>
  <div class="propertyContainer" ref="propertyeditor"></div>
</template>

<script>
// import gjv from "geojson-validation";
import JSONEditor from 'jsoneditor/dist/jsoneditor';
// import 'jsoneditor/dist/jsoneditor.min.css';

export default {
  name: 'PropertyEditor',
  props: ['properties'],
  data() {
    return {
      editor: null,
    };
  },
  watch: {
    properties: {
      handler(val) {
        if (JSON.stringify(val) !== JSON.stringify(this.editor.get())) {
          console.debug('propertyeditor.set');
          this.editor.set(val);
        }
      },
      deep: true,
    },
  },
  methods: {
    onChange() {
      console.debug("onChange", this.editor.get());
      this.$emit("propertiesUpdate", this.editor.get());
    }
  },
  mounted() {
    const container = this.$refs.propertyeditor;
    const options = {
      mode: 'tree',
      onChange: this.onChange,
      mainMenuBar: false,
      navigationBar: false,
    };

    this.editor = new JSONEditor(container, options);
    this.editor.set(this.properties)
  },
};
</script>

<style>
.propertyContainer {
  min-width: 300px;
  min-height: 300px;
}
</style>
