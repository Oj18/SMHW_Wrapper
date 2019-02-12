# using requests for HTTP and json for, um... JSON
import requests
import json
import asyncio

debug = True  # DO NOT USE unless you know what you're doing! This overrides errors!


# a quick note - random tests led me to discover a school with subdomain "lololol", id 251616 - use for testing

# let's start with custom exceptions

class NotStoredError(Exception):
    pass


class CredentialError(Exception):
    pass


class NoAuthAPI:
    def public_api_request(location):
        return requests.get("https://api.showmyhomework.co.uk/api/public/" + location,
                            headers={"Accept": "application/smhw.v3+json"}).text  # HTTPS request to the server

    def regular_api_request(location):
        return requests.get("https://api.showmyhomework.co.uk/api/" + location,
                            headers={"Accept": "application/smhw.v3+json"}).text  # HTTPS request to the server

# main class - all operations are called from in here
class School:
    def __init__(self, sub, autodownload=False, count=0):
        self.subdomain = sub
        self.id = self.get_school_id(sub, count)

        self.links = self.make_links();
        self.count = count
        self.employess = self.get_employees()

    def make_links():
        return {
            'students': 'students?school_id=' + str(self.id),
            'parents': 'parents?school_id=' + str(self.id),
            'employees': 'employees?school_id=' + str(self.id),
            'class_years': 'class_years?school_id=' + str(self.id),
            'subjects': 'subjects?school_id=' + str(self.id),
            'house_groups': 'house_groups?school_id=' + str(self.id),
            'class_groups': 'class_groups?school_id=' + str(self.id),
            'kudos_reasons': 'kudos_reasons?school_id=' + str(self.id)
        }
    
    def get_school_id(self, subdomain, count=0):
        try:
            data = json.loads(NoAuthAPI.public_api_request("school_search?subdomain=" + subdomain))["schools"][count]["id"]
            return data
        except IndexError:
            return 0

    def get_employees(self):
        return json.loads(NoAuthAPI.regular_api_request(self.links["employees"]))["employees"]

    def find_employee(self, **kwargs):
        # todo
        return 'todo'


class User:
    def __init__(self, school: School, username, password):
        self.school = school
        self.username = username
        self.password = password
        self.loop = asyncio.get_event_loop()

        payload = {"client_id": "55283c8c45d97ffd88eb9f87e13f390675c75d22b4f2085f43b0d7355c1f",
                    "client_secret": "c8f7d8fcd0746adc50278bc89ed6f004402acbbf4335d3cb12d6ac6497d3"}

        data = {"username": self.username, "password": self.password,
                "grant_type": "password", "school_id": self.school.id}
        temp = requests.post("https://api.showmyhomework.co.uk/oauth/token", params=payload, data=data,
                            headers={"Accept": "application/smhw.v3+json"})
        try:
            self.token = temp.headers["smhw_token"]
            self.token_expires = temp.headers["expires_in"]
            self.refresh_token = temp.headers["refresh_token"]
        except KeyError:
            global debug
            if not debug:
                raise CredentialError
            else:
                print("Credentials invalid, please inject!")

        self.loop.run_until_complete(self.wait_for_oauth_token_refresh())

    def user_api_request(self, location, auth=True):
        if auth:
            headers = {"Accept": "application/smhw.v3+json", "Authorization": "Bearer " + self.token}
        else:
            headers = {"Accept": "application/smhw.v3+json"}
        return requests.get("https://api.showmyhomework.co.uk/api/" + location, headers=headers).text  # HTTPS request

    def refresh_oauth_token(self):
        payload = {"client_id": "55283c8c45d97ffd88eb9f87e13f390675c75d22b4f2085f43b0d7355c1f",
                    "client_secret": "c8f7d8fcd0746adc50278bc89ed6f004402acbbf4335d3cb12d6ac6497d3"}

        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token, "school_id": self.school.id}
        temp = requests.post("https://api.showmyhomework.co.uk/oauth/token", params=payload, data=data,
                            headers={"Accept": "application/smhw.v3+json"})
        self.loop.run_until_complete(self.wait_for_oauth_token_refresh())

    async def wait_for_oauth_token_refresh(self):
        await asyncio.sleep(self.token_expires)
        self.refresh_token()