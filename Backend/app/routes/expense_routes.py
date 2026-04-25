"""
POST   /groups/<group_id>/expenses              - Create a new expense
GET    /groups/<group_id>/expenses              - Get all expenses in a group
GET    /groups/<group_id>/expenses/<id>         - Get a single expense
PUT    /groups/<group_id>/expenses/<id>         - Update an expense (creator only)
DELETE /groups/<group_id>/expenses/<id>         - Delete an expense (admin only)
"""

from flask import Blueprint, request, jsonify
from app.utils.auth_decorator import token_required
from app.utils.group_authorisation import group_member_required, group_admin_required

from app.services import expense_service

expense_bp = Blueprint("expenses", __name__)

@expense_bp.route("/groups/<int:group_id>/expenses", methods=["POST"])
@token_required
@group_member_required
def create_expense(current_user, group_id):
  data = request.get_json(silent=True)

  if not data:
    return jsonify({"message": "Invalid JSON data"}), 400

  description = data.get("description")
  amount = data.get("amount")
  splits = data.get("splits")

  if not description or not amount or not splits:
    return jsonify({"message": "Description, amount and splits are required"}), 400
  
  result = expense_service.create_expense(
    group_id = group_id,
    creator_user = current_user,
    description = description,
    total_amount = amount,
    splits = splits
    )

  if "error" in result:
    return jsonify({"message": result["error"]}), 400
  
  return jsonify({"message": "Expense created successfully", "expense_id": result["expense_id"]}), 201

@expense_bp.route("/groups/<int:group_id>/expenses", methods=["GET"])
@token_required
@group_member_required
def get_expenses(current_user, group_id):
  expenses = expense_service.get_group_expenses(group_id)
  if "error" in expenses:
    return jsonify({"message": expenses["error"]}), 400
  
  return jsonify({"expenses": expenses["expenses"]}), 200

@expense_bp.route("/groups/<int:group_id>/expenses/<int:expense_id>", methods=["GET"])
@token_required
@group_member_required
def get_expense_details(current_user, group_id, expense_id):
  expense = expense_service.get_expense_details(expense_id)
  if "error" in expense:
    return jsonify({"message": expense["error"]}), 400
  
  return jsonify({"expense": expense}), 200

@expense_bp.route("/groups/<int:group_id>/expenses/<int:expense_id>", methods=["PUT"])
@token_required
@group_admin_required
def update_expense(current_user, group_id, expense_id):
  data = request.get_json(silent=True)

  if not data:
    return jsonify({"message": "Invalid JSON data"}), 400
  
  updated_expense = expense_service.update_expense(
    group_id = group_id,
    expense_id = expense_id,
    current_user = current_user,
    data = data
  )

  if "error" in updated_expense:
    return jsonify({"message": updated_expense["error"]}), 400
  
  return jsonify({"message": "Expense updated successfully", "expense": updated_expense}), 200

@expense_bp.route("/groups/<int:group_id>/expenses/<int:expense_id>", methods=["DELETE"])
@token_required
@group_admin_required
def delete_expense(current_user, group_id, expense_id):
  deleted_expense = expense_service.delete_expense(
    group_id = group_id,
    expense_id = expense_id,
  )

  if "error" in deleted_expense:
    return jsonify({"message": deleted_expense["error"]}), 400
  
  return jsonify({"message": "Expense deleted successfully"}), 200







