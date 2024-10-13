import os.path
import json
import base64
import argparse

from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from db import init_db, SessionLocal
from dotenv import load_dotenv
from models import Email
from util import load_creds

MAX_RESULTS = 500

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


def load_emails(num):
	"""
	Loads emails to database.
	"""
	try:
		fetch_emails(num)
		load_emails_to_db()
	except HttpError as error:
		print(f"An error occurred: {error}")


def create_num_emails_parser():
    parser = argparse.ArgumentParser(description='Specify the number of emails to load from gmail.')
    parser.add_argument(
        '-n', 
        '--num', 
        type=str, 
        required=False, 
        help='Number of emails to fetch from Gmail'
    )
    return parser

if __name__ == "__main__":
	parser = create_num_emails_parser()
	args = parser.parse_args()
	num = 500 if args.num is None else args.num
	# Load environment variables
	load_dotenv()
	# Initialize database
	init_db()
	# Load Emails
	load_emails(num)
