from flask.ext.script import Manager

from adn_news import app, db
from adn import Adn

manager = Manager(app)


@manager.command
def create_database():
    """
    create the database
    """

    db.create_all()


@manager.command
def get_app_access_token():
    """
    Get an App Access Token for your app
    """

    adn_conn = Adn(client_id=app.client_id, client_secret=app.client_secret)

    print
    print adn_conn.getClientToken()
    print


if __name__ == "__main__":
    manager.run()
