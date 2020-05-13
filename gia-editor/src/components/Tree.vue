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

export default {
  props: ["sortedCollections"],
  methods: {
    selectionUpdate(selectedIds) {
      this.$emit("selectionUpdate", selectedIds);
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
            e.name = e.provider_uuid;
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