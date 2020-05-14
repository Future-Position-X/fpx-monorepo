<template>
  <div class="editorContainer" ref="jsoneditor"></div>
</template>

<script>
//import gjv from "geojson-validation";
import JSONEditor from "jsoneditor/dist/jsoneditor.js";
import "jsoneditor/dist/jsoneditor.min.css";

export default {
  name: "Code",
  props: ["code"],
  data() {
    return {
      editor: null
    };
  },
  watch: {
    code(val) {
      this.editor.set(val);
    }
  },
  methods: {
    /*onCmCodeChange(newCode, changeObj) {
      console.log("codeChanged: ", changeObj);
      if (changeObj.origin == "setValue") return;
      try {
        const newCodeParsed = JSON.parse(newCode);
        if (gjv.valid(newCodeParsed)) {
          console.log("newCode is valid!");
          this.$emit("geojsonUpdate", newCodeParsed);
        } else {
          console.log("newCode is NOT valid!");
        }
      } catch (e) {
        console.log(e.name);
      }
    }*/
  },
  onJsonChange() {},
  mounted() {
    const container = this.$refs.jsoneditor;
    const options = {
      mode: "code",
      onChange: this.onJsonChange
    };

    this.editor = new JSONEditor(container, options);
  }
};
</script>

<style>
.editorContainer {}
</style>