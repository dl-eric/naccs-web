from flask import Blueprint, render_template, session, jsonify, abort, url_for, redirect, flash
from db import db, School
from forms import SchoolForm


schools_page = Blueprint('schools', __name__, url_prefix='/schools', template_folder='templates')

@schools_page.route('/', methods=['get', 'post'])
def schools():
    form = SchoolForm()
    
    if form.validate_on_submit():
        # Check if valid school
        school = School.query.filter(School.name == form.name.data).first()
        if school == None:
            flash('School not found', 'error')
            return render_template("schools/schools.html", username=session.get('username'), form=form)

        abbrev = school.abbrev
        return redirect(url_for('schools.school', abbrev=abbrev))

    return render_template("schools/schools.html", username=session.get('username'), form=form)

@schools_page.route('/<abbrev>', methods=['get'])
def school(abbrev):
    # Check if school exists
    school = School.query.filter(School.abbrev == abbrev).first()
    if school == None:
        abort(404)

    return render_template("schools/school.html", username=session.get('username'), school=school)   

@schools_page.route('schoolsjson', methods=['get'])
def get_json():
    results = [] 
    for school in School.query.order_by(School.name).all():
        results.append(school.serialize)
    return jsonify(results)