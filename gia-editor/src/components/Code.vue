<template>
  <div class="editorContainer" ref="jsoneditor"></div>
</template>

<script>
import gjv from "geojson-validation";
import JSONEditor from 'jsoneditor/dist/jsoneditor';
import 'jsoneditor/dist/jsoneditor.min.css';

export default {
  name: 'Code',
  props: ['code'],
  data() {
    return {
      editor: null,
    };
  },
  watch: {
    code: {
      handler(val) {
        console.debug('editor.set');
        this.editor.set(val);
      },
      deep: true,
    },
  },
  methods: {
    onChangeText(jsonString) {
      console.debug("onChange", jsonString);
      try {
        const geojsonParsed = JSON.parse(jsonString);
        if (gjv.valid(geojsonParsed)) {
          console.debug("geojson is valid!");
          this.$emit("geojsonUpdate", geojsonParsed);
        } else {
          console.debug("geojson is NOT valid!");
        }
      } catch (e) {
        console.debug(e.name);
      }
    },
  },
  mounted() {
    const container = this.$refs.jsoneditor;
    const options = {
      mode: 'code',
      onChangeText: this.onChangeText,
    };

    this.editor = new JSONEditor(container, options);
  },
};
</script>

<style>
.editorContainer {
}
</style>
