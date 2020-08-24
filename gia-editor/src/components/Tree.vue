<template>
  <v-treeview return-object @input="selectionUpdate" @update:active="onActiveUpdate" :items="items" selectable activatable :open.sync="open">
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
    onActiveUpdate(activeCollections) {
      const collection = activeCollections[0];

      if (collection.editable) {
        this.$emit("updateCodeView", collection);
      }
    },
    selectionUpdate(selectedItems) {
      const selectedUuids = selectedItems.filter(x => !!x.uuid).map(x => x.uuid);
      this.$emit("selectionUpdate", selectedUuids);
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

      collection.color = color;
      collection.editable = true;
      collection.id = collection.uuid;

      const item = {
        id: collection.name,
        name: collection.name,
        color: "#FFF",
        provider_uuid: collection.provider_uuid,
        editable: false,
        children: [collection]
      };

      this.items[0].children.push(item);
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
        collections.push({
          id: key,
          name: key,
          color: "#FFF",
          provider_uuid: value[0].provider_uuid,
          editable: false,
          children: value.map(function(e) {
            e.id = e.uuid;
            e.editable = true
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
          color: "#FFF",
          editable: false,
          children: collections.filter((coll) => coll.provider_uuid == provider_uuid),
        })
      this.items.push({
          id: "Other collections",
          name: "Other collections",
          color: "#FFF",
          editable: false,
          children: collections.filter((coll) => coll.provider_uuid != provider_uuid),
        })
        this.open = ["Owned collections"];
    }
  },
  data: () => ({
    items: [],
    open: []
  })
};
</script>