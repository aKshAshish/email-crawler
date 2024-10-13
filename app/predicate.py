from sqlalchemy import not_, and_, or_
from models import Email

class Predicate:
    """Base class for all predicates."""
    def __call__(self, field, value):
        raise NotImplementedError("Subclasses must implement this method.")

class Contains(Predicate):
    def __call__(self, field, value):
        return getattr(Email, field).ilike(f'%{value}%')

class NotContains(Predicate):
    def __call__(self, field, value):
        return getattr(Email, field).not_ilike(f'%{value}%')

class Equals(Predicate):
    def __call__(self, field, value):
        return getattr(Email, field).__eq__(value)

class NotEquals(Predicate):
    def __call__(self, field, value):
        return not_(getattr(Email, field).__eq__(value))
    
class LessThan(Predicate):
    def __call__(self, field, value):
        return getattr(Email, field).__lt__(value)
    
class GreaterThan(Predicate):
    def __call__(self, field, value):
        return getattr(Email, field).__gt__(value)
    
class All(Predicate):
    def __call__(self, _, value):
        return and_(*value)
    
class Any(Predicate):
    def __call__(self, _, value):
        return or_(*value)