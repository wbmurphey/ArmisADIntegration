import configparser
import armis_client
import ldap_client

if __name__ == "__main__":
    # Defines groups that Armis will use for role assignment.
    dn_var = "DN for your group"
    group_roles = {
        # Add dn_var to appropriate values for roles
        "Admin": [],
        "Read Only": [],
        "Security Analyst": [],
        "Asset Manager": [],
        "Integrations Manager": [],
        "User Manager": [],
        "Alert Resolver": [],
        "Full Advanced Permissions": [],
        "Policy Manager": [],
        "Read Only with Reports": [],
        "Read Write": [],
        "Read Write with Reports": [],
        }
    
    # Specifies the file from which configparser extracts AD credetials.
    # config_file = "path to your config file"
    config = configparser.ConfigParser()
    config.read(config_file)

    # Specifies the AD group whose members will be added as Armis users, then connects to and queries the AD.
    ad_group = dn_var
    connection = ldap_client.LDAPClient(username=config["AD"]["username"], password=config["AD"]["password"])
    
    # Specifies the api key to use with the Armis API, establishes a connection with the API, and gets all current Armis users.
    api_key = "your api key here"
    base = "https://url here"
    api_instance = armis_client.APIClient(base=base, api_key=api_key, verify=False)
    
    # Defines a function that will return a list of roles for a specified group.
    def find_role(group: str):
        """Pass an AD group for "group". Returns a list of allowed Armis roles."""
        role_assignments = []
        for k, v in group_roles.items():
            if group in v:
                role_assignments.append(k)
        return role_assignments
    
    # Defines a function that will return two dictionaries: one of current Armis users with @charter.com emails,
    # and one of current Armis users without @charter.com emails.
    def get_charter_users():
        """Returns dictionary of @charter.com Armis users, and dictionary of non-@charter.com Armis users."""
        arm_usrs = api_instance.format_users(api_instance.get_all_users())
        arm_dict = {}
        noncharter_arm_dict = {}
        for k, v in arm_usrs.items():
            if "@charter.com" in k:
                arm_dict[k] = v
            else:
                noncharter_arm_dict[k] = v
        return arm_dict, noncharter_arm_dict

    def get_users_in_group(group: str):
        """Pass an AD group for "group". Returns a dictionary of Armis users only from that group."""
        ch_arm_usrs, nch_arm_usrs = get_charter_users()
        grp_mems = connection.format_group_members(connection.get_group_members(group=group))
        grp_arm_dict = {}
        non_grp_arm_dict = {}
        for k, v in ch_arm_usrs.items():
            if k in grp_mems:
                grp_arm_dict[k] = v
            else:
                non_grp_arm_dict[k] = v
        return grp_arm_dict, non_grp_arm_dict

    # Checks if all Armis users with @charter.com email are still in AD, and deletes those that are not.
    armis_users, noncharter_armis_users = get_charter_users()
    for k, v in armis_users.items():
        if connection.is_in_ad(k) == False:
            api_instance.delete_users(k)
            print(f"Deleted user with email {k}.")
    print(f"The following {len(noncharter_armis_users)} Armis users have non-Charter emails, and will not be updated:")
    for k, v in noncharter_armis_users.items():
        print(k)

    # Retrieves current Armis users in the specified group, and checks if their role assignments are correct, then updates necessary role assignments.
    armis_users, non_group_armis_users = get_users_in_group(group=ad_group)
    
    print(f"The following {len(non_group_armis_users)} Armis users do not belong to {ad_group}, and will not be updated:")
    for k, v in non_group_armis_users.items():
        print(k)

    current_armis_user_roles = {}
    allowed_armis_user_roles = {}
    for k, v in armis_users.items():
        current_armis_user_roles[k] = v["roleAssignment"]

    for k, v in current_armis_user_roles.items():
        role_list = []
        for grp in connection.get_users_groups(k):
            if find_role(group=grp):
                roles = find_role(group=grp)
                for role in roles:
                    role_list.append(role)
        allowed_armis_user_roles[k] = role_list

    if current_armis_user_roles != allowed_armis_user_roles:
        for k, v in current_armis_user_roles.items():
            if current_armis_user_roles[k] != allowed_armis_user_roles[k]:
                print(f"Current role(s) for {k}: {current_armis_user_roles[k]}\nAllowed role(s) for {k}: {allowed_armis_user_roles[k]}")
                for i in v:
                    if i not in allowed_armis_user_roles[k]:
                        # REMOVE ROLE "i" FROM ARMIS USER'S ROLE ASSIGNMENTS
                        api_instance.update_roles(email=k, role_assignment=allowed_armis_user_roles[k])
                        print(f"Updated user {k}: Removed role {i}.")
                for i in allowed_armis_user_roles[k]:
                    if i not in v:
                        # ADD ROLE "i" TO ARMIS USER'S ROLE ASSIGNMENTS
                        api_instance.update_roles(email=k, role_assignment=allowed_armis_user_roles[k])
                        print(f"Updated user {k}: Added role {i}.")
    else:
        print("All users role assignments are up to date.")
    
    # Compares Armis users and members of specified AD group, and adds AD group members with no Armis account.
    armis_users, non_group_armis_users = get_users_in_group(ad_group)
    ad_users = connection.format_group_members(connection.get_group_members(ad_group))
    group_role_assingments = find_role(group=ad_group)
    ctr = 0
    for k, v in ad_users.items():
        if k not in armis_users:
            # print(k)
            r = api_instance.post_users(email=v["email"], location=v["location"], name=v["name"], role_assignment=group_role_assingments, title=v["title"], username=v["username"])
            print(f"{k} = {r.text}")
            ctr += 1

    if ctr == 0:
        print(f"AD users from group {ad_group} are all already added to Armis.")
    else:
        print(f"Armis successfully updated with new users from AD.")
