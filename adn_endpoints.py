base_url = "https://alpha-api.app.net"

api_table = {

    'getUser': {
        'url': '/stream/0/users/{{user_id}}',
        'method': 'GET',
        },

    'getSelf': {
        'url': '/stream/0/users/me',
        'method': 'GET',
        },

    'followUser': {
        'url': '/stream/0/users/{{user_id}}/follow',
        'method': 'POST',
        },
    
    'unfollowUser': {
        'url':'/stream/0/users/{{user_id}}/follow',
        'method': 'DELETE',
        },
 
    'usersFollows': {
        'url': '/stream/0/users/{{user_id}}/following',
        'method': 'GET',
        },

    'followingUser': {
        'url': '/stream/0/users/{{user_id}}/followers',
        'method': 'GET',
        },
    
    'muteUser': {
        'url': '/stream/0/users/{{user_id}}/mute',
        'method': 'POST',
        },
    
    'unmuteUser': {
        'url': '/stream/0/users/{{user_id}}/mute',
        'method': 'DELETE',
        },

    'mutedUsers': {
        'url': '/stream/0/users/me/muted',
        'method': 'GET',
        },
    
    'searchForUsers': {
        'url': '/stream/0/users/search',
        'method': 'GET',
        },
    
    'repostersOfPost': {
        'url': '/stream/0/posts/{{post_id}}/reposters',
        'method': 'GET',
        },

    'starredPost': {
        'url': '/stream/0/posts/{{post_id}}/stars',
        'method': 'GET',
        },

    'checkToken': {
        'url': '/stream/0/token',
        'method': 'GET',
        },
    
    'createPost': {
      'url': '/stream/0/posts',
      'method': 'POST',
        },

    'retrievePost': {
        'url': '/stream/0/posts/{{post_id}}',
        'method': 'GET',
        },

    'deletePost': {
        'url': '/stream/0/posts/{{post_id}}',
        'method': 'DELETE',
        },

    'repliesToPost': {
        'url': '/stream/0/posts/{{post_id}}/replies',
        'method': 'GET',
        },

    'postsCreatedByUser': {
        'url': '/stream/0/users/{{user_id}}/posts',
        'method': 'GET',
        },
    
    'repostPost': {
        'url': '/stream/0/posts/{{post_id}}/repost',
        'method': 'POST',
        },
    
    'unrepostPost': {
        'url': '/stream/0/posts/',
        'method': 'DELETE',
        },

    'starPost': {
        'url': '/stream/0/posts/{{post_id}}/star',
        'method': 'POST',
        },

    'unstarPost': {
        'url': '/stream/0/posts/{{post_id}}/star',
        'method': 'DELETE',
        },

    'postsStarredByUser': {
        'url': '/stream/0/users/{{user_id}}/stars',
        'method': 'GET',
        },
    
    'postsMentioningUser': {
        'url': '/stream/0/users/{{user_id}}/mentions',
        'method': 'GET',
        },

    'userStream': {
        'url': '/stream/0/posts/stream',
        'method': 'GET',
        },

    'globalStream': {
        'url': '/stream/0/posts/stream/global',
        'method': 'GET',
        },

    'taggedPosts': {
        'url': '/stream/0/posts/tag/{{hashtag}}',
        'method': 'GET',
        },

    # Streams, Filters, Realtime updates coming soon

    
}


