from flask.ext.wtf import Form, TextField, Required, validators, TextAreaField

class SubmitForm(Form):
    title = TextField("Title", [validators.Length(min=4, message="Little short for a headline?"), validators.Required()])
    url = TextField("Url", [validators.Length(min=4, message="Little short for a url?"), validators.Required()])


class CommentForm(Form):
    comment = TextAreaField('Comments', [validators.Length(min=4, max=256), validators.Required()]) 


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
        return 0
    else:
        a.count = len(post.comments)
        x(post.comments)




#HEROKU CONFIG
CLIENT_ID = 'sDndZTeGWmmd5tYEyRmm5WA6wpSdDBse'
CLIENT_SECRET = 'jKPDXPHLPqdC49p6RqARTk5EwJWknJpW'
REDIRECT_URL = 'http://127.0.0.1:5000/oauth/complete'
ACCESS_TOKEN = 'AQAAAAAAAYmXp4Y26LOMsXwCGD9D2HajHMphN9PmTRlGeJWbwCc42Tikgn9YL5gBipybAiNeED35Wttje7K0y7HLbN-GkCigtA'


app_adn = Adn(access_token=ACCESS_TOKEN, client_id= CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

filter_out_media = ['instagram.com', 'www.instagram.com', 'instagr.am', 'youtube.com', 'www.youtube.com', 'www.vimeo.com', 'vimeo.com', 'twitpic.com', 'www.twitpic.com', 'i.imgur.com', 'www.yfrog.com', 'twitter.yfrog.com','twitter.com', 'imgur.com', 't.co', 'join.app.net', 'd.pr', 'www.mobypicture.com', 'i.appimg.net', 'foursquare.com', 'www.foursquare.com', 'www.path.com', 'path.com', 'cl.ly', 'm.youtube.com', 'mobile.twitter.com', 'alpha.app.net', 'alpha-api.app.net', 'appnetizens.com', 'jer.srcd.mp', 'm.flickr.com', 'patter-app.net'] 
