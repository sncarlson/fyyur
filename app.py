# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

import sys

# from models import Artist, Venue, Show

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    from models import Venue

    # Done: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    areas = Venue.query.distinct('city', 'state').all()

    data = []

    for area in areas:
        venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
        record = {
            'city': area.city,
            'state': area.state,
            'venues': [venue.get_venue() for venue in venues],
        }
        data.append(record)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    from models import Venue
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()

    data = []
    for venue in venues:
        data.append(venue.search)

    response = {
        "count": len(venues),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    from models import Artist, Venue, Show, db
    from forms import Genre
    # shows the venue page with the given venue_id
    # Done: replace with real venue data from the venues table, using venue_id

    past_shows = []
    upcoming_shows = []
    now = datetime.now()

    venue = Venue.query.filter_by(id=venue_id).first_or_404()

    genreList = []

    for genre in venue.genres:
        genreList.append(Genre[genre])

    past_shows_query = db.session.query(Show, Artist) \
        .filter(Show.venue_id == venue.id) \
        .filter(Show.start_time < now) \
        .filter(Artist.id == Show.artist_id) \
        .all()

    for s, a in past_shows_query:
        past_shows.extend([{
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": a.image_link,
            "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M")
        }])

    upcoming_shows_query = db.session.query(Show, Artist) \
        .filter(Show.venue_id == venue.id) \
        .filter(Show.start_time > now) \
        .filter(Artist.id == Show.artist_id) \
        .all()

    for s, a in upcoming_shows_query:
        upcoming_shows.extend([{
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": a.image_link,
            "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M")
        }])

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genreList,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": venue.get_past_shows_count(),
        "upcoming_shows_count": venue.get_upcoming_shows_count(),
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    from models import Venue, db
    from forms import Genre
    # Done: insert form data as a new Venue record in the db, instead
    # Done: modify data to be the data object returned from db insertion

    error = False
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                genres=form.genres.data,
                website=form.website.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data

            )

            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            print("oops")
            abort(400)

    else:
        message = []
        for field, errors in form.errors.items():
            message.append(field + ': (' + '|'.join(errors) + ')')
        flash('The Venue data is not valid. Please try again!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    from models import Venue, db
    # Done: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        print("Venue deletion error")

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    from models import Artist

    data = Artist.query.order_by('id').all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    from models import Artist
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()

    data = []
    for artist in artists:
        data.append(artist.search)

    response = {
        "count": len(artists),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    from models import Artist, Venue, Show, db
    from forms import Genre
    # shows the venue page with the given venue_id
    # Done: replace with real venue data from the venues table, using venue_id
    past_shows = []
    upcoming_shows = []
    now = datetime.now()

    artist = Artist.query.filter_by(id=artist_id).first_or_404()

    genreList = []

    for genre in artist.genres:
        genreList.append(Genre[genre])

    past_shows_query = db.session.query(Show, Venue) \
        .filter(Show.artist_id == artist.id) \
        .filter(Show.start_time < now) \
        .filter(Venue.id == Show.venue_id) \
        .all()

    for s, v in past_shows_query:
        past_shows.extend([{
            "venue_id": v.id,
            "venue_name": v.name,
            "venue_image_link": v.image_link,
            "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M")
        }])

    upcoming_shows_query = db.session.query(Show, Venue) \
        .filter(Show.artist_id == artist.id) \
        .filter(Show.start_time > now) \
        .filter(Venue.id == Show.venue_id) \
        .all()

    for s, v in upcoming_shows_query:
        upcoming_shows.extend([{
            "venue_id": v.id,
            "venue_name": v.name,
            "venue_image_link": v.image_link,
            "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M")
        }])

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": genreList,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": artist.get_past_shows_count(),
        "upcoming_shows_count": artist.get_upcoming_shows_count(),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    from models import Artist

    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    form = ArtistForm(obj=artist)

    # Done: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    from models import Artist
    # Done: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error = False
    form = ArtistForm(request.form, meta={'csrf': False})

    artist = db.session.query(Artist).filter_by(id=artist_id).first()

    if form.validate():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.image_link = form.image_link.data
            artist.facebook_link = form.facebook_link.data
            artist.genres = form.genres.data
            artist.website = form.website.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. Artist ' + artist.name + ' could not be updated.')
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            print("oops")
            abort(400)

    else:
        message = []
        for field, errors in form.errors.items():
            message.append(field + ': (' + '|'.join(errors) + ')')
        flash('The Venue data is not valid. Please try again!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    from models import Venue

    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    form = VenueForm(obj=venue)

    # Done: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    from models import Venue
    # Done: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    error = False
    form = VenueForm(request.form, meta={'csrf': False})

    venue = db.session.query(Venue).filter_by(id=venue_id).first()

    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.genres = form.genres.data
            venue.website = form.website.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            print("oops")
            abort(400)

    else:
        message = []
        for field, errors in form.errors.items():
            message.append(field + ': (' + '|'.join(errors) + ')')
        flash('The Venue data is not valid. Please try again!')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    from models import Artist, db
    # called upon submitting the new artist listing form
    # Done: insert form data as a new Venue record in the db, instead
    # Done: modify data to be the data object returned from db insertion

    error = False
    form = ArtistForm(request.form, meta={'csrf': False})

    if form.validate():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                genres=form.genres.data,
                website=form.website.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )

            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. Venue ' + artist.name + ' could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            print("oops")
            abort(400)

    else:
        message = []
        for field, errors in form.errors.items():
            message.append(field + ': (' + '|'.join(errors) + ')')
        flash('The Venue data is not valid. Please try again!')

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # Done: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    from models import Artist, Venue, Show, db
    # displays list of shows at /shows
    # Done: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []

    shows = db.session.query(Show, Venue, Artist) \
        .filter(Show.venue_id == Venue.id) \
        .filter(Show.artist_id == Artist.id) \
        .order_by(Show.start_time.desc()) \
        .all()

    for s, v, a in shows:
        data.extend([{
            "venue_id": v.id,
            "venue_name": v.name,
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": a.image_link,
            "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M")
        }])

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    from models import Show, db
    # called to create new shows in the db, upon submitting new show listing form
    # Done: insert form data as a new Show record in the db, instead
    error = False
    form = ShowForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            show = Show()
            show.artist_id = form.artist_id.data,
            show.venue_id = form.venue_id.data,
            show.start_time = form.start_time.data

            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            print("oops")
            abort(400)

    else:
        message = []
        for field, errors in form.errors.items():
            message.append(field + ': (' + '|'.join(errors) + ')')
        flash('The Show data is not valid. Please try again!')

    # on successful db insert, flash success
    # Done: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
