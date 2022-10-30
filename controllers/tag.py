from typing import Dict, Any

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from controllers.utils import handle_error
from db import db
from models import StoreModel, TagModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

from schemas import TagSchema

blp = Blueprint("Tags", "tags", description="Operations on tags")


@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):

    @blp.response(200, TagSchema(many=True))
    def get(self, store_id: str):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data: Dict[str, Any], store_id: str):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message=f"A tag with name {TagModel.name} already exists in store {store_id}.")
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @jwt_required()
    @blp.response(201, TagSchema)
    @handle_error
    def post(self, item_id: str, tag_id: str):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message=f"An error ocurred while inserting tag {tag_id} in item {item_id}.")

        return tag

    @jwt_required()
    @handle_error
    def delete(self, item_id: str, tag_id: str):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message=f"An error ocurred while inserting tag {tag_id} in item {item_id}.")

        return {"message": f"Item {item_id} removed from tag {tag_id}"}


@blp.route("/tag/<string:tag_id>")
class Tags(MethodView):

    @blp.response(200, TagSchema)
    @handle_error
    def get(self, tag_id: str):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @jwt_required()
    @blp.response(202,
                  description="Deletes a tag if no item is tagged with it.",
                  example={"message": "Tag deleted."})
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items. In this case"
                                       ", the tag is not deleted.")
    @handle_error
    def delete(self, tag_id: str):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": f"tag {tag_id} deleted."}
        abort(400, message="Could not delete tag. Make sure that tag is not associated with any items,"
                           "the try again!")
