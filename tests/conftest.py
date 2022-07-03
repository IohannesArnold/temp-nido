import pytest


from sqlalchemy.orm import sessionmaker, scoped_session

from nido import create_app
from nido.models import Base
from mock_data import seed_db


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
    db_session = app.Session()
    Base.metadata.bind = db_session.get_bind()
    Base.metadata.create_all()
    seed_db(db_session)

    yield db_session

    Base.metadata.drop_all()


@pytest.fixture()
def client(app, db):
    return app.test_client()


@pytest.fixture(scope="function")
def session(db):
    connection = db.get_bind().connect()
    transaction = connection.begin()
    yield scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
    transaction.rollback()
    connection.close()
