from typing import Dict, Any

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from controllers.utils import StoreNotFoundError, handle_error, StoreExistsError
from db import db
from models import StoreModel
from schemas import PlainStoreSchema


blp = Blueprint("Stores", "stores", description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @staticmethod
    def _get_store(store_id: str) -> Dict[str, Any]:
        store = stores.get(store_id, None)
        if store is None:
            raise StoreNotFoundError
        return store

    @blp.response(200, PlainStoreSchema)
    @handle_error
    def get(self, store_id: int):
        store = StoreModel.get_or_404(store_id)
        return store

    @handle_error
    def delete(self, store_id: str):
        store = StoreModel.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": f"store {store_id} deleted."}


@blp.route("/store")
class StoreList(MethodView):

    @blp.response(200, PlainStoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(PlainStoreSchema)
    @blp.response(201, PlainStoreSchema)
    def post(self, store_data: Dict[str, Any]):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error ocurred while inserting Item.")

        return store
