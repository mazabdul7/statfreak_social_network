'''Code by Mazin Abdulmahmood, Paul Ho, Ben Li'''
from flask import render_template, request, redirect, flash, url_for
from flask import Blueprint
from flask_login.utils import login_required
from flask_login import current_user
from statfreak.models import Wellbeing, Profile, Area
from statfreak import db
from django.db import IntegrityError
import json
from functools import wraps
from datetime import datetime
import requests
from flask import request

main_bp = Blueprint('main', __name__)


def profile_required(f):
    '''Custom decorator to ensure the user has a profile connected to their
        account in order to access the websites functionalities. Prevents errors.'''
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if Profile.query.filter_by(user_id=current_user.id).first() is None:
            flash("Please create a profile to access site functionality", "warning")
            return redirect(url_for('community.create_profile'))

        return f(*args, **kwargs)

    return decorated_function


@main_bp.route('/')
def index():
    '''Generates community borough rankings based on wellbeing entries
        of users. Averages happiness, satisfaction and anxiety for each
        borough. Rating factor equals (happiness + satisfaction)/(anxiety).
        Returns sorted rankings dictionary'''
    if not current_user.is_anonymous:
        if Profile.query.filter_by(user_id=current_user.id).first() is None:
            flash("Please create a profile to access site functionality", "warning")
            return redirect(url_for('community.create_profile'))

    area_list = list(area.area_name for area in Area.query.all())

    ratings = dict.fromkeys(area_list, {"happiness": 0,
                                        "satsifaction": 0,
                                        "anxiety": 0,
                                        "rating_factor": 0,
                                        "position": 0})

    for area in area_list:
        user_wellbeing = Wellbeing.query.filter_by(location=area).all()

        if user_wellbeing:
            hapstat = []
            satstat = []
            anxstat = []
            for entry in user_wellbeing:
                hapstat.append(int(entry.happiness))
                satstat.append(int(entry.satisfaction))
                anxstat.append(int(entry.anxiety))

                avghap = int(round(sum(hapstat)/len(hapstat)))
                avgsat = int(round(sum(satstat)/len(satstat)))
                avganx = int(round(sum(anxstat)/len(anxstat)))

            ratings[area] = {"happiness": avghap,
                             "satisfaction": avgsat,
                             "anxiety": avganx,
                             "rating_factor": round((avghap+avgsat)/(avganx), 3),
                             "position": 0}

    sorted_ratings = dict(sorted(
        ratings.items(), key=lambda item: item[1]["rating_factor"], reverse=True))

    counter = 0
    for rating in sorted_ratings:
        counter += 1
        sorted_ratings[rating]["position"] = counter

    if request.args.get('api_status'):
        api_status = True
    else:
        api_status = False

    return render_template('index.html', ratings=sorted_ratings, api=api_status)


@main_bp.route('/distance_api', methods=['GET', 'POST'])
@login_required
@profile_required
def distance_api():
    '''Distance and time between destinations API through Google Maps
    Error handling applied for no result from contacting API. 
    returns flash of result of API '''
    if request.method == 'POST':
        api_key = 'AIzaSyDoFdnL3N1G7fW-nJLXoUXTctZm5EsRX_w'
        start = request.form['text1']
        end = request.form['text2']
        city = 'london'
        urlbase = 'https://maps.googleapis.com/maps/api/distancematrix/json?&'
        url = urlbase + 'origins=' + start + city + '&destinations=' + \
            end + city + '&mode=car' + '&key=' + api_key

        output = requests.get(url).json()
        if output:
            for obj in output['rows']:
                for data in obj['elements']:
                    result = 'The distance between ' + start + ' and ' + end + ' is ' + \
                        data['distance']['text'] + ' which will take you ' + \
                        data['duration']['text']+' travelling by car.'
                    flash(result, 'success')
                    return redirect(url_for('main.index', api_status=True))
        else:
            flash('An error occured while contacting the API', 'danger')
            return redirect(url_for('main.index'))
    
    return redirect(url_for('main.index'))


@main_bp.route('/wellbeing', methods=['GET', 'POST'])
@login_required
@profile_required
def wellbeing():
    '''Wellbeing page that allows user to track their wellbeing over entries
        returns jsonified data to feed to chart.js for plotting of data
        returns cooldown boolean if last entry made within 24 hr restrtiction'''

    entries = Wellbeing.query.filter_by(user_id=current_user.id).all()

    hapstat = []
    satstat = []
    anxstat = []
    labels = []
    notes = []
    i = 0
    cooldown = False
    last_post_time = None

    for entry in entries:
        hapstat.append(int(entry.happiness))
        satstat.append(int(entry.satisfaction))
        anxstat.append(int(entry.anxiety))
        labels.append(str(entry.created_at.strftime('%m/%d/%Y, %H:%M:%S')))
        notes.append([i, entry.notes])
        i += 1

    if entries:
        #Calculate time since last post for cooldown period to avoid spam entries altering rankings
        last_post = Wellbeing.query.filter_by(user_id=current_user.id).all()
        last_post_time = int(
            last_post[len(last_post)-1].created_at.strftime('%d'))
        time_now = int(datetime.now().strftime('%d'))
        if time_now - last_post_time >= 1:
            cooldown = False
        elif time_now - last_post_time < 1:
            cooldown = True
        last_post_time = last_post[len(
            last_post)-1].created_at.strftime('%m/%d/%Y, %H:%M:%S')

    if request.method == 'POST':
        happy = request.form['happy']
        satisfied = request.form['satisfied']
        anxiety = request.form['anxiety']
        notes = request.form['notes']

        profile = Profile.query.filter_by(user_id=current_user.id).first()
        entry = Wellbeing(happiness=happy, satisfaction=satisfied, anxiety=anxiety,
                          notes=notes, user_id=current_user.id, location=profile.area)

        try:
            db.session.add(entry)
            db.session.commit()
            flash("Entry successfully entered", "success")
        except IntegrityError:
            db.session.rollback()
            flash("An error occured when registering the entry", 'error')

        return redirect(url_for('main.wellbeing'))

    return render_template('wellbeing_quiz.html', a=json.dumps(hapstat), b=json.dumps(satstat), c=json.dumps(anxstat), label=json.dumps(labels), notes=notes,
                           label_normal=labels, cooldown=cooldown, last_post=last_post_time)
