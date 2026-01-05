import re

from sqlalchemy import inspect


def resolve_table_name(name: str) -> str:
    """Resolve PascalCase model name to snake_case table name."""
    names = re.split(r'(?=[A-Z])', name)  # Split by capital letters
    return '_'.join([x.lower() for x in names if x])


def build_model_representation(model) -> str:
    """Build simple __repr__ for a model, e.g. ModelName(id=<id value>)."""
    identities = inspect(model).identity
    if identities:
        identity_str = '-'.join([str(identity) for identity in identities])
    else:
        identity_str = 'None'
    return f'{model.__class__.__name__}(id={identity_str})'
