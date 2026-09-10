import os

from instagram_account import InstagramAccount

class MavenAIInstagramAccount(InstagramAccount):
    def __init__(self) -> None:
        id = str(os.getenv('MAVEN_AI_IG_ID'))
        auth_token = str(os.getenv('AI_AUTH_TOKEN'))
        super().__init__(id, auth_token)