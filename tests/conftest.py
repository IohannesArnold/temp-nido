import pytest

from nido import create_app
from nido.models import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "VERY_SECRET",
        }
    )

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    _db.app = app
    _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture()
def client(app, db):
    return app.test_client()


@pytest.fixture(scope="function")
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()
