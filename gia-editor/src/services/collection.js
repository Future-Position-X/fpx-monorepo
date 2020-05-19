const GIA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIwNDQ1Y2Y5YS0zMTc4LTQ5YmQtODM5Mi1kNjA4ZWNkZGVmMWMiLCJuYmYiOjE1ODU2NDIyNDYsImV4cCI6MTkwMTE3NTA0NiwiaWF0IjoxNTg1NjQyMjQ2LCJpc3MiOiJnYXZsZWlubm92YXRpb25hcmVuYS5zZSIsImF1ZCI6Imh0dHBzOi8vYXBpLmdhdmxlaW5ub3ZhdGlvbmFyZW5hLnNlIn0.cFgPLVx11LSpb06qOo4GZojQYZG-lOEWHi6fDVbV9SI";

export default {
    async fetchCollections() {
        const response = await fetch("https://dev.gia.fpx.se/collections", {
            headers: {
                Authorization:
                    `Bearer ${GIA_TOKEN}`
            }
        });

        const data = await response.json();
        return data;
    },
    async fetchById(signal, collectionId, bounds, simplify) {
        const response = await fetch(
            `https://dev.gia.fpx.se/collections/${collectionId}/items/geojson?limit=100000&spatial_filter=intersect&spatial_filter.envelope.xmin=${bounds.minX}&spatial_filter.envelope.ymin=${bounds.minY}&spatial_filter.envelope.xmax=${bounds.maxX}&spatial_filter.envelope.ymax=${bounds.maxY}&simplify=${simplify}`,
            {
                headers: {
                    Authorization:
                        `Bearer ${GIA_TOKEN}`
                },
                signal: signal
            }
        );

        const data = await response.json();
        return data;
    },
    async addItems(collectionId, items) {
        await fetch(
            `https://dev.gia.fpx.se/collections/${collectionId}/items/geojson`,
            {
                method: "PUT",
                mode: "cors",
                headers: {
                    "Content-Type": "application/json",
                    Authorization:
                        `Bearer ${GIA_TOKEN}`
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
            await fetch(`https://dev.gia.fpx.se/items/${item.id}`, {
                method: "DELETE",
                mode: "cors",
                headers: {
                    "Content-Type": "application/json",
                    Authorization:
                        `Bearer ${GIA_TOKEN}`
                }
            });
        }
    },
    async updateItems(items) {
        await fetch(`https://dev.gia.fpx.se/items/geojson`, {
            method: "PUT",
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
                Authorization:
                    `Bearer ${GIA_TOKEN}`
            },
            body: JSON.stringify({
                type: "FeatureCollection",
                features: items
            })
        });
    },
    async create(collectionName, isPublic) {
        await fetch(`https://dev.gia.fpx.se/collections`, {
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
                Authorization:
                    `Bearer ${GIA_TOKEN}`
            },
            body: JSON.stringify({
                name: collectionName,
                is_public: isPublic
            })
        });
    }
};