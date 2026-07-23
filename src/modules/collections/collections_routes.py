"""Collections routes — Instagram-style saved folders."""
from flask import Blueprint

from src.middlewares.auth_middleware import auth_required, onboarding_required
from src.shared.utils.api_response import success_response
from src.shared.utils.async_handler import async_handler
from src.modules.collections import collections_controller

collections_bp = Blueprint("collections", __name__)


def _ok(message, data, status=200):
    resp, _ = success_response(message, data, status)
    return resp, status


@collections_bp.get("")
@auth_required
@async_handler
def list_collections():
    data, status = collections_controller.list_for_me()
    return _ok("OK", data, status)


@collections_bp.post("")
@onboarding_required
@async_handler
def create_collection():
    data, status = collections_controller.create()
    return _ok("Collection created.", data, status)


@collections_bp.get("/<collection_id>")
@auth_required
@async_handler
def get_collection(collection_id):
    data, status = collections_controller.get_detail(collection_id)
    return _ok("OK", data, status)


@collections_bp.patch("/<collection_id>")
@onboarding_required
@async_handler
def rename_collection(collection_id):
    data, status = collections_controller.rename(collection_id)
    return _ok("Collection updated.", data, status)


@collections_bp.delete("/<collection_id>")
@onboarding_required
@async_handler
def delete_collection(collection_id):
    data, status = collections_controller.delete(collection_id)
    return _ok("Collection deleted.", data, status)


@collections_bp.post("/<collection_id>/items")
@onboarding_required
@async_handler
def add_item(collection_id):
    data, status = collections_controller.add_item(collection_id)
    return _ok("Added to collection.", data, status)


@collections_bp.delete("/<collection_id>/items/<target_type>/<target_id>")
@onboarding_required
@async_handler
def remove_item(collection_id, target_type, target_id):
    data, status = collections_controller.remove_item(collection_id, target_type, target_id)
    return _ok("Removed from collection.", data, status)
