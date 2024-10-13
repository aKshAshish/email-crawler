import datetime

from abc import ABC, abstractmethod
from sqlalchemy import select
from models import Email
from db import SessionLocal
from predicate import Predicate, Contains, NotContains, NotEquals, Equals, All, Any, LessThan, GreaterThan
from typing import Union


Fields = set(["recv_from", "subject", "message", "date"])
Predicates = set(['contains', 'notcontains', 'equals', 'notequals', 'any', 'all', 'ltndays', 'gtndays'])

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
        if predicate not in self.SUPPORTED_PREDICATES:
            raise ValueError(f"Predicate {predicate} must be one of {self.SUPPORTED_PREDICATES}")
        if predicate not in self.SUPPORTED_FIELDS:
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
        if predicate not in self.SUPPORTED_PREDICATES:
            raise ValueError(f"Predicate must be one of {self.SUPPORTED_PREDICATES}")
        if not all([isinstance(rule, Rule) for rule in rules]):
            raise ValueError("All rules must be of type Rule.")
        

    def execute(self):
        query = select(Email.email_id, Email.id).where(
            self.predicate()('', [rule.predicate()(rule.field, rule.value) for rule in self.rules])
        )
        session = SessionLocal()
        results = session.execute(query).all()
        return results