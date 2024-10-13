from dotenv import load_dotenv
from rule import create_composite_rule
from db import init_db

load_dotenv()
init_db()

composite_rule = create_composite_rule('rule.json')
composite_rule.apply()