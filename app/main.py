from dotenv import load_dotenv
from rule import CompositeRule, StringRule, DateRule
from predicate import All, Contains, NotContains, GreaterThan, LessThan
from db import init_db
import datetime

load_dotenv()
init_db()

composite_rule = CompositeRule(
    rules=[
        DateRule(LessThan, 'date', 1)
    ],
    predicate=All,
    actions=[]
)
print(composite_rule.execute())

# print(Contains in (Contains, NotContains, All))