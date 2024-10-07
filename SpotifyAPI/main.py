import os
import sys
from flask import *
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from time import time, gmtime, strftime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

CLIENT_ID = '9381c03b50ff4dd0b5dd1960e41f905f'
CLIENT_SECRET = 'b9a1e77140c04e1b8262370a653f0f58'
redirect_uri = 'http://localhost:5000/callback'
scope = 'user-library-read user-top-read'
cache_handler = FlaskSessionCacheHandler(session)

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True,
)
sp = Spotify(auth_manager=sp_oauth)

# DEFAULT PAGE BEFORE LOGGING IN
@app.route('/')
def index():
    return render_template("index.html")
    
    

# FOR REFRESHING PAGE
@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code']) # GETS SPOTIFY ACCESS TOKEN
    return redirect(url_for('homepage'))

# FOR REFRESHING PAGE
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#If NOT logged in
@app.route('/homepage')
def homepage():
    if sp_oauth.validate_token(cache_handler.get_cached_token()): # IF ALREADY VALIDATED
        pass
    else:
        auth_url = sp_oauth.get_auth_response() #OPENS THE SPOTIFY LOGIN SCREEN
        render_template('index.html')
        return redirect(auth_url)
    
    current_user_name = sp.current_user()['display_name']
    shortTermTracks = sp.current_user_top_tracks(
        limit=25,
        offset=0,
        time_range="short_term"
    )

    mediumTermTracks = sp.current_user_top_tracks(
        limit=25,
        offset=0,
        time_range="medium_term"
    )

    longTermTracks = sp.current_user_top_tracks(
        limit=25,
        offset=0,
        time_range="long_term"
    )

    # USER TOP ARTISTS
    shortTermArtists = sp.current_user_top_artists(
        limit=25,
        offset=0,
        time_range="short_term"
    )

    mediumTermArtists = sp.current_user_top_artists(
        limit=25,
        offset=0,
        time_range="medium_term"
    )

    longTermArtists = sp.current_user_top_artists(
        limit=25,
        offset=0,
        time_range="long_term"
    )
    
    return render_template('homepage.html', user_display_name=current_user_name, shortTermTracks=shortTermTracks, mediumTermTracks=mediumTermTracks, longTermTracks=longTermTracks, shortTermArtists=shortTermArtists, mediumTermArtists=mediumTermArtists, longTermArtists=longTermArtists, currentTime=gmtime())

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    return strftime("%a, %d %b %Y", date)

@app.template_filter('mmss')
def _jinja2_filter_miliseconds(time, fmt=None):
    time = int(time / 1000)
    minutes = time // 60 
    seconds = time % 60 
    if seconds < 10: 
        return str(minutes) + ":0" + str(seconds)
    return str(minutes) + ":" + str(seconds ) 

@app.template_filter('format_followers')
def format_followers(count):
    if count >= 1_000_000:
        return f'{count / 1_000_000:.0f}M'
    elif count >= 1_000:
        return f'{count / 1_000:.0f}K'
    return str(count)

@app.template_filter('format_followers_table')
def format_followers(count):
    return "{:,}".format(count)

@app.template_filter('format_genres')
def format_followers(genres):
    genre_string = ''.join(genres)
    capitalized_genre = genre_string.title()
    return capitalized_genre

if __name__ == '__main__':
    app.run(debug=True)