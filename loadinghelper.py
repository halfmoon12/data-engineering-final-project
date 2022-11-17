"""Helper module for loading-data"""

import pandas as pd


# Helper function for checking numeric NA values
def check_numeric_na(var):
    """Check if the input variable is negative value or NaN"""
    return None if var < 0 else var


def check_geo(var):
    if pd.isna(var):
        return None, None
    else:
        return float(var.split(" ")[1][1:]), float(var.split(" ")[2][:-1])


def check_rating(var):
    return None if var == "Not Available" else var


def get_existing_ids(cur, conn):
    # Get existing hospitals/facilities id
    # Seem that pd.read_sql doesn't work
    cur.execute("SELECT facility_id FROM facility_information")
    facility_ids = pd.DataFrame(cur.fetchall())
    conn.commit()        # Commit here for the SELECT clause
    # Hashed so serach faster
    return set(facility_ids[0]) if len(facility_ids) > 0 else {}