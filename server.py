"""Photo Spots."""

import os

from get_photos import (get_photos_by_location,
                        get_photo_location, get_photo_url)

from get_address import get_address_by_lat_lng

from photo_spots import (user_exists, correct_password, get_user, register_user,
                         log_out, get_user_by_id, get_photos_by_user, get_city,
                         is_saved)

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import City, User, Photo, connect_to_db, db


app = Flask(__name__)

app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined

google_maps_api_key = os.environ['GOOGLE_KEY']


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/user-login')
def user_login():
    """Render HTML template with login form."""

    return render_template("user-login.html")


@app.route('/user-login', methods=["POST"])
def handle_user_login():
    """Handles login for users."""

    user = get_user()

    if not user_exists(user):
        flash('Sorry, that email does not match our records.')
        return redirect("/user-login")

    if correct_password(user):
        return redirect("/user/" + str(user.user_id))
    else:
        return redirect("/user-login")


@app.route('/user-registration', methods=["POST"])
def handle_user_registration():
    """Handles login and registration for new users."""

    user = get_user()

    if not user_exists(user):
        new_user = register_user()
        return redirect("/user/" + str(new_user.user_id))
    else:
        flash('Sorry, that email is already registered. Please log in or create a new account.')
        return redirect("/")


@app.route('/user-logout')
def logout():
    """Remove user_id from session and redirect to the home page."""

    log_out()

    return redirect("/user-login")


@app.route('/user/<user_id>')
def user_page(user_id):
    """Show user profile."""

    current_user = get_user_by_id(user_id)

    saved_photos_info = get_photos_by_user(user_id)

    return render_template("user-profile.html",
                           current_user=current_user,
                           saved_photos_info=saved_photos_info
                           )


@app.route('/search-results')
def search_city():
    """Return photo results from city search."""

    city = get_city()

    if city is not None:
        name = city.name
        session['city_name'] = name
        lat = city.lat
        lng = city.lng
        city_id = city.city_id
        url_pairs = get_photos_by_location(lat, lng)

    else:
        name = None
        url_pairs = None
        city_id = None

    return render_template("search-results.html",
                           name=name,
                           url_pairs=url_pairs,
                           city_id=city_id)


@app.route('/photo-details/<photo_id>')
def show_photo_and_location(photo_id):
    """Show photo and location details."""

    img_src = get_photo_url(photo_id)

    location_details = get_photo_location(photo_id)

    lat = location_details['lat']
    lng = location_details['lng']

    address = get_address_by_lat_lng(lat, lng)

    saved = is_saved(photo_id)

    return render_template("photo-details.html",
                           img_src=img_src,
                           photo_id=photo_id,
                           lat=lat,
                           lng=lng,
                           address=address,
                           google_maps_api_key=google_maps_api_key,
                           saved=saved)


@app.route('/save-photo', methods=["POST"])
def save_photo():
    """Saves photo to database."""

    img_src = request.form.get("src")
    photo_id = request.form.get("id")
    city_id = City.query.filter(City.name == session['city_name']).one().city_id
    user_id = session['user_id']

    print "city id is: ", city_id

    new_photo = Photo(img_src=img_src, photo_id=photo_id, city_id=city_id, user_id=user_id)
    db.session.add(new_photo)
    db.session.commit()

    return "OK"


@app.route('/remove-photo', methods=["POST"])
def remove_photo():
    """Removes photo from database."""

    photo_id = request.form.get("id")
    user_id = session['user_id']

    photo = Photo.query.filter(Photo.photo_id == photo_id, Photo.user_id == user_id).first()
    db.session.delete(photo)
    db.session.commit()

    return "OK"

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
