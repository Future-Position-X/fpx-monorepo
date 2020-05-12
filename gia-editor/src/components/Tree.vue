<template>
  <v-treeview @input="selectionUpdate" selectable :items="items">
        <template v-slot:append="{ item }">
          <!--
          <v-icon
            v-if="item.children"
            v-text="`mdi-${item.id === 1 ? 'home-variant' : 'folder-network'}`"
            v-color=
          ></v-icon>-->
          <div :style="{'background-color': item.color}">YOLO</div>
        </template>
  </v-treeview>
</template>

<script>
const groupBy = function(xs, key) {
  return xs.reduce(function(rv, x) {
    (rv[x[key]] = rv[x[key]] || []).push(x);
    return rv;
  }, {});
};
const selectColor = function(colorNum, colors) {
    if (colors < 1) colors = 1; // defaults to one color - avoid divide by zero
    const saturation = 60 + colorNum % 5 * 10;
    return "hsl(" + (colorNum * (360 / colors) % 360) + "," + saturation + "%,50%)";
}

export default {
  props: ["collections"],
  methods: {
    selectionUpdate(selectedIds) {
      this.$emit("selectionUpdate", selectedIds);
    }
  },
  watch: {
    collections: function() {
      const items = [];
      let sortedCollections = groupBy(this.collections, "name");
      let i = 1;
      const len = Object.keys(sortedCollections).length
      console.log(len)
      for (let [key, value] of Object.entries(sortedCollections)) {
        let color = selectColor(i, len);
        items.push({
          id: key,
          name: key,
          color: color,
          children: value.map(function(e) {
            e.id = e.uuid;
            e.name = e.provider_uuid;
            e.color = color;
            return e;
          })
        });
        i++;
      }
      this.items = items;
    }
  },
  data: () => ({
    items: []
  })
};
</script>