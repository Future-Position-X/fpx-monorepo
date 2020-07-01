const BASE_URL = process.env.VUE_APP_BASE_URL;

export default {
    sessionToken: null,

    async fetchCollections() {
        const response = await fetch(`${BASE_URL}/collections`, {
            headers: {
                Authorization: `Bearer ${this.sessionToken}`,
                Accept: `application/json`
            }
        });

        const data = await response.json();
        return data;
    },
    async fetchCollection(collectionId) {
        const response = await fetch(`${BASE_URL}/collections/${collectionId}`, {
            headers: {
                Authorization: `Bearer ${this.sessionToken}`,
                Accept: `application/json`
            }
        });

        const data = await response.json();
        return data;
    },
    async fetchItems(signal, collectionId, bounds, simplify) {
        const response = await fetch(
            `${BASE_URL}/collections/${collectionId}/items?limit=100000&spatial_filter=intersect&spatial_filter.envelope.xmin=${bounds.minX}&spatial_filter.envelope.ymin=${bounds.minY}&spatial_filter.envelope.xmax=${bounds.maxX}&spatial_filter.envelope.ymax=${bounds.maxY}&simplify=${simplify}`,
            {
                headers: {
                    Authorization: `Bearer ${this.sessionToken}`,
                    Accept: `application/geojson`
                },
                signal: signal
            }
        );

        const data = await response.json();
        return data;
    },
    async authenticated() {
        if (this.sessionToken == null)
            return false;

        return true;
    },
    async addItems(collectionId, items) {
        if (! (await this.authenticated())) {
            console.log("not allowed");
            return false;
        }

        await fetch(
            `${BASE_URL}/collections/${collectionId}/items`,
            {
                method: "PUT",
                mode: "cors",
                headers: {
                    Authorization: `Bearer ${this.sessionToken}`,
                    'Content-Type': `application/geojson`,
                    Accept: `application/geojson`
                },
                body: JSON.stringify({
                    type: "FeatureCollection",
                    features: items
                })
            }
        );

        return true;
    },
    async removeItems(items) {
        for (const item of items) {
            await fetch(`${BASE_URL}/items/${item.id}`, {
                method: "DELETE",
                mode: "cors",
                headers: {
                    Authorization: `Bearer ${this.sessionToken}`
                }
            });
        }
    },
    async updateItems(items) {
        await fetch(`${BASE_URL}/items`, {
            method: "PUT",
            mode: "cors",
            headers: {
                Authorization: `Bearer ${this.sessionToken}`,
                'Content-Type': `application/geojson`
            },
            body: JSON.stringify({
                type: "FeatureCollection",
                features: items
            })
        });
    },
    async create(collectionName, isPublic) {
        return await fetch(`${BASE_URL}/collections`, {
            method: "POST",
            mode: "cors",
            headers: {
                Authorization: `Bearer ${this.sessionToken}`,
                'Content-Type': `application/json`
            },
            body: JSON.stringify({
                name: collectionName,
                is_public: isPublic
            })
        });
    },
    async remove(collectionId) {
        await fetch(`${BASE_URL}/collections/${collectionId}`, {
            method: "DELETE",
            mode: "cors",
            headers: {
                Authorization: `Bearer ${this.sessionToken}`
            }
        });
    }
};