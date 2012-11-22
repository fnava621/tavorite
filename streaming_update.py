import requests
import pprint
from adn_news import *
from helpers import *
from adn import Adn
from update import process_post, reduce_score_with_time

app_adn_conn = Adn(access_token=os.environ['APP_ACCESS_TOKEN'])


FILTER_NAME = 'Posts with links'
FILTER_OBJECT = json.dumps({
    "match_policy": "include_any",
    "clauses": [{
        "operator": "matches",
        "field": "/data/post/entities/links/*/url",
        "object_type": "star",
        "value": "http"
    }],
    "name": FILTER_NAME
})

STREAM_OBJECT = {
    "object_types": [
        "post",
        "star",
    ],
    "type": "long_poll",
    "key": "link_stream"
}


def handle_control(obj):
    print 'got a control object'


def handle_post(obj):
    process_post(obj['data'])
    print 'collecting a post'


def handle_reply(obj):
    print 'We got a reply'


def handle_star(obj):
    print 'collected a star'


def handle_repost(obj):
    print 'collected a repost'


def handle_new(obj):
    print 'new obj'


def start_listening():
    """Automates listening to the streaming api"""

    # Have we created the filter we need
    # We need to create filters as a user
    response = tavorite.filters()
    filter_id = None
    if response['data']:
        for _filter in response['data']:
            if _filter['name'] == FILTER_NAME:
                filter_id = _filter['id']

    if not filter_id:
        print "We need to create a filter first"
        response = tavorite.filters(method='POST', params=FILTER_OBJECT)
        filter_id = response['data']['id']

    print 'Filter ID: %s' % (filter_id)
    # STREAM_OBJECT['filter_id'] = filter_id
    # app_adn_conn.streams(method="DELETE")
    # exit()
    # Have we already created a stream
    response = app_adn_conn.streams(params={'key': 'link_stream'})
    if not response['data']:  # If we don't have any streams make one
        print "we need to create a stream"
        response = app_adn_conn.streams(method="POST",
                                        params=json.dumps(STREAM_OBJECT))
        stream_endpoint = response['data']['endpoint']
    else:
        stream_endpoint = response['data'][0]['endpoint']
    print "Fetching requests from %s" % (stream_endpoint)
    pprint.pprint(response)
    resp = requests.get(stream_endpoint, prefetch=False)
    i = 0
    for line in resp.iter_lines():
        if line:  # filter out keep-alive new lines
            i += 1
            line.strip()
            obj = json.loads(line)
            print
            print
            pprint.pprint(obj)
            if obj['meta']['type'] == 'control':
                handle_control(obj)
            elif obj['meta']['type'] == 'post':
                if 'reply_to' in obj['data'].keys():
                    handle_reply(obj)
                else:
                    handle_post(obj)
            elif obj['meta']['type'] == 'star':
                handle_star(obj)
            elif obj['meta']['type'] == 'repost':
                handle_repost(obj)
            else:
                handle_new(obj)
            print
            print
            del obj

            # Right now every 10 lines lets update the scores
            if i % 10 == 0:
                reduce_score_with_time()


if __name__ == '__main__':
    start_listening()
