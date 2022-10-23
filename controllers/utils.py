from functools import wraps
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
        except ItemNotFoundError as e:
            return abort(404, message="Item not found")
        except StoreNotFoundError as e:
            return abort(404, message="Store not found")
        except StoreExistsError as e:
            return abort(400, message=f"Store already exists.")
        except Exception as ex:
            import traceback
            traceback = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
            print(traceback)
            return abort(500, message="Internal error.")

    return decorated_function
