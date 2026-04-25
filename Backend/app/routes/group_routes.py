"""
POST   /groups                          - Create a group
GET    /groups                          - Get all groups for current user
GET    /groups/<group_id>               - Get group details
PUT    /groups/<group_id>               - Rename a group (admin only)
DELETE /groups/<group_id>               - Delete a group (admin only)
POST   /groups/<group_id>/members       - Add a member (admin only)
DELETE /groups/<group_id>/members/<id>  - Remove a member (admin only)
"""

from flask import Blueprint, jsonify, request
from app.services import group_service
from app.utils.auth_decorator import token_required
from app.utils.group_authorisation import group_member_required, group_admin_required


group_bp = Blueprint("group", __name__)

@group_bp.route("/groups", methods=["GET"])
@token_required
def get_groups(current_user):

  groups = group_service.get_user_groups(current_user.id)

  if "error" in groups:
    return jsonify({"message": groups["error"]}), 400
  
  return jsonify({"groups": groups["groups"]}), 200

@group_bp.route("/groups/<int:group_id>", methods = ["GET"])
@token_required
@group_member_required
def get_group_details(current_user, group_id):
  group_details = group_service.get_group_details(group_id)

  if "error" in group_details:
    return jsonify({"message": group_details["error"]}), 400

  return jsonify({
    "id": group_details["group_id"],
    "name": group_details["name"],
    "members": group_details["members"]
  }), 200


@group_bp.route("/groups", methods=["POST"])
@token_required
def create_group(current_user):
  data = request.get_json(silent=True)
  if not data:
    return jsonify({"error": "Invalid JSON data"}), 400
  
  name = data.get("name")
  description = data.get("description")

  if not name:
    return jsonify({"error": "Group name is required"}), 400

  new_group = group_service.create_group(
    name = name,
    description = description,
    creator_user_id = current_user.id
  )

  if "error" in new_group:
    return jsonify({"error": new_group["error"]}), 400

  return jsonify({
    "id": new_group["group_id"],
    "name": new_group["name"],
  }),201


@group_bp.route("/groups/<int:group_id>", methods=["PUT"])
@token_required
@group_admin_required
def rename_group(current_user, group_id):

  data = request.get_json(silent=True)
  if not data:
    return jsonify({"error": "Invalid JSON data"}), 400
  new_name = data.get("name")
  description = data.get("description")

  if not new_name:
    return jsonify({"error": "Group name is required"}), 400
  
  group = group_service.rename_group(group_id, new_name, description)

  if "error" in group:
    return jsonify({"error": group["error"]}), 400

  return jsonify({
    "id": group["group_id"],
    "name": group["name"]
  }), 200

@group_bp.route("/groups/<int:group_id>/members", methods = ["POST"])
@token_required
@group_admin_required
def add_member(current_user, group_id):
  data = request.get_json(silent=True)
  if not data:
    return jsonify({"error": "Invalid JSON data"}), 400

  user_id = data.get("user_id")
  if not user_id:
    return jsonify({"error": "User ID is required"}), 400
  
  role = data.get("role", "member")
  
  result = group_service.add_user_to_group(group_id, user_id, role)

  if "error" in result:
    return jsonify({"error": result["error"]}), 400

  return jsonify({"message": "Member added to group successfully"}), 201

@group_bp.route("/groups/<int:group_id>/members/<int:user_id>", methods = ["DELETE"])
@token_required
@group_admin_required
def remove_member(current_user, group_id, user_id):

  result = group_service.remove_user_from_group(group_id, user_id)

  if "error" in result:
    return jsonify({"error": result["error"]}), 400

  return jsonify({"message": "Member removed from group successfully"}), 200

@group_bp.route("/groups/<int:group_id>", methods = ["DELETE"])
@token_required
@group_admin_required
def delete_group(current_user, group_id):
  group = group_service.delete_group(group_id)

  if "error" in group:
    return jsonify({"error": group["error"]}), 400 

  return jsonify({"message": "Group deleted successfully"}), 200
  



