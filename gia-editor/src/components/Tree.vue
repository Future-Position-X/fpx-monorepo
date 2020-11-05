<template>
  <div>
    <v-btn @click="click">Yolo</v-btn>
    <CollectionTreeView
        ref="treeview"
        return-object
        @input="onSelectionUpdate"
        @update:active="onActiveUpdate"
        :active="active"
        :items="items"
        selectable
        activatable
        :open.sync="open"
    >
      <template v-slot:append="{ item }">
        <v-icon :color="item.color">mdi-brightness-1</v-icon>
      </template>
    </CollectionTreeView>

  </div>
</template>

<script>
/* eslint-disable no-console, no-prototype-builtins */
import CollectionTreeView from "./CollectionTreeView.vue";
import session from '../services/session';

export default {
  components: {CollectionTreeView},
  props: ['sortedCollections'],
  methods: {
    click() {
    },
    onActiveUpdate(activeCollections) {
      console.log("onActiveUpdate", activeCollections);
      if (activeCollections.length >= 1) {
        const collection = activeCollections[0];
        this.$emit('activeUpdate', collection.uuid)
      } else {
        this.$emit('activeUpdate', null)
      }
    },
    onSelectionUpdate(selectedItems) {
      console.log("onSelectionUpdate", selectedItems);
      const selectedUuids = selectedItems.filter((x) => !!x.uuid).map((x) => x.uuid);
      this.$emit('selectionUpdate', selectedUuids);
    },
    addCollection(collection) {
      const colorNum = this.items.length;
      const colors = this.items.length + 1;
      const saturation = 100;
      const color = `hsl(${(colorNum * (360 / colors)) % 360},${saturation}%,50%)`;

      const newCollection = {...collection, color, editable: true, id: collection.uuid};

      const item = {
        id: newCollection.name,
        name: newCollection.name,
        color: '#FFF',
        provider_uuid: newCollection.provider_uuid,
        editable: false,
        children: [newCollection],
      };

      this.items[0].children.push(item);
    },
    removeCollection(collection) {
      this.items.splice(this.items.indexOf(collection), 1);
    },
  },
  watch: {
    async sortedCollections() {
      this.items = [];
      const collections = [];

      // eslint-disable-next-line no-restricted-syntax
      for (const [key, value] of Object.entries(this.sortedCollections)) {
        collections.push({
          id: key,
          name: key,
          color: '#FFF',
          provider_uuid: value[0].provider_uuid,
          editable: false,
          activatable: false,
          selectable: false,
          children: value.map((e) => {
            e.id = e.uuid;
            e.editable = true;
            e.activatable = true;
            e.selectable = true;
            // e.name = e.provider_uuid;
            return e;
          }),
        });
      }
      let providerUuid = null;
      if (session.authenticated()) {
        providerUuid = session.user.provider_uuid;
      }
      this.items.push({
        id: 'Owned collections',
        name: 'Owned collections',
        color: '#FFF',
        editable: false,
        activatable: false,
        selectable: false,
        children: collections.filter((coll) => coll.provider_uuid === providerUuid),
      });
      this.items.push({
        id: 'Other collections',
        name: 'Other collections',
        color: '#FFF',
        editable: false,
        activatable: false,
        selectable: false,
        children: collections.filter((coll) => coll.provider_uuid !== providerUuid),
      });
      this.open = ['Owned collections'];
    },
    /*
    active: {
      handler(val) {
        // eslint-disable-next-line no-console
        console.log("args3", val, this.active)
      }
    }

     */
  },
  data: () => ({
    selectedUuids: [],
    items: [],
    open: [],
    active: [],
  }),
};
</script>
