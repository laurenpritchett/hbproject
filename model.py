from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


################################################################################
# Model definition

class City(db.Model):
    """City with location information."""

    __tablename__ = "cities"

    city_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(33), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(32), nullable=False)
    iso2 = db.Column(db.String(3), nullable=False)
    province = db.Column(db.String(43), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<City id=%s name=%s country=%s>" % (self.city_id, self.name, self.country)

    @classmethod
    def by_id(cls, city_id):
        return cls.query.filter_by(city_id=city_id).first()


class User(db.Model):
    """User of photo spots website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

    @classmethod
    def by_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()


class UserCity(db.Model):
    """Middle table for User and City relationship."""

    __tablename__ = "users_cities"

    users_cities_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'))
    city_id = db.Column(db.Integer,
                        db.ForeignKey('cities.city_id'))
    photo_id = db.Column(db.String(200),
                         db.ForeignKey('photos.photo_id'))

    user = db.relationship("User",
                           backref=db.backref("users_cities",
                                              order_by=users_cities_id))

    city = db.relationship("City",
                           backref=db.backref("users_cities",
                                              order_by=users_cities_id))

    photo = db.relationship("Photo",
                            backref=db.backref("users_cities",
                                               order_by=users_cities_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<UserCity users_cities_id=%s user=%s city=%s>" % (self.users_cities_id,
                                                                  self.user_id,
                                                                  self.city_id)

    @classmethod
    def by_id(cls, users_cities_id):
        return cls.query.filter_by(users_cities_id=users_cities_id).first()


class Photo(db.Model):
    """Photo saved by a user."""

    __tablename__ = "photos"

    photo_id = db.Column(db.String(200), primary_key=True)
    img_src = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Photo photo_id=%s img_src=%s>" % (self.photo_id, self.img_src)

    @classmethod
    def by_id(cls, photo_id):
        return cls.query.filter_by(photo_id=photo_id).first()


################################################################################
# Helper functions

def connect_to_db(app, db_uri='postgresql:///hbproject'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


def example_data():
    """Create some sample data."""

    paris = City(name='Paris',
                 lat=48.86669293,
                 lng=2.333335326,
                 country='France',
                 iso2='FR',
                 province='Ile-de-France')
    tokyo = City(name='Tokyo',
                 lat=35.68501691,
                 lng=139.7514074,
                 country='Japan',
                 iso2='JP',
                 province='Tokyo')
    seattle = City(name='Seattle',
                   lat=47.57000205,
                   lng=-122.339985,
                   country='United States of America',
                   iso2='US',
                   province='Washington')

    karen = User(first_name='karen',
                 last_name='smith',
                 email='ksmith@gmail.com',
                 password='happy123')
    bob = User(first_name='bob',
               last_name='johnson',
               email='bjohnson@gmail.com',
               password='umbrella24')
    sally = User(first_name='sally',
                 last_name='smith',
                 email='ksmith@gmail.com',
                 password='happy123')

    db.session.add_all([paris, tokyo, seattle, karen, bob, sally])
    db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
