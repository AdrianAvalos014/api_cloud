# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os

# DATABASE_URL = os.getenv("postgresql://tasklife_user:c5m33k5lryh8JwrRbfYWJhFy6mSic98v@dpg-d7sps3bbc2fs73d0asug-a.oregon-postgres.render.com/tasklife")

# # 🔥 PostgreSQL (Render lo te dará)
# # DATABASE_URL = "postgresql://tasklife_user:c5m33k5lryh8JwrRbfYWJhFy6mSic98v@dpg-d7sps3bbc2fs73d0asug-a.oregon-postgres.render.com/tasklife"

# engine = create_engine(DATABASE_URL)

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# Base = declarative_base()



import psycopg2

DATABASE_URL = "postgresql://tasklife_user:c5m33k5lryh8JwrRbfYWJhFy6mSic98v@dpg-d7sps3bbc2fs73d0asug-a.oregon-postgres.render.com/tasklife"

def get_conn():
    return psycopg2.connect(DATABASE_URL)