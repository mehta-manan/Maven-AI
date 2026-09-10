import os

from instagram.instagram_account import InstagramAccount

class PersonalInstagramAccount(InstagramAccount):
    def __init__(self) -> None:
        id = str(os.getenv('MY_IG_ID'))
        auth_token = str(os.getenv('PERSONAL_AUTH_TOKEN'))
        super().__init__(id, auth_token)