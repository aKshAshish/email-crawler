import os.path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]

def load_creds():
	"""
	Loads token from Google OAuth to be used by google client to access the apis.
	"""
	creds = None
	# The file at PATH_TOKENS stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists(os.environ.get('PATH_TOKENS')):
		creds = Credentials.from_authorized_user_file(os.environ.get('PATH_TOKENS'), SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				os.environ.get('PATH_GMAIL_CREDENTIALS'), SCOPES
			)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(os.environ.get('PATH_TOKENS'), "w") as token:
			token.write(creds.to_json())

	return creds