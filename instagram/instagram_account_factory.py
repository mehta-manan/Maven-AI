from abc import ABC

from instagram.instagram_accounts import InstagramAccounts
from instagram.instagram_account import InstagramAccount

from instagram.accounts.mavenai_account import MavenAIInstagramAccount
from instagram.accounts.personal_account import PersonalInstagramAccount

class InstagramAccountFactory(ABC):
    @staticmethod
    def create(account_type) -> InstagramAccount:
        match account_type:
            case InstagramAccounts.MAVEN_AI:
                return MavenAIInstagramAccount()
            case InstagramAccounts.PERSONAL:
                return PersonalInstagramAccount()
            case _:
                 raise ValueError(f"Unsupported account type: {account_type}")