import collection from "./collection"

export default {
    createContext() {
        return {
            addedItems: [],
            removedItems: [],
            modifiedItems: []
        };
    },
    onItemRemoved(ctx, item) {
        let i;

        for (i = ctx.addedItems.length - 1; i >= 0; i--) {
            if (ctx.addedItems[i] == item) {
                ctx.addedItems.splice(i, 1);
            }
        }

        for (i = ctx.modifiedItems.length - 1; i >= 0; i--) {
            if (ctx.modifiedItems[i].id == item.id) {
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
    async commit(ctx, collectionId) {
        if (ctx.addedItems.length > 0) {
            await collection.addItems(
                collectionId,
                ctx.addedItems
            );
            ctx.addedItems = [];
        }

        if (ctx.removedItems.length > 0) {
            await collection.removeItems(ctx.removedItems);
            ctx.removedItems = [];
        }

        if (ctx.modifiedItems.length > 0) {
            await collection.updateItems(ctx.modifiedItems);
            ctx.modifiedItems = [];
        }
    }
};