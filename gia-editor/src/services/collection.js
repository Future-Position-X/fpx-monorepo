const BASE_URL = process.env.VUE_APP_BASE_URL;

import session from "../services/session";

export default {
    async validateResponse(response) {
        if (!response.ok)
            throw new Error(await response.text())
    },
    async fetchCollections() {
        const headers = {
            Accept: `application/json`
        }

        if (session.authenticated())
            headers.Authorization = `Bearer ${session.token}`;

        const response = await fetch(`${BASE_URL}/collections`, {
            headers: headers
        });
        
        await this.validateResponse(response);

        const data = await response.json();
        return data;
    },
    async fetchCollection(collectionId) {
        const response = await fetch(`${BASE_URL}/collections/${collectionId}`, {
            headers: {
                Authorization: `Bearer ${session.token}`,
                Accept: `application/json`
            }
        });

        await this.validateResponse(response);

        const data = await response.json();
        return data;
    },
    async fetchItems(signal, collectionId, bounds, simplify) {
        const headers = {
            Accept: `application/geojson`
        }

        if (session.authenticated())
            headers.Authorization = `Bearer ${session.token}`;

        const response = await fetch(
            `${BASE_URL}/collections/${collectionId}/items?limit=100000&spatial_filter=intersect&spatial_filter.envelope.xmin=${bounds.minX}&spatial_filter.envelope.ymin=${bounds.minY}&spatial_filter.envelope.xmax=${bounds.maxX}&spatial_filter.envelope.ymax=${bounds.maxY}&simplify=${simplify}`,
            {
                headers: headers,
                signal: signal
            }
        );

        await this.validateResponse(response);

        const data = await response.json();
        return data;
    },
    async addItems(collectionId, items) {
        const response = await fetch(
            `${BASE_URL}/collections/${collectionId}/items`,
            {
                method: "PUT",
                mode: "cors",
                headers: {
                    Authorization: `Bearer ${session.token}`,
                    'Content-Type': `application/geojson`,
                    Accept: `application/geojson`
                },
                body: JSON.stringify({
                    type: "FeatureCollection",
                    features: items
                })
            }
        )
        
        await this.validateResponse(response);
    },
    async removeItems(items) {
        for (const item of items) {
            const response = await fetch(`${BASE_URL}/items/${item.id}`, {
                method: "DELETE",
                mode: "cors",
                headers: {
                    Authorization: `Bearer ${session.token}`
                }
            });

            await this.validateResponse(response);
        }
    },
    async updateItems(items) {
        const response = await fetch(`${BASE_URL}/items`, {
            method: "PUT",
            mode: "cors",
            headers: {
                Authorization: `Bearer ${session.token}`,
                'Content-Type': `application/geojson`,
                Accept: 'application/geojson'
            },
            body: JSON.stringify({
                type: "FeatureCollection",
                features: items
            })
        });

        await this.validateResponse(response);
    },
    async create(collectionName, isPublic) {
        const response = await fetch(`${BASE_URL}/collections`, {
            method: "POST",
            mode: "cors",
            headers: {
                Authorization: `Bearer ${session.token}`,
                'Content-Type': `application/json`
            },
            body: JSON.stringify({
                name: collectionName,
                is_public: isPublic
            })
        });

        await this.validateResponse(response);

        const collection = await response.json();
        return collection;
    },
    async remove(collectionId) {
        const response = await fetch(`${BASE_URL}/collections/${collectionId}`, {
            method: "DELETE",
            mode: "cors",
            headers: {
                Authorization: `Bearer ${session.token}`
            }
        });

        await this.validateResponse(response);
    }
};