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

To run a fresh postgres using docker run following command:
```bash
    # Run from the directory with docker-compose.yml file
    # To start the docker container
    docker-compose up -d
    # To stop the container
    docker-compose down
```

### *Loading Emails to Database*: 
To load emails to database run the script *load_emails.py* from app folder. If the argument for number of emails is not passed the script will only load 500 emails.
> [!IMPORTANT]
> Before loading emails to DB, the script gets the list of emails and stores in the folder pointed by DIR_EMAILS of .env file. So please make sure to delete the files from previous runs.

```bash
    # if not in app directory
    cd app
    # Will load 1000 emails from the gmail starting from recent
    python load_emails.py -n 1000
```
### *Executing Rules*:
- Once the emails are loaded. We can run our *main.py* file that executes the rule present in *rule.json* file as default rule. If required the path to rule file can be passed as an argument as shown in the example.
```bash
    # Runs default rule file rule.json
    python main.py
    # Run the rule in the file provided
    python main.py -p ex-rule.json
```

## Running Test Cases
The test cases are run from project directory (i.e. parent directory of app). To run all the test cases run the following command
```bash
    python -m pytest
```

## Rule Details
For reference some example rules are present in [example_rules.json](./app/example_rules.json).
- Schema **Composite Rule**:
```json
    {
        "predicate": "string",
        "rules": ["Rule 1", "Rule 2"],
        "actions": ["string"]
    }
```
- **Rule** Schema:
```json
    {
        "predicate": "string",
        "value": "string|number",
        "field": "string"
    }
```
- **Fields** can be one of the following:
```python
('recv_from', 'date', 'subject', 'message')
```
- **Predicates** can be one of the following:
```python
('contains', 'notcontains' 'equals', 'notequals', 'any', 'all', 'ltndays', 'gtndays')
```
- **Actions** can be one of the follwing: 
```python
('mark_as_read', 'mark_as_unread', 'move')
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