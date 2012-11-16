import os, time, sched, requests, json, HTMLParser
import urlparse, math, collections, re
from flask import *
from flask.ext.sqlalchemy import *
from BeautifulSoup import BeautifulSoup
from adn import *
from flask.ext.wtf.html5 import URLField
from helpers import *



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

app.secret_key = os.environ['APP_SECRET_KEY']

tavorite = Adn(access_token=os.environ['ACCESS_TOKEN'])


@app.route('/')
def home():
    twenty_minutes_ago = datetime.utcnow() - timedelta(seconds=1200)
    links = Post.query.order_by(Post.score_with_time.desc()).filter(~Post.main_url.in_(filter_out_media)).filter(Post.date < twenty_minutes_ago).filter(Post.score >= 2).limit(70).all()
    links = links[0:50]

    if 'access_token' in session:
        username = session['username']
        if not User.query.filter_by(username=username).first():
            user = Adn(access_token=session['access_token']).getSelf()['data']
            add_user_to_db = User(user, access_token=session['access_token'])
            db.session.add(add_user_to_db)
            db.session.commit()
        
        karma_score = User.query.filter_by(username=username).first().karma

        return render_template('show_links.html', age=age, links=links, username=username, voted_for=voted_for, count_comments=count_comments, karma_score=karma_score,newest_class="not-active", vid_class="not-active", sub_class="not-active")
    else:
        return render_template('show_links.html', age=age, links=links, count_comments=count_comments, newest_class="not-active", vid_class="not-active", sub_class="not-active")



@app.route('/videos')
def videos():
    twenty_minutes_ago = datetime.utcnow() - timedelta(seconds=1200)
    media = ['www.youtube.com', 'youtube.com', 'vimeo.com', 'www.vimeo.com']
    links = Post.query.order_by(Post.score_with_time.desc()).filter(Post.main_url.in_(media)).filter(Post.date < twenty_minutes_ago).limit(50).all()

    if 'access_token' in session:
        username = session['username']
        karma_score = User.query.filter_by(username=username).first().karma

        return render_template('show_links.html', age=age, links=links, username=username, voted_for=voted_for, count_comments=count_comments, karma_score=karma_score, newest_class="not-active", vid_class="active", sub_class="not-active")
    else:
        return render_template('show_links.html', age=age, links=links, count_comments=count_comments, newest_class="not-active", vid_class="active", sub_class="not-active")



@app.route('/photos')
def photos():
    media = ['instagram.com', 'www.instagram.com', 'instagr.am']
    photos = Post.query.order_by(Post.date.desc()).filter(Post.picture > '').limit(50).all()
    return render_template('photos.html', photos=photos)



@app.route('/newest')
def newest():

    links = Post.query.order_by(Post.date.desc()).filter(~Post.main_url.in_(newest_filter)).limit(50).all()

    if 'access_token' in session:
        username = session['username']
        karma_score = User.query.filter_by(username=username).first().karma

        return render_template('show_links.html', age=age, links=links, username=username, voted_for=voted_for, count_comments=count_comments, karma_score=karma_score, newest_class="active", vid_class="not-active", sub_class="not-active")
    else:
        return render_template('show_links.html', age=age, links=links, count_comments=count_comments, newest_class="active", vid_class="not-active", sub_class="not-active")


@app.route('/_upvote')
def upvote():


    data = request.args.get('a', None)
    if 'access_token' in session:
        adn = Adn(access_token=session['access_token'])
        username = session['username']
        post = Post.query.filter_by(post_id=data).first()
        comment = Comment.query.filter_by(comment_id=data).first()
        
        if username not in voted_for(post) and post:
            post.score += 1
            voting = Votes(username, post=post)
            db.session.add(voting)
            db.session.commit()
            if post.username != username:
                user = User.query.filter_by(username=post.username).first()
                if user:
                    user.karma += 1
                    db.session.commit()
            return jsonify(result=post.score)
        elif username not in voted_for(comment) and comment:
            comment.score += 1
            voting = Votes(username, comment=comment)
            db.session.add(voting)
            db.session.commit()
            if comment.username != username:
                user = User.query.filter_by(username=comment.username).first()
                if user:    
                    user.karma += 1
                    db.session.commit()
            return jsonify(result=comment.score)
        else:
            return redirect(url_for('home'))
    else:
       return redirect(url_for('home'))


