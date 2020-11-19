const BASE_URL = process.env.VUE_APP_BASE_URL;

export default {
  async validateResponse(response) {
    if (!response.ok) throw new Error(await response.text());
  },
  async get(uuid) {
    const response = await fetch(`${BASE_URL}/providers/${uuid}`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        Accept: `application/json`,
      }
    });

    await this.validateResponse(response);
    return response.json();
  },
};
