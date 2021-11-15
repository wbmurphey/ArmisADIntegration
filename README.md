# ArmisADIntegration

This tool is for efficiently managing Armis users who belong to a specific Active Directory group in an Active Directory domain.

## Usage

In the main.py, make sure the following variables are properly defined:

```
config_file
ad_group
api_key
```

config_file should be the path to a file with the following format:

/home/exampleuser/ad.ini:
```
[AD]
username = <username here>
password = <password here>
```

ad_group should be a string specifying the Active Directory group you wish to manage with proper Active Directory syntax.

api_key should be a string containing only your Armis API key.

Once these three variables are correctly defined, run main.py from a network on which your Active Directory domain is reachable.

## Expected Behavior

When you run main.py, the script should walk through the following steps:
1. Retrieve current Armis users, check whether or not they are in Active Directory, and delete those that are not.
2. Retrieve current Armis users with both @charter.com emails and those that belong to the specified group, and updates the role assignments of these users as necessary.
3. Compares current Armis users with users in the specified group, and adds new Armis users as necessary.