@app.route('/comments/<int:post_id>', methods=['GET', 'POST'])
def comments(post_id):
    form = CommentForm()
    link = Post.query.filter_by(post_id=post_id).first()

    if 'access_token' in session:
        adn = Adn(access_token=session['access_token'])
        username = session['username']
        karma_score = User.query.filter_by(username=username).first().karma
        if request.method == "GET":
            if link:
                return render_template("comments.html", count_comments=count_comments, age=age, link=link, username=username, voted_for=voted_for, form=form, karma_score=karma_score)
            else:
                return render_template("404.html") 

        if request.method == "POST" and form.validate():
            comment = form.comment.data
            comment_adn = adn.createPost(text="@" + link.username + " " + comment + " (via @tavorite)", reply_to=link.post_id)
            
            comment = Comment(comment_adn['data'], text=comment)
            votes = Votes(username, comment=comment)
            db.session.add(votes)
            link.comments.append(comment)
            db.session.commit()

            return redirect(url_for("comments", post_id=link.post_id))

        else:
            return render_template("comments.html", count_comments=count_comments, age=age, link=link, username=username, voted_for=voted_for, form=form, karma_score=karma_score)
            
    else:
        if link:
            return render_template("comments.html", count_comments=count_comments, age=age, link=link, form=form)
        else:
            return render_template("404.html")




@app.route('/reply/<int:comment_id>', methods=['GET', 'POST'])
def reply(comment_id):
    form = CommentForm()
    comment =Comment.query.filter_by(comment_id=comment_id).first()
    if 'access_token' in session:

        username = session['username']
        adn = Adn(access_token=session['access_token'])
        karma_score = User.query.filter_by(username=username).first().karma

        if request.method == "GET":
            if comment:
                return render_template("reply.html", age=age, comment=comment, form=form, username=username, voted_for=voted_for, karma_score=karma_score)
            else:
                return render_template("404.html")

        if request.method == 'POST' and form.validate():

            reply = form.comment.data
            post = parent_post(comment)

            reply_adn = adn.createPost(text="@" + comment.username + " " + reply + " (via @tavorite)", reply_to=comment.comment_id)
            c = Comment(reply_adn['data'], text=reply)
            votes = Votes(username, comment=c)

            db.session.add(votes)
                         
            comment.children.append(c)

            db.session.commit()
            return redirect(url_for("comments", post_id=post.post_id))
        
        else: 
            return render_template("reply.html", age=age, comment=comment, 
                                   form=form, username=username, voted_for=voted_for, karma_score=karma_score)
            

    else:
        if comment:
            return render_template("reply.html", age=age, comment=comment, form=form) 
        else:
            return render_template("404.html")
            
    
 
    




@app.route('/submit', methods=['POST', 'GET'])
def submit():

    form = SubmitForm()

    if 'access_token' in session:

        adn = Adn(access_token=session['access_token'])
        username = session['username']
        karma_score = User.query.filter_by(username=username).first().karma

        if request.method == 'GET':
            return render_template('submit.html', username=username, form=form, karma_score=karma_score, newest_class="not-active", vid_class="not-active", sub_class="active")

        if request.method == 'POST' and form.validate():
            title = form.title.data
            url = form.url.data
            tavorite_post = adn.createPost(text=title + ": " + url + " (via @Tavorite)")
            if tavorite_post['data']['entities']['links']:
                insert_post_to_db = Post(tavorite_post['data'], score=2, headline=title)
                vote_for_post     = Votes(username, post=insert_post_to_db)
                db.session.add(insert_post_to_db)
                db.session.add(vote_for_post)
                db.session.commit()
                return redirect(url_for("newest"))
            else:
                flash("Something went wrong with your url, Try again!")
                return redirect(url_for("submit"))
        else:
            return render_template("submit.html", username=username, form=form, newest_class="not-active", vid_class="not-active", sub_class="active")
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
        adn = Adn(client_id=os.environ.get('CLIENT_ID'), 
                  client_secret=os.environ.get('CLIENT_SECRET'), 
                  redirect_uri=os.environ.get('REDIRECT_URL'))

        if adn.getAccessToken(code) != "ERROR":
            session['access_token'] = adn.access_token                
            session['username'] = adn.getSelf()['data']['username']
            return redirect(url_for("home"))
            
        else:
            return redirect(url_for("home"))
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
    url_exists      = db.Column(db.Boolean)
    profile_picture = db.Column(db.Unicode(500))
    picture         = db.Column(db.Unicode(500))
    thread          = db.Column(db.Unicode(256))
    

    def __init__(self, post, score=1, headline=None):

        if post['entities']['links']:
            if len(post['entities']['links']) == 1:
                try:
                    r = requests.get(post['entities']['links'][0]['url'])
                    self.link = r.url
                except:
                    self.link = post['entities']['links'][0]['url']
            else:
                if len(post['entities']['links']) > 1:
                    link_and_r = find_longest_url(post['entities']['links'])
                    self.link = link_and_r[0]
                    r = link_and_r[1]
                        
                else:
                    self.link = unicode("")

        try:
            self.page_text = r.text
        except:
            self.page_text = "Error grabbing text"

        #get instagram
        if ('http://instagr' in self.link):
            try:
                soup = BeautifulSoup(self.page_text)
                a = soup.findAll(attrs={"property":"og:image"})[0]['content']
                #a = soup.find(id='media_photo').findAll('img')[0]['src']
                self.picture = a
            except:
                self.picture = unicode("")

        if [image_exists for image_exists in ['.gif', '.jpeg', 'jpg', '.png'] if image_exists in self.link]:
            self.picture = self.link

        #get twitpic
        if ('twitpic' in self.link):
            soup = BeautifulSoup(self.page_text)
            a = soup.findAll(attrs={"name":"twitter:image"})[0]['value']
            self.picture = a

        #get yfrog
        if ('yfrog' in self.link):
            soup = BeautifulSoup(self.page_text)
            a = soup.findAll(attrs={"property":"og:image"})[0]['content']
            self.picture = a        
        

        #get main url
        if self.link:
            home = urlparse.urlsplit(self.link)
            self.main_url = home.netloc
        else:
            self.main_url = unicode("")

        if self.picture == None:
            self.picture = unicode("")
        if self.link == None:
            self.link == unicode("")

        self.profile_picture = post['user']['avatar_image']['url'] 
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
        self.thread          = post['thread_id']


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
                if clean_up_2 == unicode('403 Forbidden') or clean_up_2 == unicode('500 Internal Server Error'):
                    a = self.text
                    cleaned_up = a.lstrip("'").rstrip("'")
                    return cleaned_up
                else:
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


