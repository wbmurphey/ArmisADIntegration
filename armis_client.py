import json

import requests


class APIClient:
    def __init__(self, base: str, api_key: str, verify: bool=True):
        self.base = base
        self.api_key = api_key
        self.endpoint_users = "/api/v1/users/"
        self.endpoint_token = "/api/v1/access_token/"
        self.application_json = "application/json"
        self.headers = {"accept": self.application_json}
        self.verify = verify
        self.post_access_token()

    def post_access_token(self) -> None:
        endpoint = self.endpoint_token
        headers = {"accept": self.application_json, "content-type": "application/x-www-form-urlencoded"}
        data = {"secret_key": self.api_key}
        response = requests.post(url=self.base+endpoint, headers=headers, data=data, verify=self.verify)
        if response.ok == True:
            self.headers["Authorization"] = response.json()["data"]["access_token"]
        else:
            raise Exception

    def get_all_users(self):
        response = requests.get(url=self.base+self.endpoint_users, headers=self.headers, verify=self.verify)
        return response

    def format_users(self, armis_users: dict):
        formatted_users = {}
        users = armis_users.json()
        if users["success"] == True:
            users = users["data"]["users"]
            for i in users:
                email = i["email"]
                location = i["location"]
                name = i["name"]
                role_assignment = i["roleAssignment"][0]["name"]
                title = i["title"]
                username = i["username"]
                formatted_users[email] = {
                    "email": email.lower(),
                    "location": location,
                    "name": str(name),
                    "roleAssignment": role_assignment,
                    "title": str(title),
                    "username": username.lower()
                    }
        return formatted_users

    def get_specific_user(self, email: str="", armis_id: str=""):
        if email and not armis_id:
            endpoint = f"{self.endpoint_users}{email}/"
        elif armis_id and not email:
            endpoint = f"{self.endpoint_users}{armis_id}/"
        else:
            endpoint = {self.endpoint_users}
        response = requests.get(url=self.base+endpoint, headers=self.headers, verify=self.verify)
        return response
    
    def delete_users(self, email: str="", armis_id: str=""):
        """Use a user's Armis ID or email address to specify user to be deleted."""
        if email and not armis_id:
            endpoint = f"{self.endpoint_users}{email}/"
        elif armis_id and not email:
            endpoint = f"{self.endpoint_users}{armis_id}/"
        else:
            endpoint = self.endpoint_users
        response = requests.delete(url=self.base+endpoint, headers=self.headers, verify=self.verify)
        print(response.text)

    def post_users(self, email: str, location: str, name: str, role_assignment: list,  title: str, username: str, role: str="", phone: str=""):
        """For role_assingment select from: [Admin, Read Only, Security Analyst, 
        Asset Manager, Integrations Manager, User Manager, Alert Resolver, 
        Full Advanced Permissions, Policy Manager, Read Only with Reports, 
        Read Write, Read Write with Reports]"""
        post_users_headers = self.headers
        post_users_headers["content-type"] = self.application_json
        endpoint = self.endpoint_users
        data = {
            "email": email,
            "location": location,
            "name": name,
            "phone": phone,
            "role": role,
            "roleAssignment": [{"name": role_assignment}],
            "title": title,
            "username": username
            }
        response = requests.post(url=self.base+endpoint, headers=post_users_headers, data=json.dumps(data), verify=self.verify)
        if response.ok:
            print(f"{name} added")
        return response

    def update_roles(self, email: str, role_assignment: list):
        """Pass a list of role assignments to replace the current list of role assignments for the user."""
        add_role_headers = self.headers
        add_role_headers["content-type"] = self.application_json
        endpoint = f"{self.endpoint_users}{email}/"
        if role_assignment == []:
            role_assignment = ["Read Only"]
            print(f"Role assignment cannot be blank. User {email} will be assigned Read Only role.")
        data = {"roleAssignment": [{"name": role_assignment}]}
        response = requests.patch(url=self.base+endpoint, headers=add_role_headers, data=json.dumps(data), verify=self.verify)
        return response
