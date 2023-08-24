from env import YOUR_DATABASE_TOKEN
import os
import urllib
import requests

BASEROW_URL = "https://api.baserow.io/api/"

AUTH_HEADER = {"Authorization": "Token " + YOUR_DATABASE_TOKEN}
GET_HEADER = AUTH_HEADER
POST_PATCH_HEADER = {
    **AUTH_HEADER,
    "Content-Type": "application/json",
}


class BaserowClient:
    def __init__(self, base_url="https://api.baserow.io/api/"):
        self.base_url = base_url
        self.headers = POST_PATCH_HEADER

    def get_table_url(self, table_id, id=None):
        if id:
            return f"{self.base_url}database/rows/table/{urllib.parse.quote(table_id)}/{id}/?user_field_names=true"
        else:
            return f"{self.base_url}database/rows/table/{urllib.parse.quote(table_id)}/?user_field_names=true"

    def handle_response(self, response):
        if response.status_code == 200:
            return {
                "message": "success",
                "data": response.json(),
                "status_code": response.status_code,
            }
        elif 400 <= response.status_code < 500:
            # client error from Baserow
            return {
                "error": response.json().get("detail", "Client error."),
                "status_code": response.status_code,
            }
        else:
            # server error from Baserow
            return {
                "error": response.json().get("detail", "Server error."),
                "status_code": response.status_code,
            }

    def get_table_fields(self, table_id):
        url = f"{self.base_url}database/fields/table/{table_id}/"
        response = requests.get(url, headers=self.headers)
        return self.handle_response(response)

    def get_table_rows(self, table_id, parameters=None):
        url = self.get_table_url(table_id)
        if parameters:
            if "?" in url:
                url += "&" + "&".join(parameters)
            else:
                url += "?" + "&".join(parameters)
        response = requests.get(url, headers=self.headers)
        return self.handle_response(response)

    def get_row(self, table_id, row_id):
        url = self.get_table_url(table_id, row_id)
        response = requests.get(url, headers=self.headers)
        return self.handle_response(response)

    def get_row_id_by_attribute(self, table_id, attribute_name, attribute_value):
        parameters = [f"filter_field_{attribute_name}={attribute_value}"]
        rows = self.get_table_rows(table_id, parameters)
        print(rows)
        if "data" in rows and len(rows["data"]) > 0:
            return rows["data"]["results"][0]["id"]
        return None

    def create_row(self, table_id, data):
        try:
            url = self.get_table_url(table_id)
            response = requests.post(url, headers=self.headers, json=data)
            print("response", response.content)
            return self.handle_response(response)
        except Exception as e:
            print(e)

    def update_row(self, table_id, row_id, data):
        url = self.get_table_url(table_id, row_id)
        response = requests.patch(url, headers=self.headers, json=data)
        return self.handle_response(response)

    def delete_row(self, table_id, row_id):
        url = self.get_table_url(table_id, row_id)
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            return True
        else:
            response.raise_for_status()

    def delete_row_by_attribute(self, table_id, attribute_name, attribute_value):
        row_id = self.get_row_id_by_attribute(table_id, attribute_name, attribute_value)
        if row_id:
            return {
                "message": f"Row {row_id} from table {table_id} deleted successfully!",
                "status": self.delete_row(table_id, row_id),
            }
        else:
            return {
                "error": f"{attribute_name.capitalize()} not found.",
                "status_code": 404,
            }
