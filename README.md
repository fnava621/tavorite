# Hacker News for App Dot Net - www.tavorite.com

# Quick Start Instructions

1. Create a venv `virtualenv --no-site-packages venv`
1. Activate your environment `source venv/bin/activate`
1. install the packages `pip install -r requirements.txt`
1. Add some information to your environment in development it might be easier to use sqlite

```sh
export DATABASE_URL="sqlite:///test.db"
export APP_SECRET_KEY="<Your Secret Key>"
export ACCESS_TOKEN="<Your Access Token>"
```

* Once you have all the information in your enviroment you can now create the database. Open a shell.

```sh
python manage.py create_database
```

* Now your DB should be created
* Next you can run the dev server `python adn_news.py`
* And now you should be able to visit http://127.0.0.1:5000 to see your site running

# Streaming Quick Start

To use streaming_update.py you need to get an App Access Token, and build a stream object. You can find more information about [App Access Tokens](https://github.com/appdotnet/api-spec/blob/master/auth.md#app-access-token-flow), and the [Streaming API](https://github.com/appdotnet/api-spec/blob/master/resources/streams.md) on App.net's developer wiki.

1. Get our App Access Token: `python manage.py get_app_access_token`
1. Put that in your enviroments: `export APP_ACCESS_TOKEN="<App Access Token>"`
1. Now you can run streaming_update.py: `python streaming_update.py`

# Contributors 

* Alex Kessinger - [@voidfiles](http://alpha.app.net/voidfiles)
* Fernando Nava  - [@nava](http://alpha.app.net/nava)