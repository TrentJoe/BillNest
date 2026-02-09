from app.extensions import db
from app.models.group import Group, Membership



def create_group(name, creator_user):
  # check name field is not empty
  if not name:
    raise ValueError("Group name cannot be empty")
  # create group and add creator as admin member
  new_group = Group(name = name, created_by = creator_user.id)
  new_membership = Membership(user_id = creator_user.id, role = "admin")
  # Add the new membership to the group's memberships relationship
  new_group.memberships.append(new_membership)
  db.session.add(new_group)
  db.session.commit()
  return new_group

def add_user_to_group(group, user, role = "member"):
  # check role is valid
  if role not in ["member", "admin"]:
    raise ValueError("Invalid role. Must be 'member' or 'admin'")

  # check if user is already a member of the group
  for membership in group.memberships:
    if membership.user_id == user.id:
      raise ValueError("User is already a member of the group")

  # add user to group with specified role
    new_membership = Membership(user_id = user.id, role = role)
    group.memberships.append(new_membership)
    db.session.commit()
  return new_membership
  

def remove_user_from_group(group, user):
  # find the membership for the user in the group
  membership = next(
    (m for m in group.memberships if m.user_id == user.id), 
    None
  )
  
  # check if the user is a member of the group
  if not membership:
    raise ValueError("User is not a member of the group")

  # check if the user is an admin and if there are other admins in the group
  if membership.role == "admin":
    admins = [m for m in group.memberships if role =="admin"]
    if len(admins) == 1:
      raise ValueError("Cannot remove the last admin from the group")

  # remove the membership
  db.session.delete(membership)
  db.session.commit()

  return True

def change_member_role(group, user, new_role):
  # check if new role is valid
  if new_role not in ["member", "admin"]:
    raise ValueError("Invalid role. Must be 'member' or 'admin'")

  membership = next(
    (m for m in group.memberships if m.user_id == user.id),
    None
  )
  # check if user is a member of the group
  if not in membership:
      raise ValueError("User is not a member of the group")

  # check if demoting an admin and if there are other admins in the group
  if membership.role =="admin" and new_role !="admin":
      admins = [m for m in group.memberships if m.role =="admin"]
    if len(admins) == 1:
      raise ValueError("Cannot demote the last admin in the group")

  # update the role
  membership.role = new_role
  db.session.commit()

  return membership

def get_user_groups(user):
  return [membership.group for membership in user.memberships]

