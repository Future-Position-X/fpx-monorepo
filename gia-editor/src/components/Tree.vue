<template>
  <v-treeview
    return-object
    @input="selectionUpdate"
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
  </v-treeview>
</template>

<script>
import session from '../services/session';

export default {
  props: ['sortedCollections'],
  methods: {
    onActiveUpdate(activeCollections) {
      // eslint-disable-next-line no-console
      console.log("args", activeCollections);
      // eslint-disable-next-line no-console
      console.log("args2", this.active);
      if(activeCollections.length >= 1) {
        const collection = activeCollections[0];
        if(this.selectedUuids.includes(collection.uuid)) {
          if (collection.editable) {
            this.$emit('updateCodeView', collection);
          }
        } else {
          this.active = []
          this.$emit('updateCodeView', null);
        }
      } else {
        this.active = []
        this.$emit('updateCodeView', null);
      }
      },
      selectionUpdate(selectedItems) {
        const selectedUuids = selectedItems.filter((x) => !!x.uuid).map((x) => x.uuid);
        this.$emit('selectionUpdate', selectedUuids);
        this.selectedUuids = selectedUuids;
      },
      addCollection(collection) {
        const colorNum = this.items.length;
        const colors = this.items.length + 1;
        const saturation = 100;
        const color = `hsl(${(colorNum * (360 / colors)) % 360},${saturation}%,50%)`;

        const newCollection = { ...collection, color, editable: true, id: collection.uuid };

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
            children: value.map((e) => {
              e.id = e.uuid;
              e.editable = true;
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
          children: collections.filter((coll) => coll.provider_uuid === providerUuid),
        });
        this.items.push({
          id: 'Other collections',
          name: 'Other collections',
          color: '#FFF',
          editable: false,
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
    active:[],
  }),
};
</script>
