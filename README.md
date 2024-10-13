# email-crawler

## Project Setup
1. To start clone the project and open the project directory.
2. Once there create Python Virtual Environment: 
```bash 
python -m venv .venv
```
3. Run the following command to install the requirements:
```bash
pip install -r requirements.txt
```
4. Update .env file with proper values. P.S. The relative paths are w.r.t app directory.
5. To setup your google project and to get client credentials follow instructions on [this](https://developers.google.com/gmail/api/quickstart/python) page.

## Running Project
Once all the steps above have been completed we can prepare our Database. If the docker is present on the machine we can use docker-compose file to run an instance of postgres that we can use. Or if we want to use existing postgres please update the properties in .env.

### *Loading Emails to Database*: 
To load emails to database run the script *load_emails.py* from app folder.
```bash
    # if not in app directory
    cd app
    python load_emails.py
```
### *Executing Rules*:
- Once the emails are loaded. We can run our *main.py* file that executes the rule present in *rule.json* file.
```bash
    python main.py
```

## Project Structure
```
email-crawler/
│
├── app/
│   ├── __init__.py
│   ├── load_emails.py
│   ├── main.py
│   ├── db.py
│   ├── *
│
├── tests/
│   ├── __init__.py
│   ├── test_util.py
│   ├── test_action.py
│
├── README.md
*
```