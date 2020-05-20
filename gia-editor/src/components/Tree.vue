<template>
  <v-treeview @input="selectionUpdate" selectable :items="items">
    <template v-slot:append="{ item }">
      <v-icon :color="item.color">mdi-brightness-1</v-icon>
    </template>
  </v-treeview>
</template>

<script>
export default {
  props: ["sortedCollections"],
  methods: {
    selectionUpdate(selectedIds) {
      this.$emit("selectionUpdate", selectedIds);
    },
    addCollection(collection) {
      let colorNum = this.items.length;
      let colors = this.items.length + 1;
      const saturation = 100;
      let color =
        "hsl(" +
        ((colorNum * (360 / colors)) % 360) +
        "," +
        saturation +
        "%,50%)";

      let item = {
        id: collection.name,
        name: collection.name,
        color: color,
        children: []
      };

      collection.id = collection.uuid;
      item.children.push(collection);
      this.items.push(item);
    }
  },
  watch: {
    sortedCollections: function() {
      const items = [];
      for (let [key, value] of Object.entries(this.sortedCollections)) {
        items.push({
          id: key,
          name: key,
          color: value[0].color,
          children: value.map(function(e) {
            e.id = e.uuid;
            //e.name = e.provider_uuid;
            return e;
          })
        });
      }
      this.items = items;
    }
  },
  data: () => ({
    items: []
  })
};
</script>