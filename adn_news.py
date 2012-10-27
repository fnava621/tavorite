import os, time, sched, requests, json, HTMLParser
import urlparse, math, collections, re
from flask import *
from flask.ext.sqlalchemy import *
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from adn import *


app = Flask(__name__)

#heroku db_config app.config['SQALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////Users/fernandonava/adn_news/test.db' 


#HEROKU CONFIG
CLIENT_ID = 'sDndZTeGWmmd5tYEyRmm5WA6wpSdDBse'
CLIENT_SECRET = 'jKPDXPHLPqdC49p6RqARTk5EwJWknJpW'
REDIRECT_URL = 'http://127.0.0.1:5000/oauth/complete'
ACCESS_TOKEN = 'AQAAAAAAAYmXp4Y26LOMsXwCGD9D2HajHMphN9PmTRlGeJWbwCc42Tikgn9YL5gBipybAiNeED35Wttje7K0y7HLbN-GkCigtA'

app.secret_key = 'V\x16d|;\x8a\xff]&\x80n\xd7\x98\x01\xd1j\x06,\xa32\x97\xcf_\xfd'
def voted_for(post):
    if post:
        return [x.username for x in post.votes.all()]
    else: return []

app_adn = Adn(access_token=ACCESS_TOKEN, client_id= CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

filter_out_media = ['instagram.com', 'www.instagram.com', 'instagr.am', 'youtube.com', 'www.youtube.com', 'www.vimeo.com', 'vimeo.com', 'twitpic.com', 'www.twitpic.com', 'i.imgur.com', 'www.yfrog.com', 'twitter.yfrog.com','twitter.com', 'imgur.com', 't.co', 'join.app.net', 'd.pr', 'www.mobypicture.com', 'i.appimg.net', 'foursquare.com', 'www.foursquare.com', 'www.path.com', 'path.com', 'cl.ly', 'm.youtube.com', 'mobile.twitter.com', 'alpha.app.net', 'alpha-api.app.net', 'appnetizens.com', 'jer.srcd.mp', 'm.flickr.com'] 
 

@app.route('/')
def home():
    links = Post.query.order_by(Post.date.desc()).filter(~Post.main_url.in_(filter_out_media)).limit(100).all()

    adn = Adn(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

    auth_url = adn.getAuthUrl()

    if 'access_token' in session:
        auth_user = Adn(access_token=session['access_token'])
        user = auth_user.getSelf()
        username = user['username']
        if not User.query.filter_by(username=username).first():
            add_user_to_db = User(user, access_token=session['access_token'])
            db.session.add(add_user_to_db)
            db.session.commit()

        return render_template('show_links.html', links=links, auth_url=auth_url, username=username, voted_for=voted_for)
    else:
        return render_template('show_links.html', links=links, auth_url=auth_url)

@app.route('/_upvote')
def upvote():
    post_id = request.args.get('a', None)
    if 'access_token' in session:
        adn = Adn(access_token=session['access_token'])
        user = adn.getSelf()['username']
        post = Post.query.filter_by(post_id=post_id).first()
        if user not in voted_for(post) and post:
            post.score += 1
            voting = Votes(user, post)
            db.session.add(voting)
            db.session.commit()
            return jsonify(result=post.score)
        else:
            return redirect(url_for('home'))
    else:
       return redirect(url_for('home'))
            
@app.route('/videos')
def videos():
    media = ['www.youtube.com', 'youtube.com', 'vimeo.com', 'www.vimeo.com']
    videos = Post.query.order_by(Post.date.desc()).filter(Post.main_url.in_(media)).limit(50).all()
    return render_template('videos.html', videos=videos)



@app.route('/photos')
def photos():
    media = ['instagram.com', 'www.instagram.com', 'instagr.am']
    photos = Post.query.order_by(Post.date.desc()).filter(Post.main_url.in_(media)).limit(50).all()
    return render_template('photos.html', photos=photos)


@app.route('/submit')
def submit():
    if 'access_token' in session:
        adn = Adn(access_token=session['access_token'])
        username = adn.getSelf()['username']
        return render_template('submit.html', username=username)
    return redirect(url_for("home"))

@app.route('/best')
def best():
    links = Post.query.order_by(Post.score.desc()).limit(50).all()
    return render_template('best_of_week.html', links=links)


@app.route('/logout')
def logout():
    if 'access_token' in session:
        session.pop('access_token', None)
        return redirect(url_for("home"))
    else:
        redirect(url_for("home"))
    


@app.route('/oauth/complete')
def complete():
    code = request.args.get('code', None)
    if code:
        adn = Adn(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

        if "ERROR" not in adn.getAccessToken(code):
            session['access_token'] = adn.access_token

    return redirect(url_for("home"))


@app.route('/show')
def show():
    if 'access_token' in session:
        links = Post.query.order_by(Post.date.desc()).limit(50).all()
        return render_template('show_links.html', links=links)
    else:
        return redirect(url_for('hello'))




          
class Post(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    post            = db.Column(db.UnicodeText)
    post_id         = db.Column(db.BIGINT, unique=True)
    username        = db.Column(db.Unicode(140))
    name            = db.Column(db.Unicode(140))
    score           = db.Column(db.Integer)
    score_with_time = db.Column(db.Float)
    headline        = db.Column(db.Unicode(300))
    std_deviation   = db.Column(db.Float)
    std_dev_sigma   = db.Column(db.Float)
    num_reposts     = db.Column(db.Integer)
    num_stars       = db.Column(db.Integer)
    num_replies     = db.Column(db.Integer)
    text            = db.Column(db.Unicode(300))
    link            = db.Column(db.Unicode(300))
    main_url        = db.Column(db.Unicode(300))
    date            = db.Column(db.DateTime)
    page_text       = db.Column(db.UnicodeText)

    def __init__(self, post):

        if post['entities']['links']:
            try:
                r = requests.get(post['entities']['links'][0]['url'])
                self.link = r.url
            except:
                self.link = post['entities']['links'][0]['url']
        else:
            self.link = unicode("")
  
        try:
            self.page_text = r.text
        except:
            self.page_text = "Error grabbing text"
        
        if self.link:
            home = urlparse.urlsplit(self.link)
            self.main_url = home.netloc
        else:
            self.main_url = unicode("")


        self.post            = self.turn_json(post)
        self.post_id         = post['id']
        self.username        = post['user']['username']
        self.name            = post['user']['name']
        self.score           = 1
        self.score_with_time = 1.0
        self.std_deviation   = 1.0
        self.std_dev_sigma   = 1.0
        self.date            = datetime.utcnow()
        self.num_reposts     = post['num_reposts']
        self.num_stars       = post['num_stars']
        self.num_replies     = post['num_replies']
        self.text            = post['text']
        self.headline        = self.pull_headline(self.page_text)


    def turn_json(self, p):
        post_str = json.dumps(p)
        return post_str


    def pull_headline(self, page_text):
        h = HTMLParser.HTMLParser()

        try:
            soup = BeautifulSoup(page_text)
        except:
            soup = BeautifulSoup('')

        if soup.findAll('title'):
            title = soup.find('title')
            content = title.renderContents()
            decode = content.decode("utf-8")
            unicode_text = h.unescape(decode)
            clean_up_0 = self.remove_separator_and_extra_content(unicode_text, " - ")
            #add self 
            clean_up_1 = self.remove_separator_and_extra_content(clean_up_0, " \| ") 
            clean_up_2 = self.remove_separator_and_extra_content(clean_up_1, " \// ")
            #add self
            return clean_up_2
        else: 
            return self.text


    def remove_separator_and_extra_content(self, content, separator): 
        dash = re.findall(separator, content)
        split_content = re.split(separator, content)
        if len(dash) > 0 and len(split_content[0] + split_content[1]) > 30:
            a = split_content[0]
            b = a.lstrip()
            c = b.rstrip()
            return c
        elif len(dash) > 0 and len(split_content[0] + split_content[1]) < 30:
            if separator == " \| ":
                separator = " | "
            a = split_content[0] + unicode(separator) + split_content[1]
            b = a.lstrip()
            c = b.rstrip()
            return c
        else: 
            a = content.lstrip()
            b = a.rstrip()
            return b

class User(db.Model):

    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.Unicode(256))
    access_token    = db.Column(db.Unicode(256), unique=True)
    created_at      = db.Column(db.Unicode(256))
    adn_url         = db.Column(db.Unicode(256))
    name            = db.Column(db.Unicode(256))

    def __init__(self, user, access_token=None):
        self.access_token = access_token
        self.username     = user['username']
        self.created_at   = user['created_at']
        self.adn_url      = user['canonical_url']
        self.name         = user['name']

class Votes(db.Model):
    """A Post has votes"""

    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.Unicode(256))
    vote_date = db.Column(db.DateTime)
    post_id   = db.Column(db.Integer, db.ForeignKey('post.id'))
    post      = db.relationship('Post',
                               backref=db.backref('votes', lazy='dynamic'))


    def __init__(self, username, post):
        self.username = username
        self.vote_date = datetime.utcnow()
        self.post = post
        

def every_two_minutes():
    def only_links():
        for x in app_adn.userStream(count=200):
            if x['entities']['links']:
                a = Post(x)
                try:
                    db.session.add(a)
                    db.session.commit()
                except:
                    db.session.rollback()
    #update every 30 seconds
    s = sched.scheduler(time.time, time.sleep)
    print "updating feed beginning"
    s.enter(60, 1, only_links, ())
    s.run()
    every_two_minutes()
    
      
    
def times_appears_in_stream(link, counter):
    links_only = []
    for x in counter:
        links_only.append(x[0])
    if link not in links_only:
        return 1
    else:
        for x in counter:
            if link in x[0]:
                return x[1]

def filter_for_double_links_from_same_person(all_links):
    filtered_links = []
    tweet_links = []
    for lnk in all_links:
        link = lnk.link
        user_id = lnk.screen_name
        if (link, user_id) not in filtered_links:
            x = (link, user_id)
            filtered_links.append(x)
            tweet_links.append(link)
    return tweet_links



if __name__ == '__main__':
    app.run(debug=True)
