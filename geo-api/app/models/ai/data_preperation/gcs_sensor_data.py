import pandas as pd
import requests
import json
import concurrent.futures


class SensorData:
    request_url = "https://api.passcheck.com/MaxiAPI3/api"
    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "cache-control": "no-cache",
    }
    user_id = "iU225693"
    pwd = "iPw23OP43a"

    sensors_in_use = [6, 16, 21, 26, 31, 36, 56, 126, 130, 134, 191, 241]

    @classmethod
    def __get_token(self):
        r = requests.get(
            self.request_url + "/Login/" + self.user_id + "?pw=" + self.pwd,
            headers=self.request_headers,
        )
        return json.loads(r.text)

    @classmethod
    def __get_sensors_index(self, token):
        r = requests.get(
            self.request_url + "/ListCounter/" + self.user_id + "?token=" + token,
            headers=self.request_headers,
        )
        return json.loads(r.text)

    @classmethod
    def __get_sensor_data(self, token, cid, start_date, end_date):
        (token, cid, start_date, end_date)
        payload = {
            "token": token,
            "sDate": start_date,
            "eDate": end_date,
            "cID": str(cid),
        }
        r = requests.get(
            self.request_url + "/CountData/" + self.user_id + "",
            params=payload,
            headers=self.request_headers,
        )
        return json.loads(r.text)

    @classmethod
    def get_data(self, start_date, end_date):
        token = self.__get_token()
        sensor_ids = []
        df_main = pd.date_range(start_date, end_date, freq="H", name="cDte").to_frame()
        df_main.drop(columns=["cDte"], axis=1, inplace=True)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for sensor_data in executor.map(
                lambda s: self.__get_sensor_data(token, s, start_date, end_date),
                self.sensors_in_use,
            ):
                df = pd.DataFrame(sensor_data)
                cid = sensor_data[0]["Cid"]
                sensor_ids.append(cid)
                df.index = pd.to_datetime(df["cDte"])
                df.drop(columns=["cDte"], axis=1, inplace=True)
                df["s" + cid + "_in"] = df["cIn"].astype(float)
                df["s" + cid + "_out"] = df["cOut"].astype(float)
                df_main = pd.merge(
                    df_main,
                    df[["s" + cid + "_in", "s" + cid + "_out"]],
                    left_on="cDte",
                    right_on="cDte",
                    how="left",
                )
            return df_main, sensor_ids
