from flask import Blueprint, render_template, session, jsonify, abort, url_for, redirect, flash
from auth import login_required, flash_errors
from forms import CreateTeamForm, JoinTeam, LeaveTeamForm, ConfirmForm
import functools
from db import db, Teams, Players
from passlib.hash import bcrypt_sha256
from warrant import Cognito
from warrant.aws_srp import AWSSRP
import os
import copy

teams_page = Blueprint('teams', __name__, url_prefix='/teams', template_folder='templates')

AWS_COGNITO_POOL_ID     = os.environ.get('AWS_COGNITO_POOL_ID')
AWS_COGNITO_CLIENT_ID   = os.environ.get('AWS_COGNITO_CLIENT_ID')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # TODO: We should be doing check_token for this routine
        if 'access_token' not in session:
            flash("You must be logged in to see that!", "error")
            return redirect(url_for('auth_page.signin'))

        return view(**kwargs)

    return wrapped_view



@teams_page.route('/' , methods=['get', 'post'])
def teams():
    # Fetches the currently registered teams.
    teams = Teams.query.order_by(Teams.team_id.desc()).all()
    player_check = Players.query.filter(Players.name == session.get('username')).first()
    return render_template("teams/teams.html", teams=teams, player_check=player_check)

@teams_page.route('/rules')
@login_required
def rules():
    return render_template('rules.html')

def is_ready(players):
    mplayers = players
    count = 0
    for player in mplayers:
        if player.paid:
            count += 1
        if count >= 5:
            return True
    return False

@teams_page.route('/<name>', methods=['post', 'get'])
def team(name):
    id_token        = session.get('id_token')
    refresh_token   = session.get('refresh_token')
    access_token    = session.get('access_token')
    auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, id_token=id_token, refresh_token=refresh_token, access_token=access_token, access_key='dummy', secret_key='dummy')
    try:
        if auth.check_token():
            session['id_token']         = auth.id_token
            session['access_token']     = auth.access_token
    except Exception as e:
        # Something went wrong. Log out the user.
        print(e)
        return redirect(url_for('auth_page.signout'))
    user = auth.client.get_user(AccessToken=session.get('access_token'))
    user = auth.get_user_obj(username=user['Username'], attribute_list=user['UserAttributes'], attr_map={"custom:discord":"discord", "custom:esea":"esea"})
    # Check if team exists
    team = Teams.query.filter(Teams.name == name).first()
    players_query = db.engine.execute('SELECT * FROM `players` WHERE players.team_id = '+ str(team.team_id) +'')
    players = copy.deepcopy(list(players_query))
    p = Players.query.filter(Players.name == session.get('username')).first()
    ready = is_ready(players)
  
    if name == None:
        abort(404)
    form = JoinTeam()
    if form.validate_on_submit():
        password = db.engine.execute('SELECT * FROM `teams` WHERE team_id ='+ str(team.team_id) +'')
        for row in password:
            if bcrypt_sha256.verify(form.password.data, row['password']):
                already_on_team = Players.query.filter(Players.name == session.get('username')).first()
                already_leader = Players.query.filter(Teams.leader == session.get('username')).count()
                #if player isnt in players table it will create a new row for the player
                if already_on_team == None:
                    new_post = Players(session.get('username'), 'null', team.team_id, 'false', user.esea)
                    db.session.add(new_post)
                    db.session.commit()
                    flash('You have joined the team', 'success')
                    return redirect(url_for('teams.teams'))
                if already_on_team.team_id != 0:
                    flash('You are already on a team.', 'error')
                    return redirect(url_for('teams.teams'))
                if already_leader > 0:
                    flash('You are already the leader of a team.', 'error')
                    return redirect(url_for('teams.teams'))
                #if player is in the table then it will just update their team id to the team they joined
                else:
                    already_on_team.team_id = team.team_id
                    db.session.commit()
                    flash('You have joined the team', 'success')
                    return redirect(url_for('teams.teams'))
            else:
                flash('The password you entered is incorrect!', 'error')
                return redirect(url_for('teams.teams'))
    lform = LeaveTeamForm()
    if lform.validate_on_submit():
        return redirect(url_for('teams.leaveconfirm'))

    return render_template("teams/team.html", username=session.get('username'), team=team, players=players, form=form, lform=lform, p=p, ready=ready)

