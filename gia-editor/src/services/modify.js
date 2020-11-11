import isEqual from 'lodash.isequal';
import collection from './collection';

export default {
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
