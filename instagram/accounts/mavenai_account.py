import os

from instagram.instagram_account import InstagramAccount
from instagram.instagram_accounts import InstagramAccounts

class MavenAIInstagramAccount(InstagramAccount):
    def __init__(self) -> None:
        id = str(os.getenv('AI_ACCOUNT_RECEIVER_ID'))
        auth_token = str(os.getenv('AI_AUTH_TOKEN'))
        super().__init__(id, auth_token, InstagramAccounts.MAVEN_AI.value)