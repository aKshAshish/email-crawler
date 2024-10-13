import datetime
import os
import json

from abc import ABC, abstractmethod
from typing import Union
from sqlalchemy import select
from models import Email
from db import SessionLocal
from action import Action
from predicate import Predicate, Contains, NotContains, NotEquals, Equals, All, Any, LessThan, GreaterThan

Fields = set(["recv_from", "subject", "message", "date"])

class Rule(ABC):
    """
    Abstract Rule Class.
    """
    @property
    @abstractmethod
    def SUPPORTED_PREDICATES(self):
        """Abstract property to be defined in subclasses."""
        pass

    @property
    @abstractmethod
    def SUPPORTED_FIELDS(self):
        """Abstract property to be defined in subclasses."""
        pass

    def __init__(self, predicate: Predicate, field: str, value: Union[str, int]):
        if not isinstance(predicate, self.SUPPORTED_PREDICATES):
            raise ValueError(f"Predicate {predicate} must be one of {self.SUPPORTED_PREDICATES}")
        if field not in self.SUPPORTED_FIELDS:
            raise ValueError(f"Predicate {value} must be one of {self.SUPPORTED_FIELDS}")
        self.predicate = predicate
        self.field = field
        self.value = value


class StringRule(Rule):
    """
    Rule for dealing with fields that have string data.
    """
    @property
    def SUPPORTED_PREDICATES(self):
        return (Contains, NotContains, Equals, NotEquals)
    
    @property
    def SUPPORTED_FIELDS(self):
        return ("recv_from", "subject", "message")
    
    def __init__(self, predicate: Predicate, field: str, value: str):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        super().__init__(predicate, field, value)


class DateRule(Rule):
    """
    Rule for date specific conditions.
    """
    @property
    def SUPPORTED_PREDICATES(self):
        return (LessThan, GreaterThan)
    
    @property
    def SUPPORTED_FIELDS(self):
        return ("date")
    
    def __init__(self, predicate: Predicate, field: str, value: int):
        if not isinstance(value, int):
            raise ValueError("Value must be an integer.")
        today_timestamp = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min).timestamp() * 1000
        value = today_timestamp - value * (60*60*24*1000)
        super().__init__(predicate, field, value)


class CompositeRule:
    """
    Represents collection of rules.
    """
    SUPPORTED_PREDICATES = (All, Any)
    def __init__(self, rules: list[Rule], predicate: Predicate, actions) -> None:
        self.validate(rules, predicate, actions)
        self.rules = rules
        self.predicate = predicate
        self.actions = actions


    def validate(self, rules: list[Rule], predicate, actions):
        if not isinstance(predicate, self.SUPPORTED_PREDICATES):
            raise ValueError(f"Predicate must be one of {self.SUPPORTED_PREDICATES}")
        if not all([isinstance(rule, Rule) for rule in rules]):
            raise ValueError("All rules must be of type Rule.")
        

    def execute(self):
        query = select(Email.email_id, Email.id).where(
            self.predicate('', [rule.predicate(rule.field, rule.value) for rule in self.rules])
        )
        session = SessionLocal()
        results = session.execute(query).all()
        return results
    
    def apply(self):
        results = self.execute()
        ids = [email_id for (email_id, _) in results]
        for action in self.actions:
            action(ids)


def create_predicate(predicate):
    switcher: dict[str, Predicate] = {
        'contains': Contains(), 
        'notcontains': NotContains(), 
        'equals': Equals(), 
        'notequals': NotEquals(), 
        'any': Any(), 
        'all': All(), 
        'ltndays': GreaterThan(), 
        'gtndays': LessThan()
    }
    if predicate not in switcher.keys():
        raise ValueError(f"{predicate} must be one of {switcher.keys()}.")

    return switcher[predicate]


def create_rule(schema):
    req_keys = {"predicate", "field", "value"}
    if req_keys != set(schema.keys()):
        raise ValueError("Properties required to create Rule are not present")
    
    if schema['field'] == 'date':
        return DateRule(
            predicate=create_predicate(schema["predicate"]),
            field=schema["field"],
            value=schema["value"]
        )
    else:
        return StringRule(
            predicate=create_predicate(schema["predicate"]),
            field=schema["field"],
            value=schema["value"]
        )

def create_action(schema):
    req_key = {"action", "value"}
    if req_key != set(schema.keys()):
        raise ValueError("Properties required to create Action are not present")
    return Action(schema["action"], schema["value"])

def create_composite_rule(file_path):
    if not os.path.exists(file_path):
        raise ValueError(f"{file_path} does not exist")
    
    with open(file_path, 'r') as fp:
        rule_schema = json.load(fp)

    req_keys = {"predicate", "actions", "rules"}
    if req_keys != set(rule_schema.keys()):
        raise ValueError("Properties required to create Composite Rule are not present")
    
    composite_rule = CompositeRule(
        rules=[create_rule(rule) for rule in rule_schema['rules']],
        predicate=create_predicate(rule_schema['predicate']),
        actions=[create_action(action) for action in rule_schema['actions']]
    )
    return composite_rule