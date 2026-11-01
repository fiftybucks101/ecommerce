
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.sessions import get_db
from app.main import app

# Import every model so SQLAlchemy knows about all tables.
from app.users.models import User
from app.products.models import Product, Category
from app.cart.models import Cart, CartItem

from app.auth.dependencies import get_current_user


# --------------------------------------------------
# 1. Test database engine
# --------------------------------------------------

test_engine = create_engine(
    settings.TEST_DATABASE_URL,
    echo=False,
)


# --------------------------------------------------
# 2. Create test database tables
# --------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


# --------------------------------------------------
# 3. Database session with transaction rollback
# --------------------------------------------------

@pytest.fixture
def db_session():
    connection = test_engine.connect()

    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        class_=Session,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# --------------------------------------------------
# 4. Override FastAPI database dependency
# --------------------------------------------------

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# --------------------------------------------------
# 5. Create a test customer
# --------------------------------------------------

@pytest.fixture
def test_user(db_session):
    user = User(
        name="Test Customer",
        email="customer@test.com",
        password_hash="not-used-in-this-test",
        role="customer",
    )

    db_session.add(user)
    db_session.flush()

    return user


# --------------------------------------------------
# 6. Authenticated test client
# --------------------------------------------------

@pytest.fixture
def authenticated_client(client, test_user):
    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    yield client

    app.dependency_overrides.pop(get_current_user, None)


# --------------------------------------------------
# 7. Create an admin user & client
# --------------------------------------------------

@pytest.fixture
def admin_user(db_session):
    user = User(
        name="Test Admin",
        email="admin@test.com",
        password_hash="not-used-in-this-test",
        role="admin",
    )

    db_session.add(user)
    db_session.flush()

    return user


@pytest.fixture
def admin_client(client, admin_user):
    def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    yield client

    app.dependency_overrides.pop(get_current_user, None)


# --------------------------------------------------
# 8. Create a test category & product
# --------------------------------------------------

@pytest.fixture
def test_category(db_session):
    category = Category(
        name="Test Category",
    )

    db_session.add(category)
    db_session.flush()

    return category


@pytest.fixture
def test_product(db_session, test_category):
    product = Product(
        name="Test Product",
        description="Product created for automated testing",
        price=Decimal("25.00"),
        stock=10,
        category_id=test_category.id,
    )

    db_session.add(product)
    db_session.flush()

    return product
