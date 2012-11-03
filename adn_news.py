import os, time, sched, requests, json, HTMLParser
import urlparse, math, collections, re
from flask import *
from flask.ext.sqlalchemy import *
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta
from adn import *
from flask.ext.wtf.html5 import URLField
from helpers import *
    


app = Flask(__name__)

#heroku db_config app.config['SQALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////Users/fernandonava/adn_news/test21.db' 


app.secret_key = 'V\x16d|;\x8a\xff]&\x80n\xd7\x98\x01\xd1j\x06,\xa32\x97\xcf_\xfd'



@app.route('/')
def home():
    links = Post.query.order_by(Post.date.desc()).filter(~Post.main_url.in_(filter_out_media)).limit(100).all()


    if 'access_token' in session:
        username = session['username']
        if not User.query.filter_by(username=username).first():
            user = Adn(access_token=session['access_token']).getSelf()
            add_user_to_db = User(user, access_token=session['access_token'])
            db.session.add(add_user_to_db)
            db.session.commit()

        return render_template('show_links.html', links=links, username=username, voted_for=voted_for, count_comments=count_comments)
    else:
        return render_template('show_links.html', links=links, count_comments=count_comments)

@app.route('/_upvote')
def upvote():
    post_id = request.args.get('a', None)
    if 'access_token' in session:
        adn = Adn(access_token=session['access_token'])
        user = session['username']
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


@app.route('/comments/<int:post_id>', methods=['GET', 'POST'])
def comments(post_id):
    form = CommentForm()
    link = Post.query.filter_by(post_id=post_id).first()

    if 'access_token' in session:
        adn = Adn(access_token=session['access_token'])
        username = session['username']

        if request.method == "GET":
            if link:
                return render_template("comments.html", link=link, username=username, voted_for=voted_for, form=form)
            else:
                return render_template("404.html") 

        if request.method == "POST" and form.validate():
            comment = form.comment.data
            comment = adn.createPost(text="@" + link.username + " " + comment + " (via @tavorite) #AdnNews", reply_to=link.post_id)
            link.comments.append(Comment(comment, ))
            db.session.commit()

            return redirect(url_for("comments", post_id=link.post_id))
            
    else:
        if link:
            return render_template("comments.html", link=link, form=form)
        else:
            return render_template("404.html")



#this should make children of reply to Comment
@app.route('/reply/<int:comment_id>', methods=['GET', 'POST'])
def reply(comment_id):
    form = CommentForm()
    comment =Comment.query.filter_by(comment_id=comment_id).first()
    if 'access_token' in session:

        username = session['username']
        adn = Adn(access_token=session['access_token'])

        if request.method == "GET":
            if comment:
                return render_template("reply.html", comment=comment, form=form, username=username, voted_for=voted_for)
            else:
                return render_template("404.html")

        if request.method == 'POST' and form.validate():

            reply = form.comment.data

            reply_adn = adn.createPost(text="@" + comment.username + " " + reply + " (via @tavorite) #AdnNews", reply_to=comment.comment_id)

            comment.children.append(Comment(reply_adn))

            db.session.commit()

            return redirect(url_for("home")) #redirect for comments/post_id

    else:
        if comment:
            return render_template("reply.html", comment=comment, form=form)
        else:
            return render_template("404.html")
            
    
    #redirect to comments page
    




@app.route('/submit', methods=['POST', 'GET'])
def submit():

    form = SubmitForm()

    if 'access_token' in session:

        adn = Adn(access_token=session['access_token'])
        username = session['username']

        if request.method == 'GET':
            return render_template('submit.html', username=username, form=form)

        if request.method == 'POST' and form.validate():
            title = form.title.data
            url = form.url.data
            tavorite_post = adn.createPost(text=title + ": " + url + " (via @Tavorite)")
            if tavorite_post['entities']['links']:
                insert_post_to_db = Post(tavorite_post, score=2, headline=title)
                vote_for_post     = Votes(username, insert_post_to_db)
                db.session.add(insert_post_to_db)
                db.session.add(vote_for_post)
                db.session.commit()
                return redirect(url_for("home"))
            else:
                flash("Something went wrong with your url, Try again!")
                return redirect(url_for("submit"))
        else:
            return render_template("submit.html", username=username, form=form)
    return redirect(url_for("home"))

@app.route('/best')
def best():
    links = Post.query.order_by(Post.score.desc()).limit(50).all()
    if 'access_token' in session:
        username = session['username']
        return render_template('best_of_week.html', links=links, username=username)
    else:
        return render_template('best_of_week.html', links=links)


@app.route('/logout')
def logout():
    if 'access_token' in session:
        session.pop('access_token', None)
        session.pop('username', None)
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
            session['username'] = adn.getSelf()['username']

    return redirect(url_for("home"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


          
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
    comments        = db.relationship('Comment', 
                                      backref=db.backref('post'))

    def __init__(self, post, score=1, headline=None):
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
        self.score           = score
        self.score_with_time = 1.0
        self.std_deviation   = 1.0
        self.std_dev_sigma   = 1.0
        self.date            = datetime.utcnow()
        self.num_reposts     = post['num_reposts']
        self.num_stars       = post['num_stars']
        self.num_replies     = post['num_replies']
        self.text            = post['text']
        self.headline        = self.pull_headline(headline, self.page_text)


    def turn_json(self, p):
        post_str = json.dumps(p)
        return post_str


    def pull_headline(self, hline, page_text):
        h = HTMLParser.HTMLParser()
        
        
        if hline:
            return hline
        else:

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
            
                clean_up_1 = self.remove_separator_and_extra_content(clean_up_0, " \| ") 
                clean_up_2 = self.remove_separator_and_extra_content(clean_up_1, " \// ")
            
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
        
        

class Comment(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    parent_id  = db.Column(db.Integer, db.ForeignKey('comment.id'))
    children   = db.relationship("Comment", 
                               backref=db.backref("parent", remote_side=[id]))
    post_id    = db.Column(db.Integer, db.ForeignKey('post.id'))
    username   = db.Column(db.Unicode(256))
    date       = db.Column(db.DateTime)
    comment    = db.Column(db.UnicodeText)
    score      = db.Column(db.Integer)
    text       = db.Column(db.Integer(500))
    comment_id = db.Column(db.BIGINT, unique=True)

    def __init__(self, comment):
        self.date       = datetime.utcnow()
        self.username   = comment['user']['username']
        self.score      = 1
        self.text       = comment['text']
        self.comment_id = comment['id']
        self.comment    = json.dumps(comment)
        

    

if __name__ == '__main__':
    app.run(debug=True)
