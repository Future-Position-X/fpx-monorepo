const BASE_URL = process.env.VUE_APP_BASE_URL;
const EMAIL = process.env.VUE_APP_EMAIL;
const PASSWORD = process.env.VUE_APP_PASSWORD;

export default {
    token: null,
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

        if (response.status == 201) {
            this.token = (await response.json())["token"]
            return true;
        }
        
        return false;
    }
};