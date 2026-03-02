from functools import wraps
from flask import request, jsonify
from app.models.membership import Membership

def group_member_required(f):
  @wraps(f)
  def wrapper(current_user, group_id, *args, **kwargs):

    membership = Membership.query.filter(
      Membership.user_id == current_user.id,
      Membership.group_id == group_id
    ).first()

    if not membership:
      return jsonify({"error": "User is not a member of this group"}), 403

    return f(current_user, group_id, *args, **kwargs)
  
  return wrapper

def group_admin_required(f):
  @wraps(f)

  def wrapper(current_user, group_id, *args, **kwargs):
    membership = Membership.query.filter(
      Membership.user_id == current_user.id,
      Membership.group_id == group_id
    ).first()

    if not membership:
      return jsonify({"error": "User is not a member of this group"}), 403

    if membership.role != "admin":
      return jsonify({"error": "User is not an admin of this group"}), 403
    
    return f(current_user, group_id, *args, **kwargs)
  
  return wrapper