from app.database import Base, engine

print("Creating database...")
Base.metadata.create_all(bind=engine)
print("Database created.")
