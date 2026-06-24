from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import database

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/friends', methods=['GET'])
@login_required
def view_friends():
    friends = database.get_friends_list(current_user.id)
    pending_requests = database.get_pending_requests(current_user.id)
    return render_template('friends.html',friends=friends,pending=pending_requests)

@friends_bp.route('/friends/add', methods=['POST'])
@login_required
def add_friend():
    email_input = request.form.get('friend_email', '').strip()
    
    status = database.send_friend_request(current_user.id, email_input)
    
    if status == "Self":
        flash("You can't send a friend request to yourself.", "danger")
    else:
        flash(f"Friend request sent if that email is registered", "success") 
    return redirect(url_for('friends.view_friends'))

@friends_bp.route('/friends/accept/<int:id>', methods=['POST'])
@login_required
def accept_friend(id):
    status = database.accept_friend_request(id,current_user.id)
    if status == "Success":
        flash("Friend request accepted!")
    else:
        flash("Could not accept request")
    return redirect(url_for('friends.view_friends'))

@friends_bp.route('/friends/remove/<int:friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    success = database.remove_friend(current_user.id, friend_id)
    if success:
        flash("Friend removed.", "info")
    else:
        flash("Could not remove friend.", "danger")
    return redirect(url_for('friends.view_friends'))

@friends_bp.route('/friends/reject/<int:id>', methods=['POST'])
@login_required
def reject_friend(id):
    success = database.reject_friend_request(id, current_user.id)
    if success:
        flash("Friend request declined.", "info")
    else:
        flash("Request not found.", "danger")
    return redirect(url_for('friends.view_friends'))
    
    flash("Friend request declined.", "info")
    return redirect(url_for('friends.view_friends'))