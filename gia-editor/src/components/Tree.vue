<template>
  <v-treeview @input="selectionUpdate" :items="items" :open.sync="open">
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
    },
    removeCollection(collection) {
      this.items.splice(this.items.indexOf(collection), 1);
    }
  },
  watch: {
    sortedCollections: function() {
      this.items = [];
      const collections = [];
      
      for (let [key, value] of Object.entries(this.sortedCollections)) {
        console.log(key, value)
        collections.push({
          id: key,
          name: key,
          color: value[0].color,
          is_public: value[0].is_public,
          children: value.map(function(e) {
            e.id = e.uuid;
            //e.name = e.provider_uuid;
            return e;
          })
        });
      }
      console.log("collections", collections);
      this.items.push({
          id: "Private",
          name: "Private",
          color: "#000",
          children: collections.filter((coll) => coll.is_public == "False"),
          selectable: false
        })
      this.items.push({
          id: "Public",
          name: "Public",
          color: "#000",
          children: collections.filter((coll) => coll.is_public == "True"),
          selectable: true
        })
        console.log(this.items);
        this.open = ["Public"];
    }
  },
  data: () => ({
    items: [],
    open: []
  })
};
</script>