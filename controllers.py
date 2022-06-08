from datetime import datetime
from forms import *
from flask import request, flash


class Controller:
    def __init__(self, db, Venue, Artist, Show):
        self.db = db
        self.Venue = Venue
        self.Artist = Artist
        self.Show = Show


class VenueController(Controller):
    def __init__(self, db, Venue, Artist, Show):
        Controller.__init__(self, db, Venue, Artist, Show)

    def get_all_venues(self):
        data = []
        db = self.db
        Venue = self.Venue

        locations = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
        for location in locations:
            venues = db.session.query(Venue).filter(Venue.city == location[0]).filter(Venue.state == location[1]).all()
            data.append(
                {
                    'city': location[0],
                    'state': location[1],
                    'venues': venues
                }
            )

        return data

    def search_venue(self):
        data = []
        db = self.db
        Venue = self.Venue
        Show = self.Show

        search_term = request.form.get('search_term')
        venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
        for venue in venues:
            data.append(
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(
                        Show.start_time > datetime.now()).all())
                }
            )

        response = {
            "count": len(venues),
            "data": data
        }
        return response

    def send_edit_venue_form(self, venue_id):
        Venue = self.Venue

        form = VenueForm()

        venue = Venue.query.get(venue_id)

        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link

        return form, venue

    def edit_venue(self, venue_id):
        db = self.db
        Venue = self.Venue

        form = VenueForm(request.form)

        venue = Venue.query.get(venue_id)

        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data

        try:
            db.session.commit()
            flash('The Venue ' + form.name.data + ' was successfully Updated')

        except:
            db.session.rollback()
            flash('The Venue ' + form.name.data + ' was not Updated')

        finally:
            db.session.close()

    def create_venue(self):
        db = self.db
        Venue = self.Venue
        form = VenueForm(request.form)
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                address=form.address.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
            )
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()

    def get_venue(self, venue_id):
        db = self.db
        Venue = self.Venue
        Artist = self.Artist
        Show = self.Show
        venue = Venue.query.get(venue_id)

        past_shows = []
        upcoming_shows = []

        venue_past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
            Show.start_time < datetime.now()).all()
        for show in venue_past_shows:
            past_shows.append(
                {
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        venue_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
            Show.start_time > datetime.now()).all()
        for show in venue_upcoming_shows:
            upcoming_shows.append(
                {
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
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
            "past_shows_count": Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time < datetime.now()).count(),
            "upcoming_shows_count": Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time > datetime.now()).count()
        }

        return data

    def delete_venue(self, venue_id):
        db = self.db
        Venue = self.Venue
        try:
            venue = Venue.query.get(venue_id)
            venue_name = venue.name

            db.session.delete(venue)
            db.session.commit()

            flash('Venue ' + venue_name + ' was deleted')
        except:
            db.session.rollback()
            flash('an error occured and Venue ' + venue_name + ' was not deleted')
        finally:
            db.session.close()


class ArtistController(Controller):
    def __init__(self, db, Venue, Artist, Show):
        Controller.__init__(self, db, Venue, Artist, Show)

    def get_all_artists(self):
        db = self.db
        Artist = self.Artist
        data = db.session.query(Artist).all()
        return data

    def search_artist(self):
        db = self.db
        Artist = self.Artist
        Show = self.Show

        data = []
        search_term = request.form.get('search_term')
        artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()

        for artist in artists:
            data.append(
                {
                    "id": artist.id,
                    "name": artist.name,
                    "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == artist.id).filter(
                        Show.start_time > datetime.now()).all()),
                }
            )
        response = {
            "count": len(artists),
            "data": data
        }

        return response

    def get_artist(self, artist_id):
        db = self.db
        Venue = self.Venue
        Artist = self.Artist
        Show = self.Show

        artist = db.session.query(Artist).get(artist_id)
        past_shows = []
        upcoming_shows = []

        artist_past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
            Show.start_time < datetime.now()).all()
        artist_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
            Show.start_time > datetime.now()).all()

        for show in artist_past_shows:
            past_shows.append(
                {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )

        for show in artist_upcoming_shows:
            upcoming_shows.append(
                {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_talent": artist.seeking_talent,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": Show.query.filter(Show.artist_id == artist.id,
                                                  Show.start_time < datetime.now()).count(),
            "upcoming_shows_count": Show.query.filter(Show.artist_id == artist.id,
                                                      Show.start_time > datetime.now()).count()
        }

        return data

    def send_edit_form(self, artist_id):
        Artist = self.Artist

        form = ArtistForm()
        artist = Artist.query.get(artist_id)

        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link

        return form, artist

    def edit_artist(self, artist_id):
        db = self.db
        Artist = self.Artist

        form = ArtistForm(request.form)

        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data

        try:
            db.session.commit()
            flash('The Artist ' + form.name.data + ' was successfully Updated')
        except:
            db.session.rollback()
            flash('The Artist ' + form.name.data + ' was not Updated')
        finally:
            db.session.close()

    def create_artist(self):
        db = self.db
        Artist = self.Artist

        form = ArtistForm(request.form)
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data
            )
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            db.session.rollback()
        finally:
            db.session.close()


class ShowsController(Controller):
    def __init__(self, db, Venue, Artist, Show):
        Controller.__init__(self, db, Venue, Artist, Show)

    def get_all_shows(self):
        db = self.db
        Venue = self.Venue
        Show = self.Show
        Artist = self.Artist

        data = []
        shows = db.session.query(Show).join(Artist).join(Venue).all()
        for show in shows:
            data.append(
                {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )

        return data

    def create_show(self):
        db = self.db
        Show = self.Show

        form = ShowForm(request.form)
        try:
            show = Show(
                venue_id=form.venue_id.data,
                artist_id=form.artist_id.data,
                start_time=form.start_time.data,
            )
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')

        except:
            db.session.rollback()
            flash('Error, show was not listed!')
        finally:
            db.session.close()