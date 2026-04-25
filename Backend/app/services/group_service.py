from app.extensions import db
from app.models.group import Group
from app.models.membership import Membership
from app.models.user import User


def create_group(name, description, creator_user_id):
  if not name:
    return {"error": "Group name cannot be empty"}
  new_group = Group(name=name, created_by=creator_user_id)
  new_membership = Membership(user_id=creator_user_id, role="admin")
  new_group.memberships.append(new_membership)
  db.session.add(new_group)
  db.session.commit()
  return {"group_id": new_group.id, "name": new_group.name}


def get_user_groups(user_id):
  memberships = Membership.query.filter(Membership.user_id == user_id).all()
  groups = []
  for m in memberships:
    group = Group.query.get(m.group_id)
    if group:
      groups.append({"group_id": group.id, "name": group.name, "role": m.role})
  return {"groups": groups}


def get_group_details(group_id):
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}
  members = []
  for m in group.memberships:
    user = User.query.get(m.user_id)
    if user:
      members.append({"user_id": user.id, "username": user.username, "role": m.role})
  return {"group_id": group.id, "name": group.name, "members": members}


def rename_group(group_id, new_name, description=None):
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}
  if not new_name:
    return {"error": "Group name cannot be empty"}
  group.name = new_name
  db.session.commit()
  return {"group_id": group.id, "name": group.name}


def delete_group(group_id):
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}
  db.session.delete(group)
  db.session.commit()
  return {"message": "Group deleted successfully"}


def add_user_to_group(group_id, user_id, role="member"):
  if role not in ["member", "admin"]:
    return {"error": "Invalid role"}
  group = Group.query.get(group_id)
  if not group:
    return {"error": "Group not found"}
  user = User.query.get(user_id)
  if not user:
    return {"error": "User not found"}
  existing = Membership.query.filter(
    Membership.group_id == group_id,
    Membership.user_id == user_id
  ).first()
  if existing:
    return {"error": "User is already a member"}
  new_membership = Membership(user_id=user_id, group_id=group_id, role=role)
  db.session.add(new_membership)
  db.session.commit()
  return {"user_id": user_id, "group_id": group_id, "role": role}


def remove_user_from_group(group_id, user_id):
  membership = Membership.query.filter(
    Membership.group_id == group_id,
    Membership.user_id == user_id
  ).first()
  if not membership:
    return {"error": "User is not a member"}
  if membership.role == "admin":
    admins = Membership.query.filter(
      Membership.group_id == group_id,
      Membership.role == "admin"
    ).all()
    if len(admins) == 1:
      return {"error": "Cannot remove the last admin"}
  db.session.delete(membership)
  db.session.commit()
  return {"message": "Member removed successfully"}


def change_member_role(group_id, user_id, new_role):
  if new_role not in ["member", "admin"]:
    return {"error": "Invalid role"}
  membership = Membership.query.filter(
    Membership.group_id == group_id,
    Membership.user_id == user_id
  ).first()
  if not membership:
    return {"error": "User is not a member"}
  if membership.role == "admin" and new_role != "admin":
    admins = Membership.query.filter(
      Membership.group_id == group_id,
      Membership.role == "admin"
    ).all()
    if len(admins) == 1:
      return {"error": "Cannot demote the last admin"}
  membership.role = new_role
  db.session.commit()
  return {"user_id": user_id, "group_id": group_id, "role": new_role}

