-- create_job_portal_db.sql

-- Table for Employers
CREATE TABLE IF NOT EXISTS employer (
    ID VARCHAR(10) PRIMARY KEY,
    COMPANY VARCHAR(100) NOT NULL UNIQUE,
    INDUSTRY VARCHAR(100) NOT NULL,
    LOCATION VARCHAR(100) NOT NULL,
    Website TEXT UNIQUE,
    contactperson VARCHAR(100) NOT NULL,
    phoneNo INT(10) NOT NULL UNIQUE
);

-- Table for Job Listings
CREATE TABLE IF NOT EXISTS joblisting (
    ID VARCHAR(10) PRIMARY KEY,
    job VARCHAR(100) NOT NULL,
    compID VARCHAR(10) NOT NULL UNIQUE,
    description TEXT,
    requirement TEXT NOT NULL,
    location VARCHAR(100) NOT NULL,
    salary INT(10) NOT NULL,
    status CHAR(1) NOT NULL,
    dateposted DATE NOT NULL,
    FOREIGN KEY (compID) REFERENCES employer(ID)
);

-- Table for Skills
CREATE TABLE IF NOT EXISTS skill (
    ID VARCHAR(10) PRIMARY KEY,
    skill TEXT NOT NULL,
    description TEXT NOT NULL
);

-- Table for Job Applications
CREATE TABLE IF NOT EXISTS job_application (
    ID VARCHAR(10) PRIMARY KEY,
    jobID VARCHAR(10) NOT NULL UNIQUE,
    jobseekerID VARCHAR(10) NOT NULL UNIQUE,
    applicationdate DATE NOT NULL,
    status CHAR(1) NOT NULL,
    coverletter TEXT NOT NULL,
    FOREIGN KEY (jobID) REFERENCES joblisting(ID),
    FOREIGN KEY (jobseekerID) REFERENCES jobseeker(ID)
);

-- Table for Education
CREATE TABLE IF NOT EXISTS education (
    ID VARCHAR(10) PRIMARY KEY,
    Degree_Name VARCHAR(20) NOT NULL,
    Institute VARCHAR(20) NOT NULL,
    Year_of_Completion CHAR(4) NOT NULL
);

-- Table for Experience
CREATE TABLE IF NOT EXISTS experience (
    ID VARCHAR(10) PRIMARY KEY,
    Job_Title VARCHAR(20) NOT NULL,
    Company_Name VARCHAR(20) NOT NULL,
    Start_Date CHAR(8) NOT NULL,
    End_Date CHAR(8) NOT NULL,
    Description VARCHAR(100) NOT NULL
);

-- Table for Location
CREATE TABLE IF NOT EXISTS location (
    ID VARCHAR(10) PRIMARY KEY,
    Location_Name VARCHAR(20) NOT NULL,
    City VARCHAR(20) NOT NULL,
    State VARCHAR(20) NOT NULL,
    Country VARCHAR(20) NOT NULL
);

-- Table for Users
CREATE TABLE IF NOT EXISTS users (
    ID VARCHAR(10) PRIMARY KEY,
    Username VARCHAR(30) NOT NULL,
    Email VARCHAR(20) NOT NULL,
    Password VARCHAR(50) NOT NULL
);
