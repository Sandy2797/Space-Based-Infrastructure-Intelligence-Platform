from app.db.database import Base, engine
from app.models.satellite_image import SatelliteImageDB
from app.models.detection import DetectionDB

def initialize_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print("Database tables created successfully.")