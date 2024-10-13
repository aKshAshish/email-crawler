import requests
import json

from util import load_creds

class Action:
    """
    Class to represent and perform actions.
    """
    SUPPORTED_ACTIONS = ('mark_as_read', 'mark_as_unread', 'move')
    def __init__(self, action: str, param="") -> None:
        if action not in self.SUPPORTED_ACTIONS:
            raise ValueError(f'{action} should be one of {self.SUPPORTED_ACTIONS}')
        self.action = action
        self.param = param

    def __call__(self, ids: list[str]):
        creds = load_creds()
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify"
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        }
        body = self.translate(ids)
        res = requests.post(url, headers=headers, data=json.dumps(body))
        if res.status_code // 100 == 2:
            print(f"Action {self.action} is done.")
            return
        else:
            raise Exception(f"Http Error occured with code {res.status_code}. Reason: {res.text}")

    def translate(self, ids):
        if self.action == 'mark_as_read':
            return {
                "ids": ids,
                "removeLabelIds": [
                    "UNREAD"
                ]
            }
        
        if self.action == 'mark_as_unread':
            return {
                "ids": ids,
                "addLabelIds": [
                    "UNREAD"
                ]
            }
        
        if self.action == 'move':
            if self.param == "":
                raise ValueError("Pass a valid folder to move email to.")
            return {
                "ids": ids,
                "addLabelIds": [
                    self.param
                ]
            }