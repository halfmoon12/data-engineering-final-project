/* The script for designing the tables for project */

/*
Three entities were designed in the schema:
    - facility_information 
    - quality_ratings REFERENCES facility_information(facility_id)
    - facility_reports REFERENCES facility_information(facility_id)
It was designed based on the assumption that:
    - Unique facility/hosipital
    - Hospital one-to-many ratings (Yearly), unique ratings
    - Hospital one-to-may reports (Weekly), unique reports
It was not redundant since:
    1. No overlap columns in three entities except primary and foreign keys
    2. The geolocation information is in the facility_information so that
       we don't need excessive JOINS to get the information
*/

/* This table stores all information of a hospital */
CREATE TABLE facility_information (
    facility_id TEXT PRIMARY KEY,
    facility_name TEXT NOT NULL,
    -- We include all geographic information in the table avoid excessive JOINs
    lat NUMERIC,
    lon NUMERIC,
    address TEXT, 
    city TEXT,
    state CHAR(2),
    -- Assume zipcode are either 00000 or 00000-0000
    zipcode VARCHAR(10),
    -- fipscode are 00000
    fipscode CHAR(5),
    county TEXT
);

/* We assume there will be many quality ratings for one hospital, 
   And we would like to keeo track of the ratings. */
CREATE TABLE quality_ratings (
    rating_date DATE NOT NULL CHECK (rating_date <= NOW()),
    -- We stored the different ratings in this column
    rating NUMERIC,
    -- So we references to the facility_information table here
    facility_id TEXT REFERENCES facility_information(facility_id),
    -- Those three columns might change in future, so we kept them to be tracked
    facility_type TEXT,
    ownership TEXT,
    emergency_service TEXT,
    -- Use the combination of date and id as pk
    PRIMARY KEY (rating_date, facility_id)
);

/* We assume there will be many reports for one hospital, 
   And we would like to keeo track of the reports. */
CREATE TABLE facility_reports (
    report_date DATE CHECK (report_date <= NOW()),
    hospital_pk TEXT REFERENCES facility_information(facility_id),
    -- The total number of hospital beds available each week, 
    -- broken down into adult and pediatric (children) beds
    total_adult_hospital_beds NUMERIC CHECK (total_adult_hospital_beds >= 0),
    total_pediatric_hospital_beds NUMERIC CHECK (total_pediatric_hospital_beds >= 0),
    -- The number of hospital beds that are in use each week
    total_adult_hospital_beds_occupied NUMERIC 
        CHECK (total_adult_hospital_beds_occupied >= 0),
    total_pediatric_hospital_beds_occupied NUMERIC
        CHECK (total_pediatric_hospital_beds_occupied >= 0),
    -- The number of ICU (intensive care unit) beds available and the number in use
    total_icu_beds NUMERIC CHECK (total_icu_beds >= 0),
    total_icu_beds_occupied NUMERIC CHECK (total_icu_beds_occupied >= 0),
    -- The number of patients hospitalized who have confirmed COVID
    inpatient_beds_occupied_covid NUMERIC
        CHECK (inpatient_beds_occupied_covid >= 0),
    -- The number of adult ICU patients who have confirmed COVID
    adult_icu_patients_confirmed_covid NUMERIC 
        CHECK (adult_icu_patients_confirmed_covid >= 0),
    -- Use the combination of date and id as pk
    PRIMARY KEY (report_date, hospital_pk)
);