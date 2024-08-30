from app import db

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    timestamp_utc = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), nullable=False)

class BusinessHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time_local = db.Column(db.Time, nullable=False)
    end_time_local = db.Column(db.Time, nullable=False)

class StoreStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    timestamp_utc = db.Column(db.DateTime, nullable=False)

class TimeZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    timezone_str = db.Column(db.String(50), nullable=False)
