import json

from ldap3 import ALL, NTLM, Connection, Server


class LDAPClient:
    def __init__(self, username: str, password: str):
        self.AD_SERVERS = "your domain here"
        self.DOMAIN = "your domain here"
        self.AD_GROUP_FILTER = "(&(objectClass=USER)(memberOf={group}))"
        self.AD_USER_FILTER = "(&(objectClass=USER)(mail={email}))"
        self.AD_BIND_USER = username
        self.AD_BIND_PWD = password
        self.conn = self.connect_to_server()

    def connect_to_server(self):
        tls_config = Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=path)
        server = Server(self.AD_SERVERS, port=636, use_ssl=True, get_info=ALL)
        conn = Connection(server, user=f"{self.DOMAIN}\\{self.AD_BIND_USER}", password=self.AD_BIND_PWD, auto_bind=True, authentication=NTLM)
        return conn

    def get_group_members(self, group: str):
        """Returns a dictionary with users' email as keys, and a dictionary of attributes from AD as values.\n
        For 'group' use the distinguished name for the desired group.\n
        For example, for the NSA team's group, use:\n 
        'CN=RG-InfrastructArchEng-AdvEngSecurity,OU=Roles,OU=Groups,OU=SPECTRUM,DC=CORP,DC=CHARTERCOM,DC=com'"""
        ad_filter = self.AD_GROUP_FILTER.replace("{group}", group)
        return_attributes = ["givenName", "sn", "mail", "title", "l", "st"]
        self.conn.search(search_base=self.DOMAIN, search_filter=ad_filter, attributes=return_attributes)
        ent_dict = {}
        for i, entry_obj in enumerate(self.conn.entries):
            ent_dict[i] = json.loads(entry_obj.entry_to_json())["attributes"]
        return ent_dict

    def get_users_groups(self, email: str):
        """Returns a list of the groups that a specified user belongs to.\n
        For email use an @charter.com email address."""
        ad_filter = self.AD_USER_FILTER.replace("{email}", email)
        return_attributes = ["memberOf"]
        self.conn.search(search_base=self.DOMAIN, search_filter=ad_filter, attributes=return_attributes)
        ent_list = []
        for i, entry_obj in enumerate(self.conn.entries):
            ent_list.append(json.loads(entry_obj.entry_to_json())["attributes"])
            ent_list = ent_list[i]["memberOf"]
        return ent_list

    def is_in_ad(self, email: str):
        """For determining whether or not a user is in AD. Returns True/False.\n
        For email use an @charter.com email address."""
        ad_filter = self.AD_USER_FILTER.replace("{email}", email)
        self.conn.search(search_base=self.DOMAIN, search_filter=ad_filter)
        if self.conn.entries:
            return True        
        else:
            return False

    def format_group_members(self, entries: dict):
        """Returns a formatted dictionary.\n
        For 'entries' use the dictionary returned by get_group_members()."""
        formatted_entries = {}
        for k, v in entries.items():
            email = entries[k]["mail"][0]
            location = entries[k]["l"][0].title() + ", " + entries[k]["st"][0].upper()
            name = entries[k]["givenName"][0] + " " + entries[k]["sn"][0]
            title = entries[k]["title"][0]
            username = entries[k]["givenName"][0][0] + entries[k]["sn"][0]
            formatted_entries[email.lower()] = {
                "email": email.lower(),
                "location": location,
                "name": str(name),
                "title": str(title),
                "username": username.lower()
                }
        return formatted_entries
        
