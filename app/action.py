import requests
import json

from util import load_creds

MAX_IDS_SUPPORTED = 1000

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
        """
        Dunder method makes action object callable.
        """
        creds = load_creds()
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify"
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        }

        # Taking actions in chunk as batchModify only supports 1000 ids per request
        n = len(ids)
        iterations = (n//MAX_IDS_SUPPORTED) if n % MAX_IDS_SUPPORTED == 0 else ((n//MAX_IDS_SUPPORTED) + 1)
        print(f"Action {self.action} will be taken in {iterations} chunk.")
        for i in range(iterations):
            start = i * MAX_IDS_SUPPORTED
            end = n if ((i+1) * MAX_IDS_SUPPORTED) > n else ((i+1) * MAX_IDS_SUPPORTED)
            id_chunk = ids[start:end]
            body = self.translate(id_chunk)
            res = requests.post(url, headers=headers, data=json.dumps(body))
            if res.status_code // 100 == 2:
                print(f"Action {self.action} is done.")
                return
            else:
                print(f"Failed to take action on {id_chunk}.")


    def translate(self, ids):
        """
        Created request body.
        """
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