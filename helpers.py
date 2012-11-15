from flask.ext.wtf import Form, TextField, Required, validators, TextAreaField
from adn import Adn
from datetime import datetime, timedelta
import requests, re

class SubmitForm(Form):
    title = TextField("Title", [validators.Length(min=4, message="Little short for a headline?"), validators.Required()])
    url = TextField("Url", [validators.Length(min=4, message="Little short for a url?"), validators.Required()])


class CommentForm(Form):
    comment = TextAreaField('Comments', [validators.Length(max=256), validators.Required()]) 


def voted_for(post):
    if post:
        return [x.username for x in post.votes.all()]
    else: return []


def count_comments(post):

    class Count():
        def __init__(self):
            self.count = 0

    a = Count()

    def x(pst):
        for child in pst:
            if child.children:
                a.count += len(child.children)
                x(child.children)

    if len(post.comments) == 0: 
        return "discuss"
    else:
        a.count = len(post.comments)
        x(post.comments)

    if a.count == 1:
        return "1 comment"
    else:
        return str(a.count) + " comments"

    return a.count


def all_comment_ids_from_post(post):
    count = []
    def unwrap_children(pst):
        for child in pst:
            if child.children:
                [count.append(str(x.comment_id)) for x in child.children]
                unwrap_children(child.children)

    if len(post.comments) == 0:
        return count
    else:
        [count.append(str(x.comment_id)) for x in post.comments]
        unwrap_children(post.comments)

    return count



filter_out_media = ['instagram.com', 'www.instagram.com', 'instagr.am', 'youtube.com', 'www.youtube.com', 'www.vimeo.com', 'vimeo.com', 'twitpic.com', 'www.twitpic.com', 'i.imgur.com', 'www.yfrog.com', 'twitter.yfrog.com','twitter.com', 'imgur.com', 't.co', 'join.app.net', 'd.pr', 'www.mobypicture.com', 'i.appimg.net', 'foursquare.com', 'www.foursquare.com', 'www.path.com', 'path.com', 'cl.ly', 'm.youtube.com', 'mobile.twitter.com', 'alpha.app.net', 'alpha-api.app.net', 'appnetizens.com', 'jer.srcd.mp', 'm.flickr.com', 'patter-app.net', 'www.floodgap.com', 'img.ly', 'gunshowcomic.com', '25.media.tumblr.com'] 

newest_filter = ['instagram.com', 'www.instagram.com', 'instagr.am', 'twitpic.com', 'www.twitpic.com', 'i.imgur.com', 'www.yfrog.com', 'twitter.yfrog.com','twitter.com', 'imgur.com', 't.co', 'join.app.net', 'd.pr', 'www.mobypicture.com', 'i.appimg.net', 'foursquare.com', 'www.foursquare.com', 'www.path.com', 'path.com', 'cl.ly', 'm.youtube.com', 'mobile.twitter.com', 'alpha.app.net', 'alpha-api.app.net', 'appnetizens.com', 'jer.srcd.mp', 'm.flickr.com', 'patter-app.net', 'www.floodgap.com', 'img.ly'] 



def link_age_in_hours(lnk):
  created_at = lnk.date
  right_now = datetime.utcnow()
  link_age = right_now - created_at
  age_in_hours = (link_age.days)*24 + link_age.seconds/3600
  return age_in_hours

#minutes
def link_age_in_minutes(lnk):
    created_at = lnk.date
    right_now = datetime.utcnow()
    link_age = right_now - created_at
    age_in_minutes = link_age.seconds/60
    return age_in_minutes


def age(lnk):

    age_in_hours = link_age_in_hours(lnk)

    if age_in_hours >= 24:
      days = age_in_hours/24
      if age_in_hours < 48:
        return str(days) + " day ago"
      else:
        return str(days) + " days ago"
    else:
        if age_in_hours == 0:
            age_in_minutes = link_age_in_minutes(lnk)
            if age_in_minutes == 1:
                return str(age_in_minutes) + " minute ago"
            else:
                return str(age_in_minutes) + " minutes ago"
            
        if age_in_hours == 1:
            return str(age_in_hours) + " hour ago"
        else:
            return str(age_in_hours) + " hours ago"

def parent_post(comment):
    if comment.parent == None:
        return comment.post
    else:
        return parent_post(comment.parent)


def find_longest_url(a):
    longest = []

    for x in a:
        try:
            r = requests.get(x['url'])
            if not longest:
                if r.ok:
                    longest.append((r.url, r))
                else:
                    longest.append((x['url'], r))
            else:
                if r.ok:
                    if len(r.url) > len(longest[0][0]):
                        longest.pop(0)
                        longest.append((r.url, r))
                    else:
                        if len(x['url']) > len(longest[0][0]):
                            longest.pop(0)
                            longest.append((x['url'], r))
        except:
            if not longest:
                longest.append((x['url'], x['url']))    
            else:
                if len(x['url']) > len(longest[0][0]):
                    longest.pop(0)
                    longest.append((x['url'], x['url']))
        
    return longest[0]


def clean_comment_text(txt):
    """removes @username from a comment"""
    clean_text = re.sub(r'@\w+\s?', '', txt)
    return clean_text


def number_of_comments(comments_for_view):
    if comments_for_view == 'discuss':
        return 0
    else:
        count = comments_for_view.split(' ')[0]
        return int(count)