class Last(db.Model):
    
  id       = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Unicode(256))
  post_id  = db.Column(db.BIGINT, unique=True)
                     
  def __init__(self, post):
      self.username = post['user']['username']
      self.post_id  = post['id']


class User(db.Model):

    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.Unicode(256))
    access_token    = db.Column(db.Unicode(256), unique=True)
    created_at      = db.Column(db.Unicode(256))
    adn_url         = db.Column(db.Unicode(256))
    name            = db.Column(db.Unicode(256))
    karma           = db.Column(db.BIGINT)

    def __init__(self, user, access_token=None):
        self.access_token = access_token
        self.username     = user['username']
        self.created_at   = user['created_at']
        self.adn_url      = user['canonical_url']
        self.name         = user['name']
        self.karma        = 1


class Votes(db.Model):
    """A Post has votes"""

    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.Unicode(256))
    vote_date = db.Column(db.DateTime)
    post_id   = db.Column(db.Integer, db.ForeignKey('post.id'))
    post      = db.relationship('Post',
                               backref=db.backref('votes', lazy='dynamic'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    comment    = db.relationship('Comment',
                                 backref=db.backref('votes', lazy="dynamic"))


    def __init__(self, username, post=None, comment=None):
        self.username = username
        self.vote_date = datetime.utcnow()
        self.post = post
        self.comment = comment
        

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
    text       = db.Column(db.Unicode(500))
    comment_id = db.Column(db.BIGINT, unique=True)
    com_text   = db.Column(db.UnicodeText)
    thread     = db.Column(db.Unicode(256))
    reply_to   = db.Column(db.Unicode(256))

    def __init__(self, comment, text=None):

        self.date       = datetime.utcnow()
        self.username   = comment['user']['username']
        self.score      = 1
        self.com_text   = comment.get('text')
        self.comment_id = comment.get('id')
        self.comment    = json.dumps(comment)
        self.thread     = comment.get('thread_id')
        self.reply_to   = comment.get('reply_to')

        if text:
            self.text = text
        else:
            if self.com_text:
                self.text = clean_comment_text(self.com_text)
            else:
                self.text = self.com_text


def add_comments(post_id):
    if type(post_id) == int:
        post_id = str(post_id)
     
    a = 1
    new_root = []
    root = [post_id]
    user = User.query.first()
    try:
        replies = tavorite.repliesToPost(post_id=post_id, count=200)['data']
    except:
        return "There was an Error in retrieving the post From ADN"

    post_comments = all_comment_ids_from_post(Post.query.filter_by(post_id=post_id).first())
   
    while a < len(replies):
        r = []
        for y in replies:
            if y.get('reply_to') in root and y.get('reply_to'):
                r.append(y)

        if post_id in root:
            post = Post.query.filter_by(post_id=post_id).first()
        else:
            post = None
        
        for reply in r:

            if reply['id'] not in post_comments:
                
                c = Comment(reply)
                votes = Votes(reply['user']['username'], comment=c)
                db.session.add(votes)

                if post:
                    post.comments.append(c)
                else:
                    comment = Comment.query.filter_by(comment_id=reply['reply_to']).first()
                    comment.children.append(c)

                db.session.commit()

            a += 1
            new_root.append(reply['id'])

        root = new_root
        new_root = []



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
