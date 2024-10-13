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
5. To setup your google project follow instructions on [this](https://developers.google.com/gmail/api/quickstart/python) page.
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
```