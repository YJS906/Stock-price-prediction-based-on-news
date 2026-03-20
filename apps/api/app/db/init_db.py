import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.base import Base
from app.db.session import get_engine
from app.models import domain  # noqa: F401


def init_db(drop_all: bool = False, max_retries: int = 15, retry_delay_seconds: float = 2.0) -> None:
    engine = get_engine()
    last_error: OperationalError | None = None

    for attempt in range(1, max_retries + 1):
        try:
            if drop_all:
                Base.metadata.drop_all(engine)

            if engine.dialect.name == "postgresql":
                with engine.begin() as connection:
                    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

            Base.metadata.create_all(engine)
            return
        except OperationalError as exc:
            last_error = exc
            if attempt == max_retries:
                raise
            time.sleep(retry_delay_seconds)

    if last_error is not None:
        raise last_error
