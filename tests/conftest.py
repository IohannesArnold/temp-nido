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
            "DATABASE_URL": "sqlite:///:memory:",
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
    Base.metadata.create_all(bind=db_session.get_bind())
    seed_db(db_session)

    yield db_session

    Base.metadata.drop_all(bind=db_session.get_bind())


@pytest.fixture(scope="function")
def session(db):
    connection = db.get_bind().connect()
    transaction = connection.begin()
    yield scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(app, session):
    app.Session = session
    return app.test_client()
