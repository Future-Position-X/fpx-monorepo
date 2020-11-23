const BASE_URL = process.env.VUE_APP_BASE_URL;

export default {
  async validateResponse(response) {
    if (!response.ok) throw new Error((await response.json()).message);
  },
  async create(email, password) {
    const response = await fetch(`${BASE_URL}/users`, {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': `application/json`,
        Accept: `application/json`,
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    await this.validateResponse(response);
    return response.json();
  },
};
