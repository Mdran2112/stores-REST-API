from functools import wraps

from flask_jwt_extended import get_jwt
from flask_smorest import abort


class ItemNotFoundError(Exception):
    ...


class StoreNotFoundError(Exception):
    ...


class StoreExistsError(Exception):
    ...


def handle_error(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        try:
            resp = f(*args, **kws)
            return resp
        except Exception as ex:
            import traceback
            traceback = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
            print(traceback)
            return abort(500, message="Internal error.")

    return decorated_function


def admin_request(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        jwt = get_jwt()
        if not jwt.get("is_admin", False):
            abort(401, message="Admin privilege required.")
        resp = f(*args, **kws)
        return resp

    return decorated_function
