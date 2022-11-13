"""Module for loading reports data into DB"""

import sys

import pandas as pd
import psycopg

from credentials import DB_PASSWORD, DB_USER

# Connect to DB
conn = psycopg.connect(
    host='sculptor.stat.cmu.edu', dbname=DB_USER,
    user=DB_USER, password=DB_PASSWORD
)
cur = conn.cursor()

# Load data from terminal input
data = pd.read_csv('data/quality/' + sys.argv[2])

# Get existing hospitals/facilities id
# Seem that pd.read_sql doesn't work
cur.execute("SELECT facility_id FROM facility_information")
facility_ids = pd.DataFrame(cur.fetchall())
conn.commit()        # Commit here for the SELECT clause

# Target variables
target = ["Facility ID", "Facility Name", "Hospital Type",
          "Emergency Services", "Address", "City", "State",
          "ZIP Code", "County Name", "Hospital overall rating"]

# Hashed so serach faster
existing_ids = set(facility_ids[0]) if len(facility_ids) > 0 else {}

# Start transaction
with conn.transaction():
    # Create counting variables
    num_info_inserted = 0
    num_info_updated = 0
    num_quality_inserted = 0

    for index, row in data.iterrows():
        # First extract our target variables
        (facility_id, facility_name, facility_type, emergency_service,
         address, city, state, zipcode, county, rating) = row[target]

        # Change rating to None if Not Avaliable
        if (rating == "Not Available"):
            rating = None

        # If the hospital is new
        if (facility_id not in existing_ids):
            # INSERT INTO facility_information
            try:
                # Make a new SAVEPOINT
                with conn.transaction():
                    # Only insert when not in table
                    cur.execute("INSERT INTO facility_information ("
                                "facility_id, facility_name, facility_type, "
                                "emergency_service, address, city, "
                                "state, zipcode, county"
                                ") VALUES ("
                                "%(facility_id)s, %(facility_name)s, "
                                "%(facility_type)s, %(emergency_service)s, "
                                "%(address)s, %(city)s, %(state)s, "
                                "%(zipcode)s, %(county)s"
                                ");",
                                {
                                    "facility_id": facility_id,
                                    "facility_name": facility_name,
                                    "facility_type": facility_type,
                                    "emergency_service": emergency_service,
                                    "address": address,
                                    "city": city,
                                    "state": state,
                                    "zipcode": zipcode,
                                    "county": county
                                })
            # If exception caught (any), rollback
            except Exception as e:
                print("Insertion into facility_information failed at row " +
                      str(index) + ":", e)
                data.iloc[index].to_csv("error_row.csv")
            else:
                num_info_inserted += 1

        # If the hospital is not new
        else:
            # Update facility_information
            try:
                # Make a new SAVEPOINT
                with conn.transaction():
                    cur.execute("UPDATE facility_information "
                                "SET facility_type = %(facility_type)s, "
                                "emergency_service = %(emergency_service)s, "
                                "state = %(state)s, "
                                "county = %(county)s "
                                "WHERE facility_id = %(facility_id)s;",
                                {
                                    "facility_type": facility_type,
                                    "emergency_service": emergency_service,
                                    "state": state,
                                    "county": county,
                                    "facility_id": facility_id
                                })

            # If exception caught (any), rollback
            except Exception as e:
                print("Insertion into facility_information failed at row " +
                      str(index) + ":", e)
                data.iloc[index].to_csv("error_row.csv")

            else:
                num_info_updated += 1

        # Then INSERT INTO quality_ratings
        try:
            # Make a new SAVEPOINT
            with conn.transaction():
                cur.execute("INSERT INTO quality_ratings ("
                            "rating_date, rating, facility_id"
                            ") VALUES ("
                            "TO_DATE(%(rating_date)s, 'YYYY-MM-DD'), "
                            "%(rating)s, %(facility_id)s"
                            ");",
                            {"rating_date": sys.argv[1], "rating": rating,
                             "facility_id": facility_id})
        except Exception as e:
            print("Insertion into quality_ratings failed at row " +
                  str(index) + ":", e)
            data.iloc[index].to_csv("error_row.csv")
        else:
            # No exception happened, so we continue
            num_quality_inserted += 1

# now we commit the entire transaction
conn.commit()
print("Number of rows inserted into facility_information:", num_info_inserted)
print("Number of rows updated in facility_information:", num_info_updated)
print("Number of rows inserted into quality_ratings:", num_quality_inserted)
