<template>
  <!--<codemirror v-model="code" :options="cmOptions" />-->
  <div class="codeWrapper">
    <codemirror
      ref="cmEditor"
      :value="code"
      :options="cmOptions"
      @ready="onCmReady"
      @focus="onCmFocus"
      @input="onCmCodeChange"
    />
  </div>
</template>

<script>
import gjv from "geojson-validation";
import { codemirror } from "vue-codemirror";

// import base style
import "codemirror/lib/codemirror.css";

// import language js
import "codemirror/mode/javascript/javascript.js";
import "codemirror/addon/fold/foldgutter.js";
import "codemirror/addon/fold/foldcode.js";
import "codemirror/addon/fold/brace-fold.js";
import "codemirror/addon/fold/foldgutter.css";

export default {
  name: "Code",
  components: {
    codemirror
  },
  props: ["code"],
  data() {
    return {
      //code: 'const a = 10',
      cmOptions: {
        tabSize: 4,
        mode: "text/javascript",
        theme: "default",
        matchBrackets: true,
        lineNumbers: true,
        line: true,
        foldGutter: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]
      }
    };
  },
  methods: {
    onCmReady(cm) {
      console.log("the editor is readied!", cm);
    },
    onCmFocus(cm) {
      console.log("the editor is focused!", cm);
    },
    onCmCodeChange(newCode, changeObj) {
      console.log(changeObj);
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
    }
  },
  computed: {
    codemirror() {
      return this.$refs.cmEditor.codemirror;
    }
  },
  mounted() {
    console.log("the current CodeMirror instance object:", this.codemirror);
    // you can use this.codemirror to do something...
  }
};
</script>

<style>
/*
.codeWrapper {
  position: absolute;
  top: 40px;
  bottom: 0;
  width: 100%;
  overflow: auto;
}
*/
.CodeMirror {
  height: 100%;
  min-height: 100%;
  font-size: 14px;
}
</style>