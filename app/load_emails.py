import os.path
import json
import base64

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from db import init_db, SessionLocal
from models import Email

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
MAX_RESULTS = 100

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


def get_db():
    db = SessionLocal()
    return db


def load_email(email, db):
	"""
	Adds email to the database.
	"""
	print(f"Adding email: {email['id']}")
	res = db.query(Email).filter_by(email_id = email['id']).first()
	if res:
		return
	db_email = Email(email_id=email['id'], message=email['message'], recv_from=email['recv_from'], date=email['date'], subject=email['subject'])
	db.add(db_email)
	db.commit()
	db.refresh(db_email)
	

def parse_headers(headers, parsed_email):
	"""
	Parses email headers to fetch Date, From and Subject of the email.
	"""
	parse_for = set(["From", "Subject"])
	for header in headers:
		if header["name"] in parse_for:
			key = header["name"].lower()
			if key == 'from':
				key = "recv_"+key
			parsed_email[key] = header["value"]


def parse_body(body):
	"""
	Parse email body and body part if it has data.
	"""
	if "data" in body.keys():
		return base64.urlsafe_b64decode(body["data"]).decode()
	return ""


def parse_email(email):
	"""
	Parses email data.
	"""
	# Initialize parsed email with empty data.
	parsed_email = {
		"id": "",
		"message": "",
		"date": 0,
		"from": "",
		"subject": ""
	}

	parsed_email["id"] = email["id"]
	parsed_email['date'] = email['internalDate']

	# Add data to parsed email.
	if "payload" in email.keys():
		payload = email["payload"]
		if "headers" in payload.keys():
			headers = payload["headers"]
			parse_headers(headers, parsed_email)
		if "body" in payload.keys():
			parsed_email["message"] += parse_body(payload["body"])
		if "parts" in payload.keys():
			for part in payload["parts"]:
				if "body" in part.keys():
					parsed_email["message"] += parse_body(part["body"])

		return parsed_email
		
	return None


def fetch_email(id: str):
	"""
	Fetch detailed email from gmail.
	"""
	# Gets credentials using Google OAuth Client
	creds = load_creds()
	# Gmail Service
	service = build("gmail", "v1", credentials=creds)
	
	return service.users().messages().get(userId="me", id=id).execute()


def load_emails_to_db():
	"""
	Goes through preloaded list of emails and fetches content of the email from gmail, parses it and loads the data into database.
	"""
	DIR_EMAILS = os.environ.get("DIR_EMAILS")
	db = get_db()
	if os.path.exists(DIR_EMAILS):
		dir_email = Path(DIR_EMAILS)
		for file in dir_email.iterdir():
			with open(file, 'r') as fp:
				emails = json.load(fp)
			 
			for email in emails:
				result = fetch_email(email['id'])
				parsed_email = parse_email(result)
				if parsed_email:
					load_email(parsed_email, db)


def fetch_emails(num: int):
	"""
	Fetches email list from gmail.
	"""
	# Gets credentials using Google OAuth Client
	creds = load_creds()
	# Call the Gmail API
	service = build("gmail", "v1", credentials=creds)
	next_page_token = ""
	i = 1

	while num > 0:
		if not creds.valid:
			creds = load_creds()
			service = build("gmail", "v1", credentials=creds)
		max_results = num if num < MAX_RESULTS else MAX_RESULTS
		num -= max_results
		results = service.users().messages().list(userId="me", pageToken= next_page_token, maxResults=str(max_results)).execute()
		messages = results.get("messages", [])

		# Write messages to file
		file_name = os.environ.get("DIR_EMAILS") + f"/emails-{i}.json"
		with open(file_name, "w") as fp:
			json.dump(messages, fp)

		next_page_token = results.get("nextPageToken", "")
		i += 1 # Increment Suffix for next file

		if not next_page_token:
			break


def load_emails(num=100):
	"""
	Loads emails to database.
	"""
	try:
		fetch_emails(num)
		load_emails_to_db()
	except HttpError as error:
		print(f"An error occurred: {error}")


if __name__ == "__main__":
	# Load environment variables
	load_dotenv()
	# Initialize database
	init_db()
	# Load Emails
	load_emails(205)
