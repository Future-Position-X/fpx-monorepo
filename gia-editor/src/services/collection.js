const GIA_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZWI4YWE5Ni05NTkzLTQwZTMtYTEzYS02ZGVmZThhYWRkNzciLCJleHAiOjE1OTM1MTE5OTUsInByb3ZpZGVyX3V1aWQiOiJkN2EyNTI4MS0yOTVjLTQ3YzktODZjMi1mMjFjNTFhZGIxM2IifQ.SStYGpLPWEPN1rP3tWeWCPl7IAyBIBAnj47QVkNp5ls";

const BASE_URL = process.env.VUE_APP_BASE_URL;

export default {
    async fetchCollections() {
        const response = await fetch(`${BASE_URL}/collections`, {
            headers: {
                Authorization: `Bearer ${GIA_TOKEN}`,
                Accept: `application/geojson`
            }
        });

        const data = await response.json();
        return data;
    },
    async fetchCollection(collectionId) {
        const response = await fetch(`${BASE_URL}/collections/${collectionId}`, {
            headers: {
                Authorization: `Bearer ${GIA_TOKEN}`,
                Accept: `application/geojson`
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
                    Authorization: `Bearer ${GIA_TOKEN}`,
                    Accept: `application/geojson`
                },
                signal: signal
            }
        );

        const data = await response.json();
        return data;
    },
    async addItems(collectionId, items) {
        await fetch(
            `${BASE_URL}/collections/${collectionId}/items`,
            {
                method: "PUT",
                mode: "cors",
                headers: {
                    Authorization: `Bearer ${GIA_TOKEN}`,
                    'Content-Type': `application/geojson`,
                    Accept: `application/geojson`
                },
                body: JSON.stringify({
                    type: "FeatureCollection",
                    features: items
                })
            }
        );
    },
    async removeItems(items) {
        for (const item of items) {
            await fetch(`${BASE_URL}/items/${item.id}`, {
                method: "DELETE",
                mode: "cors",
                headers: {
                    Authorization: `Bearer ${GIA_TOKEN}`
                }
            });
        }
    },
    async updateItems(items) {
        await fetch(`${BASE_URL}/items`, {
            method: "PUT",
            mode: "cors",
            headers: {
                Authorization: `Bearer ${GIA_TOKEN}`,
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
                Authorization: `Bearer ${GIA_TOKEN}`,
                'Content-Type': `application/geojson`
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
                Authorization: `Bearer ${GIA_TOKEN}`
            }
        });
    }
};