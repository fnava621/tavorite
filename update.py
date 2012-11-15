from adn_news import *
from helpers import *


def get_posts_update_db():
    last = Last.query.first()
    t = tavorite.userStream(count=200, since_id=last.post_id)
    for x in t:
        if x['entities']['links']:
            if x.get('id') == x.get('thread_id'):
                if not Post.query.filter_by(post_id=x.get('id')).first():
                    a = Post(x)
                    db.session.add(a)
                    db.session.commit()
    
    db.session.delete(last)
    db.session.commit()

    track_last = Last(t[-1])
    db.session.add(track_last)
    db.session.commit()




def update_posts_comments():
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    posts = Post.query.filter(Post.date > two_days_ago).all()
    for x in posts:
        num_comments = number_of_comments(count_comments(x))
        current_replies = tavorite.repliesToPost(post_id=x.post_id, count=200)
        num_replies = len(current_replies) - 1
        if num_comments < num_replies:
            x.score = num_replies
            db.session.commit()
            add_comments(str(x.post_id))



def hacker_news(votes, item_hour_age, gravity=1.8):
    return votes/pow((item_hour_age+2), gravity)

def reduce_score_with_time():
    """reduces posts score_with_time for last 5 days"""
    six_days_ago = datetime.utcnow() - timedelta(days=5)
    posts = Post.query.filter(Post.date > six_days_ago).all()
    for x in posts:
        item_hour_age = ""
        x.score_with_time = hacker_news(x.score, link_age_in_hours(x))
        db.session.commit()
    pass



def update_every_minute():
    """Automates - every X minutes gets new post and update those posts if they have additional comments"""

    s = sched.scheduler(time.time, time.sleep)
    print "updating feed beginning"
    s.enter(10, 1, get_posts_update_db, ())
    s.run()
    update_posts_comments()
    reduce_score_with_time()
    """To continously loop recursive call update_every_minute()"""



if __name__ == '__main__':
    update_every_x_minutes()