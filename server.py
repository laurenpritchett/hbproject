"""Photo Spots."""

import os

from get_photos import (get_photos_by_location,
                        get_photo_location, get_photo_url)

from get_address import get_address_by_lat_lng, get_lat_lng_by_city

from photo_spots import (user_exists, correct_password, get_user_by_email,
                         register_user, get_user_by_id, get_photos_by_user,
                         is_saved, save_photo_spot, remove_photo_spot,
                         )

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, flash,
                   session, request)

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db


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

    email = request.form.get("email")
    password = request.form.get("password")
    user = get_user_by_email(email)

    if not user_exists(user):
        flash('Sorry, that email does not match our records.')
        return redirect("/user-login")

    if correct_password(user, password):
        session['user_id'] = user.user_id
        session['name'] = user.first_name
        flash('Welcome back!')
        return redirect("/user/" + str(user.user_id))
    else:
        flash('Incorrect password provided.')
        return redirect("/user-login")


@app.route('/user-registration', methods=["POST"])
def handle_user_registration():
    """Handles login and registration for new users."""

    user_info = request.form

    user = get_user_by_email(user_info['email'])

    if not user_exists(user):
        new_user = register_user(user_info)
        session['user_id'] = new_user.user_id
        session['name'] = new_user.first_name
        flash('Welcome to Photo Spots!')
        return redirect("/user/" + str(new_user.user_id))
    else:
        flash('Sorry, that email is already registered. Please log in or create a new account.')
        return redirect("/")


@app.route('/user-logout')
def logout():
    """Remove user_id from session and redirect to the home page."""

    del session['user_id']
    flash('See you later!')

    return redirect("/")


# TODO: optimize logic so that photos are divided by city
@app.route('/user/<user_id>')
def user_page(user_id):
    """Show user profile."""

    current_user = get_user_by_id(user_id)

    saved_photos_info = get_photos_by_user(user_id)

    return render_template("user-profile.html",
                           current_user=current_user,
                           saved_photos_info=saved_photos_info,
                           )


# TODO: paginate search results
@app.route('/search-results')
def search_city():
    """Return photo results from city search."""

    search = request.args.get('city-search')
    lat_lng = get_lat_lng_by_city(search)

    if lat_lng is not None:
        name = search
        lat, lng = lat_lng
        url_pairs = get_photos_by_location(lat, lng)

    else:
        name = None
        url_pairs = None

    return render_template("search-results.html",
                           name=name,
                           url_pairs=url_pairs,
                           search=search,
                           )


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
                           saved=saved,
                           )


@app.route('/save-photo', methods=["POST"])
def save_photo():
    """Saves photo to database."""

    img_src = request.form.get("src")
    photo_id = request.form.get("id")
    user_id = session['user_id']

    save_photo_spot(img_src, photo_id, user_id)

    return "OK"


@app.route('/remove-photo', methods=["POST"])
def remove_photo():
    """Removes photo from database."""

    photo_id = request.form.get("id")
    user_id = session['user_id']

    remove_photo_spot(photo_id, user_id)

    return "OK"

if __name__ == "__main__":
    app.debug = False
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app, os.environ.get("DATABASE_URL"))
    DEBUG = "NO_DEBUG" not in os.environ

    PORT = int(os.environ.get("PORT", 5000))
    app.run(port=PORT, host='0.0.0.0', debug=DEBUG)
