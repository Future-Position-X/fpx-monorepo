<template>
  <v-treeview @input="selectionUpdate" :items="items" :open.sync="open">
    <template v-slot:append="{ item }">
      <v-icon :color="item.color">mdi-brightness-1</v-icon>
    </template>
  </v-treeview>
</template>

<script>
import session from "../services/session";
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
    sortedCollections: async function() {
      this.items = [];
      const collections = [];
      
      for (let [key, value] of Object.entries(this.sortedCollections)) {
        console.log(key, value)
        collections.push({
          id: key,
          name: key,
          color: value[0].color,
          provider_uuid: value[0].provider_uuid,
          children: value.map(function(e) {
            e.id = e.uuid;
            //e.name = e.provider_uuid;
            return e;
          })
        });
      }
      let provider_uuid = null
      if (session.authenticated()) {
        provider_uuid = session.user.provider_uuid;
      }
      this.items.push({
          id: "Owned collections",
          name: "Owned collections",
          color: "#000",
          children: collections.filter((coll) => coll.provider_uuid == provider_uuid),
          selectable: false
        })
      this.items.push({
          id: "Other collections",
          name: "Other collections",
          color: "#000",
          children: collections.filter((coll) => coll.provider_uuid != provider_uuid),
          selectable: true
        })
        console.log(this.items);
        this.open = ["Owned collections"];
    }
  },
  data: () => ({
    items: [],
    open: []
  })
};
</script>