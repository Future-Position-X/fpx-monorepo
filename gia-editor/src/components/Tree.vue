<template>
  <v-treeview @input="selectionUpdate" selectable :items="items"></v-treeview>
</template>

<script>
const groupBy = function(xs, key) {
  return xs.reduce(function(rv, x) {
    (rv[x[key]] = rv[x[key]] || []).push(x);
    return rv;
  }, {});
};

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
      for (let [key, value] of Object.entries(sortedCollections)) {
        items.push({
          id: key,
          name: key,
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