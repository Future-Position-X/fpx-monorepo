const BASE_URL = process.env.VUE_APP_BASE_URL;
const EMAIL = process.env.VUE_APP_EMAIL;
const PASSWORD = process.env.VUE_APP_PASSWORD;

export default {
    token: null,
    async validateResponse(response) {
        if (!response.ok)
            throw new Error(await response.text())
    },
    async create() {
        const response = await fetch(`${BASE_URL}/sessions`, {
            method: "POST",
            mode: "cors",
            headers: {
                'Content-Type': `application/json`,
                Accept: `application/json`
            },
            body: JSON.stringify({
                email: EMAIL,
                password: PASSWORD
            })
        });

        await this.validateResponse(response);

        this.token = (await response.json())["token"]
    },
    authenticated() {
        return !!this.token;
    }
};