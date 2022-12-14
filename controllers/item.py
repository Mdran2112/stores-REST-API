from typing import Dict, Any

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from controllers.utils import handle_error, admin_request
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema
from db import db

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):

    @blp.response(200, ItemSchema)
    def get(self, item_id: int):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    @admin_request
    def delete(self, item_id: int):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": f"Item {item_id} deleted"}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    @handle_error
    def put(self, item_data: Dict[str, Any], item_id: str):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    @handle_error
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data: Dict[str, Any]):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(400, message=f"An item with that name already exists: {item.name}.")
        except SQLAlchemyError:
            abort(500, message=f"An error ocurred while inserting Item: {item_data}.")

        return item
