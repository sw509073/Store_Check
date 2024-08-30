import sys
import os
import pandas as pd
from sqlalchemy import and_
from flask import Flask
from app import create_app, db
from app.models import Store, BusinessHours, TimeZone
from datetime import datetime, timedelta
import pytz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = create_app()

def ingest_store_data(store_data_csv):
    with app.app_context():
        try:
            df = pd.read_csv(store_data_csv)
            print("Store Data CSV loaded successfully.")
            for _, row in df.iterrows():
                timestamp = row['timestamp_utc']
                try:
                    parsed_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f UTC')
                    timestamp_utc = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    parsed_timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S UTC')
                    timestamp_utc = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')

                store = Store(
                    store_id=row['store_id'],
                    timestamp_utc=timestamp_utc,
                    status=row['status']
                )
                db.session.add(store)
            db.session.commit()
            print("Store data ingested successfully.")
        except Exception as e:
            print(f"Error ingesting store data: {e}")

def ingest_business_hours(business_hours_csv):
    with app.app_context():
        try:
            df = pd.read_csv(business_hours_csv)
            print("Business Hours CSV loaded successfully.")
            for _, row in df.iterrows():
                business_hour = BusinessHours(
                    store_id=row['store_id'],
                    day_of_week=row['day'],
                    start_time_local=row['start_time_local'],
                    end_time_local=row['end_time_local']
                )
                db.session.add(business_hour)
            db.session.commit()
            print("Business hours data ingested successfully.")
        except Exception as e:
            print(f"Error ingesting business hours data: {e}")

def ingest_timezones(timezones_csv):
    with app.app_context():
        try:
            df = pd.read_csv(timezones_csv)
            print("Timezones CSV loaded successfully.")
            for _, row in df.iterrows():
                timezone = TimeZone(
                    store_id=row['store_id'],
                    timezone_str=row['timezone_str']
                )
                db.session.add(timezone)
            db.session.commit()
            print("Timezone data ingested successfully.")
        except Exception as e:
            print(f"Error ingesting timezone data: {e}")

def process_uptime_downtime():
    with app.app_context():
        try:
            stores = Store.query.all()
            if not stores:
                print(f"No stores found.")
                return []

            print(f"Processing a all stores.")
            report_data = []
            
            current_time = max([store.timestamp_utc for store in Store.query.all()]).replace(tzinfo=pytz.UTC)

            for store in stores:
                # print(f"Processing Store ID: {store.store_id}")

                timezone_entry = TimeZone.query.filter_by(store_id=store.store_id).first()
                if not timezone_entry:
                    # print(f"No timezone entry found for Store ID: {store.store_id}. Skipping store.")
                    continue
                
                store_tz = pytz.timezone(timezone_entry.timezone_str)
                # print(f"Store ID: {store.store_id} timezone: {store_tz}")

                business_hours = BusinessHours.query.filter_by(store_id=store.store_id).all()
                # print(f"Store ID: {store.store_id} has {len(business_hours)} business hours entries.")

                statuses = Store.query.filter_by(store_id=store.store_id).order_by(Store.timestamp_utc).all()
                # print(f"Store ID: {store.store_id} has {len(statuses)} status logs.")

                for status in statuses:
                    status.timestamp_utc = pytz.utc.localize(status.timestamp_utc)

                intervals = {
                    "last_hour": timedelta(hours=1),
                    "last_day": timedelta(days=1),
                    "last_week": timedelta(weeks=1)
                }

                results = {
                    "uptime_last_hour": timedelta(0),
                    "uptime_last_day": timedelta(0),
                    "uptime_last_week": timedelta(0),
                    "downtime_last_hour": timedelta(0),
                    "downtime_last_day": timedelta(0),
                    "downtime_last_week": timedelta(0)
                }

                for interval_name, interval in intervals.items():
                    interval_start = current_time - interval

                    total_uptime = timedelta(0)
                    total_downtime = timedelta(0)

                    for day_hours in business_hours:
                        # print(f"Processing business hours for day {day_hours.day_of_week}: {day_hours.start_time_local} to {day_hours.end_time_local}")
                        
                        start_time = day_hours.start_time_local
                        end_time = day_hours.end_time_local
                        
                        day_statuses = [status for status in statuses if status.timestamp_utc.weekday() == day_hours.day_of_week and interval_start <= status.timestamp_utc <= current_time]
                        # print(f"Store ID: {store.store_id} has {len(day_statuses)} statuses for weekday {day_hours.day_of_week} within {interval_name}.")

                        if not day_statuses:
                            # print(f"No status logs found for Store ID: {store.store_id} on weekday {day_hours.day_of_week}.")
                            continue
                        
                        day_start = datetime.combine(day_statuses[0].timestamp_utc.date(), start_time)
                        day_end = datetime.combine(day_statuses[0].timestamp_utc.date(), end_time)
                        
                        day_start = store_tz.localize(day_start)
                        day_end = store_tz.localize(day_end)
                        
                        day_start_utc = day_start.astimezone(pytz.utc)
                        day_end_utc = day_end.astimezone(pytz.utc)

                        # print(f"Business Hours in UTC: {day_start_utc} to {day_end_utc}")

                        within_hours = [status for status in day_statuses if day_start_utc <= status.timestamp_utc <= day_end_utc]
                        # print(f"Store ID: {store.store_id} has {len(within_hours)} statuses within business hours.")

                        if len(within_hours) < 2:
                            # print(f"Insufficient statuses within business hours for Store ID: {store.store_id}.")
                            continue
                        
                        for i in range(1, len(within_hours)):
                            status = within_hours[i]
                            prev_status = within_hours[i-1]
                            duration = status.timestamp_utc - prev_status.timestamp_utc
                            
                            if prev_status.status == 'active':
                                total_uptime += duration
                            else:
                                total_downtime += duration

                            # print(f"Duration between statuses: {duration} | Status: {prev_status.status}")
                    
                    results[f"uptime_{interval_name}"] = total_uptime.total_seconds() / 60 if "hour" in interval_name else total_uptime.total_seconds() / 3600
                    results[f"downtime_{interval_name}"] = total_downtime.total_seconds() / 60 if "hour" in interval_name else total_downtime.total_seconds() / 3600

                report_data.append({
                    "store_id": store.store_id,
                    "uptime_last_hour": results["uptime_last_hour"],
                    "uptime_last_day": results["uptime_last_day"],
                    "uptime_last_week": results["uptime_last_week"],
                    "downtime_last_hour": results["downtime_last_hour"],
                    "downtime_last_day": results["downtime_last_day"],
                    "downtime_last_week": results["downtime_last_week"]
                })
                # print("Processed data:", report_data)
        
        except Exception as e:
            print(f"Error processing uptime/downtime: {e}")
        
        return report_data


# if __name__ == "__main__":
#     # Set the paths to your CSV files
#     store_data_csv = 'data/store_data.csv'
#     business_hours_csv = 'data/business_hours.csv'
#     timezones_csv = 'data/timezones.csv'
    
#     # Uncomment these lines to ingest data
#     # ingest_store_data(store_data_csv)
#     # ingest_business_hours(business_hours_csv)
#     # ingest_timezones(timezones_csv)

#     process_uptime_downtime()
