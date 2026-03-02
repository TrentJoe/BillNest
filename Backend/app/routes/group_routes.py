from flask import Blueprint, jsonify, request
from app.services import group_service
from app.utils.auth_decorator import token_required
from app.utils.group_authorisation import group_member_required, group_admin_required
from app.extensions import db
from app.models.group import Group
from app.models.membership import Membership
from app.models.user import User


group_bp = Blueprint("group", __name__)

@group_bp.route("/groups", methods=["GET"])
@token_required
def get_groups(current_user):

  memberships = Membership.query.filter(Membership.user_id == current_user.id).all()

  result = []
  for m in memberships:
    group = Group.query.get(m.group_id)
    result.append({
      "id":group.id,
      "name" : group.name,
      "role": m.role
    })
  return jsonify({"groups": result}), 200

@group_bp.route("/groups/<int:group_id>", methods = ["GET"])
@token_required
@group_member_required
def get_group_details(current_user, group_id):
  group = Group.query.get(group_id)

  if not group:
    return jsonify({"error": "Group not found"}), 404
  
  memberships = Membership.query.filter(Membership.group_id == group_id).all()

  members = []
  for m in memberships:
    user = User.query.get(m.user_id)
    members.append({
      "id": user.id,
      "name": user.name,
      "email": user.email,
      "role": m.role
    })

  return jsonify({
    "id": group.id,
    "name": group.name,
    "members": members
  }), 200


@group_bp.route("/groups", methods=["POST"])
@token_required
def create_group(current_user):
  data = request.get_json()
  name = data.get("name")
  description = data.get("description")

  if not name:
    return jsonify({"error": "Group name is required"}), 400

  new_group = Group(name=name, 
    description = description,
    created_by = current_user.id)
  db.session.add(new_group)
  db.session.flush()  # Flush to get the new group ID

  # Add creator as admin member
  membership = Membership(
    user_id = current_user.id,
    group_id = new_group.id,
    role = "admin"
  )

  db.session.add(membership)
  db.session.commit()

  return jsonify({
    "id": new_group.id,
    "name": new_group.name,
  }),201


@group_bp.route("/groups/<int:group_id>", methods=["PUT"])
@token_required
@group_admin_required
def rename_group(current_user, group_id):

  data = request.get_json()
  new_name = data.get("name")

  group = Group.query.get(group_id)

  if not group:
    return jsonify({"error": "Group not found"}), 404

  if new_name:
    group.name = new_name

  db.session.commit()

  return jsonify({
    "id": group.id,
    "name": group.name
  }), 200

@group_bp.route("/groups/<int:group_id>/members", methods = ["POST"])
@token_required
@group_admin_required
def add_member(current_user, group_id):
  data = request.get_json()
  email = data.get("email")

  if not email:
    return jsonify({"error": "Email is required"}), 400
  
  user = User.query.filter(User.email == email).first()

  if not user:
    return jsonify({"error": "User not found"}), 404
  
  existing_membership = Membership.query.filter(
    Membership.user_id == user.id,
    Membership.group_id == group_id
  ).first()

  if existing_membership:
    return jsonify({"error": "User is already a member of this group"}), 400

  new_membership = Membership(
    user_id = user.id,
    group_id = group_id,
    role = "member"
  )

  db.session.add(new_membership)
  db.session.commit()

  return jsonify({
    "message": f"{user.name} added to group successfully"}), 201

@group_bp.route("/groups/<int:group_id>/members/<int:user_id>", methods = ["DELETE"])
@token_required
@group_admin_required
def remove_member(current_user, group_id, user_id):

  membership = Membership.query.filter(
    Membership.user_id == user_id,
    Membership.group_id == group_id
  ).first()

  if not membership:
    return jsonify({"error": "Membership not found"}), 404
  
  db.session.delete(membership)
  db.session.commit()

  return jsonify({"message": "Member removed from group successfully"}), 200

@group_bp.route("/groups/<int:group_id>", methods = ["DELETE"])
@token_required
@group_admin_required
def delete_group(current_user, group_id):
  group = Group.query.get(group_id)

  if not Group:
    return jsonify({"error": "Group not found"}), 404

  db.session.delete(group)
  db.session.commit()

  return jsonify({"message": "Group deleted successfully"}), 200
  



