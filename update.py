from adn_news import *
from helpers import *


def process_post(x):
    if x['entities'] and x['entities']['links']:
        if x.get('id') == x.get('thread_id'):
            if not Post.query.filter_by(post_id=x.get('id')).first():
                a = Post(x)
                try:
                    db.session.add(a)
                    db.session.commit()
                except:
                    db.session.rollback()


def get_posts_update_db():
    last = Last.query.first()
    last_in_post_db = Post.query.order_by(Post.id.desc()).first()

    if last == None:
        last = Last(json.loads(last_in_post_db.post))
        db.session.add(last)
        db.session.commit()

    if last.post_id < last_in_post_db.post_id:
        db.session.delete(last)
        db.session.commit()
        new_last = Last(json.loads(last_in_post_db.post))
        db.session.add(new_last)
        db.session.commit
        last = Last.query.first()

    t = tavorite.globalStream(count=200, since_id=last.post_id)
    if t.get('meta').get('code') == 200:
        for x in t['data']:
            process_post(x)

        if t['data']:
            if int(t['data'][0]['id']) != last.post_id:
                db.session.delete(last)
                db.session.commit()

                track_last = Last(t['data'][0])
                db.session.add(track_last)
                db.session.commit()


def get_hashtag_update_db():
    hashtag = Hashtag.query.first()
    t = tavorite.taggedPosts(hashtag='tavorite', count=200, since_id=hashtag.post_id)
    if t.get('meta').get('code') == 200:    
        for x in t['data']:
            process_post(x)
        if t['data']:
            if int(t['data'][0]['id']) != hashtag.post_id:
                db.session.delete(hashtag)
                db.session.commit()

                track_last = Hashtag(t['data'][0])
                db.session.add(track_last)
                db.session.commit()
                return "Posts udpated from Hashtag"
    else:
        return "No posts were updated from Hashtag"




def update_posts_comments():
    two_days_ago = datetime.utcnow() - timedelta(days=1)
    posts = Post.query.filter(Post.date > two_days_ago).all()
    for x in posts:
        num_comments = number_of_comments(count_comments(x))
        current_replies = tavorite.repliesToPost(post_id=x.post_id, count=200).get('data')
        if current_replies == None:
            current_replies = ["No replies"]

        num_replies = len(current_replies) - 1
        if num_comments < num_replies:
            x.score = num_replies
            db.session.commit()
            add_comments(str(x.post_id))



def hacker_news(votes, item_hour_age, gravity=1.8):
    return votes/pow((item_hour_age+2), gravity)

def reduce_score_with_time(days_old=[1,2,3,4,5]):
    def reduce_score(time_old):
        if time_old == 1:
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            post = Post.query.filter(Post.date > one_day_ago).all()
        else:
            frm = datetime.utcnow() - timedelta(days=(time_old-1))
            to = datetime.utcnow() - timedelta(days=time_old)
            post = Post.query.filter(Post.date < frm, Post.date > to).all()
        for x in post:
            x.score_with_time = hacker_news(x.score, link_age_in_hours(x))
            db.session.commit()
    for x in days_old:
        reduce_score(x)
    print "Gravity at work"



def update_every_minute():
    """Automates - every X minutes gets new post and update those posts if they have additional comments"""

    #s = sched.scheduler(time.time, time.sleep)
    print "updating feed beginning"
    #s.enter(300, 1, get_posts_update_db, ())
    #s.run()
    get_posts_update_db()
    print "updating hashtag posts"
    get_hashtag_update_db()
    reduce_score_with_time()
    update_posts_comments()    
    return update_every_minute()
    """To continously loop recursive call update_every_minute()"""

# heroku scheduler runs every 10 minutes

if __name__ == '__main__':
    update_every_minute()
    
    
