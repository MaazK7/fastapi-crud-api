from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import create_engine


DATABASE_URL = "sqlite:///sql_app.db"


engine = create_engine(url=DATABASE_URL)


Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
