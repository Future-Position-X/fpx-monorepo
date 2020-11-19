<template>
  <CollectionTreeView
      ref="treeview"
      return-object
      @input="onSelectionUpdate"
      @update:active="onActiveUpdate"
      :items="items"
      selectable
      activatable
      :open.sync="open"
  >
    <template v-slot:append="{ item }">
      <v-icon :color="item.color">mdi-brightness-1</v-icon>
    </template>
  </CollectionTreeView>
</template>

<script>
import CollectionTreeView from "./CollectionTreeView.vue";
import session from '../services/session';
import providerService from '../services/provider';

export default {
  components: {CollectionTreeView},
  props: ['sortedCollections'],
  methods: {
    click() {
    },
    onActiveUpdate(activeCollections) {
      console.debug("onActiveUpdate", activeCollections);
      if (activeCollections.length >= 1) {
        const collection = activeCollections[0];
        this.$emit('activeUpdate', collection.uuid)
      } else {
        this.$emit('activeUpdate', null)
      }
    },
    onSelectionUpdate(selectedItems) {
      console.debug("onSelectionUpdate", selectedItems);
      const selectedUuids = selectedItems.filter((x) => !!x.uuid).map((x) => x.uuid);
      console.debug("selectedUuids: ", selectedUuids);
      this.$emit('selectionUpdate', selectedUuids);
    },
    addCollection(collection) {
      const newCollection = {...collection, editable: true, activatable: true, selectable: true, id: collection.uuid};

      console.debug("newCollection: ", newCollection);
      const item = {
        id: newCollection.uuid,
        uuid: newCollection.uuid,
        name: newCollection.name,
        color: newCollection.color,
        provider_uuid: newCollection.provider_uuid,
        editable: true,
        activatable: true,
        selectable: true
      };

      this.items[0].children.push(item);
    },
    removeCollection(collection) {
      this.items.splice(this.items.indexOf(collection), 1);
    },
    async cacheProvider(uuid) {
      let provider = this.providerCache[uuid];

      if (provider == null) {
        provider = await providerService.get(uuid);
        this.providerCache[uuid] = provider;
      }
    }
  },
  watch: {
    async sortedCollections() {
      this.items = [];
      const collections = [];

      const promises = Object.values(this.sortedCollections)
        .reduce((acc, coll) => acc.concat(coll))
        .map(c => this.cacheProvider(c.provider_uuid));

      await Promise.all(promises);

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
            const suffix = ` (${this.providerCache[e.provider_uuid].name})`
            if (!e.name.endsWith(suffix)) {
              e.name += suffix;
            }
            // e.name = e.provider_uuid;
            return e;
          }),
        });
      }
      let providerUuid = null;
      if (session.authenticated()) {
        providerUuid = session.user.provider_uuid;
      }

      const our = Object.values(this.sortedCollections)
        .reduce((acc, coll) => acc.concat(coll))
        .filter(coll => coll.provider_uuid === providerUuid);

      this.items.push({
        id: 'Owned collections',
        name: 'Owned collections',
        color: '#FFF',
        editable: false,
        activatable: false,
        selectable: false,
        children: our.map(coll => ({
          id: coll.uuid,
          uuid: coll.uuid,
          name: coll.name,
          color: coll.color,
          provider_uuid: providerUuid,
          editable: true,
          activatable: true,
          selectable: true
        }))
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
  },
  data: () => ({
    items: [],
    open: [],
    providerCache: {}
  }),
};
</script>
