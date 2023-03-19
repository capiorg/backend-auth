import logging
from functools import wraps

from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from app.exceptions.db.exceptions import handle_db_api_error
from app.exceptions.db.exceptions import handle_foreign_key_error
from app.exceptions.db.exceptions import handle_not_found_error
from app.exceptions.db.exceptions import handle_not_null_violation_error
from app.exceptions.db.exceptions import handle_unique_error

logger = logging.getLogger(__name__)


def orm_error_handler(func):
    @wraps(func)
    async def decorator(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except IntegrityError as exc:
            logger.warning(msg="error orm_error_handler", exc_info=exc)
            sql_detail = str(exc.orig.obj.detail)
            handle_not_null_violation_error(exc=exc)
            handle_unique_error(exc=exc, sql_detail=sql_detail)
            handle_foreign_key_error(exc=exc)

        except NoResultFound as exc:
            logger.warning(msg="error orm_error_handler", exc_info=exc)
            handle_not_found_error(exc=exc)

        except DBAPIError as exc:
            logger.warning(msg="error orm_error_handler", exc_info=exc)

            sql_detail = str(exc.orig.obj.detail)
            handle_db_api_error(exc=exc, sql_detail=sql_detail)

        except Exception as exc:
            print(f"\n\n\n\n\n ошибка \n\n\n\n")
            logger.warning(msg="error orm_error_handler", exc_info=exc)
    return decorator