@teams_page.route('/createteam', methods=['post', 'get'])
@login_required
def create():
    id_token        = session.get('id_token')
    refresh_token   = session.get('refresh_token')
    access_token    = session.get('access_token')
    auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, id_token=id_token, refresh_token=refresh_token, access_token=access_token, access_key='dummy', secret_key='dummy')
    try:
        if auth.check_token():
            session['id_token']         = auth.id_token
            session['access_token']     = auth.access_token
    except Exception as e:
        # Something went wrong. Log out the user.
        print(e)
        return redirect(url_for('auth_page.signout'))
    user = auth.client.get_user(AccessToken=session.get('access_token'))
    user = auth.get_user_obj(username=user['Username'], attribute_list=user['UserAttributes'], attr_map={"custom:discord":"discord", "custom:esea":"esea"})
    player_check = Teams.query.filter(Players.name == session.get('username')).count()
    form = CreateTeamForm()
    if form.validate_on_submit():
        team = Teams.query.filter(Teams.name == form.teamname.data).count()
        leader_check = Teams.query.filter(Teams.leader == session.get('username')).count()
        player_check = Players.query.filter(Players.name == session.get('username')).count()
        #Checks if team name is taken.
        if team > 0:
            flash('This name already exists. Please Choose another.', 'error')
            return redirect(url_for('teams.create'))
        #Only one account per leader.
        elif leader_check > 0:
            flash('You cannot create more than one team.', 'error')
            return redirect(url_for('teams.create'))
        elif player_check == 0:
            enc_pass = bcrypt_sha256.hash(form.password.data)
            new_post = Teams(form.school.data, form.teamname.data, form.teamtype.data, session.get('username'), enc_pass)
            db.session.add(new_post)
            db.session.commit()
            team1 = Teams.query.filter(Teams.name == form.teamname.data).first()
            new_player = Players(session.get('username'), form.school.data, team1.team_id, 'false', user.esea)
            db.session.add(new_player)
            db.session.commit()
            flash('Your team has been successfully created!', 'success')
            return redirect(url_for('teams.teams'))
        else:
            players = Players.query.filter(Players.name == session.get('username')).first()
            enc_pass = bcrypt_sha256.hash(form.password.data)
            new_post = Teams(form.school.data, form.teamname.data, form.teamtype.data, session.get('username'), enc_pass)
            db.session.add(new_post)
            db.session.commit()
            tid = Teams.query.filter(Teams.name == form.teamname.data).first()
            players.team_id = tid.team_id
            db.session.commit()
            flash('Your team has been successfully created!', 'success')
            return redirect(url_for('teams.teams'))
    else:
        flash_errors(form)
    return render_template('teams/createteam.html', form = form, username=session.get('username'))

@teams_page.route('/leaveconfirm', methods=['post', 'get'])
@login_required
def leaveconfirm():
    form = ConfirmForm()
    if form.validate_on_submit():
        if form.accept.data == True:
            hi = Players.query.filter(Players.name == session.get('username')).first()
            user = Players.query.filter(Players.name == session.get('username')).first()
            leader = Teams.query.filter(Teams.leader == session.get('username')).first()
            if user == None:
                flash('You are not currently on a team.', 'error')
                return redirect(url_for('teams.teams'))
            # if statement checking whether theyre a leader (if theyre leader delete the team theyre a leader of)
            # set the ids of all users that were on the team to null or 0
            elif leader != None:
                players = Teams.query.filter(Teams.leader == session.get('username')).first()
                teamid = players.team_id
                curr_players = Players.query.filter(Players.team_id == teamid).all()
                #players are removed from database when leader leaves. since theyre not on a team anymore
                for i in curr_players:
                    i.team_id = 0
                    db.session.commit()
                user.team_id = 0
                db.session.delete(leader)
                db.session.commit()
                flash('You have successfully left your team (Your team was deleted!).', 'success')
                return redirect(url_for('teams.teams'))
            else:
                #player is not leader and is just leaving his team.
                user.team_id = 0
                db.session.commit()
                flash('You have successfully left your team.', 'success')
                return redirect(url_for('teams.teams'))
        elif form.accept.data == False:
            flash('You must accept to leave your team.', 'error')
            return redirect(url_for('teams.teams'))
        else:
            return redirect(url_for('teams.teams'))
    return render_template('teams/confirm.html', form = form)
