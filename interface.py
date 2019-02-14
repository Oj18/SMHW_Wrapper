import requests
import json
import time


class HomeworkNotFound(Exception):
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

    def get_homework(id):
        request = NoAuthAPI.regular_api_request('homeworks/' + str(id))
        
        if request == '':
            raise HomeworkNotFound("Homework Not Found")
        
        return Homework(json.loads(request)['homework'])

class Homework:
    def __init__(self, properties):
        self.properties = properties
        for key in self.properties:
            setattr(self, key, self.properties[key])


# main class - all operations are called from in here
class School:
    def __init__(self, sub, autodownload=False, count=0):
        self.subdomain = sub
        self.id = self.get_school_id(sub, count)

        self.links = {
            'students': 'students?school_id=' + str(self.id),
            'parents': 'parents?school_id=' + str(self.id),
            'employees': 'employees?school_id=' + str(self.id),
            'class_years': 'class_years?school_id=' + str(self.id),
            'subjects': 'subjects?school_id=' + str(self.id),
            'house_groups': 'house_groups?school_id=' + str(self.id),
            'class_groups': 'class_groups?school_id=' + str(self.id),
            'kudos_reasons': 'kudos_reasons?school_id=' + str(self.id)
        }

        self.count = count
        self.employess = self.get_employees()

    """def make_links():
        return {
            'students': 'students?school_id=' + str(self.id),
            'parents': 'parents?school_id=' + str(self.id),
            'employees': 'employees?school_id=' + str(self.id),
            'class_years': 'class_years?school_id=' + str(self.id),
            'subjects': 'subjects?school_id=' + str(self.id),
            'house_groups': 'house_groups?school_id=' + str(self.id),
            'class_groups': 'class_groups?school_id=' + str(self.id),
            'kudos_reasons': 'kudos_reasons?school_id=' + str(self.id)
        }"""

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
        
        payload = {"client_id": "55283c8c45d97ffd88eb9f87e13f390675c75d22b4f2085f43b0d7355c1f",
                    "client_secret": "c8f7d8fcd0746adc50278bc89ed6f004402acbbf4335d3cb12d6ac6497d3"}

        data = {"username": self.username, "password": self.password,
                "grant_type": "password", "school_id": self.school.id}
        temp = requests.post("https://api.showmyhomework.co.uk/oauth/token", params=payload, data=data,
                            headers={"Accept": "application/smhw.v3+json"})

        try:
            self.token = temp.json()["smhw_token"]
            self.token_expires_in = temp.json()["expires_in"]
            self.refresh_token = temp.json()["refresh_token"]
            self.token_created_at = temp.json()["created_at"]
            self.token_expires_at = self.token_created_at + self.token_expires_in
        except KeyError:
            raise CredentialError("Invalid Credentials")
        
        #self.id = self.get_user_id()

    def private_infos(include='user_private_info,school'): #useful info
        return self.user_api_request('students/' + self.id + '?include=' + include)

    def user_api_request(self, location, auth=True):
        if (int(time.time()) >= self.token_expires_at):
            self.refresh_oauth_token()
        
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

        self.token = temp.json()["smhw_token"]
        self.token_expires_in = temp.json()["expires_in"]
        self.refresh_token = temp.json()["refresh_token"]
        self.token_created_at = temp.json()["created_at"]
        self.token_expires_at = self.token_created_at + self.token_expires_in