import isEqual from 'lodash.isequal';
import collection from './collection';

export default {
  createContext() {
    return {
      addedItems: [],
      removedItems: [],
      modifiedItems: [],
    };
  },
  onItemRemoved(ctx, item) {
    let i;

    for (i = ctx.addedItems.length - 1; i >= 0; i -= 1) {
      if (ctx.addedItems[i] === item) {
        ctx.addedItems.splice(i, 1);
      }
    }

    for (i = ctx.modifiedItems.length - 1; i >= 0; i -= 1) {
      if (ctx.modifiedItems[i].id === item.id) {
        ctx.modifiedItems.splice(i, 1);
      }
    }

    ctx.removedItems.push(item);
  },
  onItemAdded(ctx, item) {
    ctx.addedItems.push(item);
  },
  onItemModified(ctx, item) {
    ctx.modifiedItems.push(item);
  },
  async commit2(ctx, collectionId) {
    console.debug("commit");
    if (ctx.addedItems.length > 0) {
      const success = await collection.addItems(collectionId, ctx.addedItems);

      if (success) {
        ctx.addedItems = [];
      } else {
        return false;
      }
    }

    if (ctx.removedItems.length > 0) {
      await collection.removeItems(ctx.removedItems);
      ctx.removedItems = [];
    }

    if (ctx.modifiedItems.length > 0) {
      await collection.updateItems(ctx.modifiedItems);
      ctx.modifiedItems = [];
    }

    return true;
  },
  async commit(orgGeojson, geojson, collectionId) {
    const promises = [];
    const geojsonIds = geojson.features.map((f) => f.id);
    const orgGeojsonIds = orgGeojson.features.map((f) => f.id);
    console.debug("ids", orgGeojsonIds, geojsonIds);
    const itemsToDelete = orgGeojson.features.filter((f) => !geojsonIds.includes(f.id))
    console.debug("itemsToDelete", itemsToDelete);
    if(itemsToDelete.length > 0) promises.push(collection.removeItems(itemsToDelete));

    // eslint-disable-next-line no-param-reassign
    const itemsToCreate = geojson.features.filter((f) => (f.id === undefined || (f.id.startsWith('tmp_') && delete f.id)));
    console.debug("itemsToCreate", itemsToCreate);
    if(itemsToCreate.length > 0) promises.push(collection.addItems(collectionId, itemsToCreate));

    const itemsToUpdate = geojson.features.filter((f) => {
      if(f.id === undefined) return false
      const orgFeature = orgGeojson.features.find((of) => of.id === f.id);
      return !isEqual(orgFeature, f)
    });
    console.debug("itemsToUpdate", itemsToUpdate);
    if(itemsToUpdate.length > 0) promises.push(collection.updateItems(itemsToUpdate));
    return Promise.all(promises)
  }
};
