import re

import sqlalchemy
from backend.exceptions import (
    QuestionNotFoundProblem,
    UserNotFoundProblem,
)


def handle_foreign_key_violation(error: sqlalchemy.exc.IntegrityError) -> None:
    error_str = str(error.orig)
    key_match = re.search(r"Key \((.+?)\)=\((.+?)\)", error_str)

    if not key_match:
        raise error

    column_name = key_match.group(1)
    value = key_match.group(2)

    fk_exception_map = {
        "question_id": QuestionNotFoundProblem,
        "owner_id": UserNotFoundProblem,
        "user_id": UserNotFoundProblem,
    }

    exception_class = fk_exception_map.get(column_name)
    if exception_class:
        entity_name = column_name.replace("_id", "")
        raise exception_class(f"{entity_name.capitalize()} {value} not found")

    raise error
