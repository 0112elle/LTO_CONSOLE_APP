-- CMSC 127 - ST15L
-- Project Milestone 3

-- -- For creating (if not yet existing) or replacing (if already existing) a user for the LTO system
-- CREATE OR REPLACE USER 'ltodirector'@'localhost' IDENTIFIED BY 'lto';

-- In case na mag-error due to access denied, go to root user then grant all privileges to ltodirector using the statement below:
-- GRANT ALL PRIVILEGES ON lto.* TO 'ltodirector'@'localhost';
-- We just dropped any already-existing so that there would be no conflict with this SQL file.
DROP DATABASE IF EXISTS `lto`;
-- This creates a new database for the LTO system
CREATE DATABASE IF NOT EXISTS `lto`;
-- GRANT ALL ON lto.* TO 'ltodirector'@'localhost';
USE `lto`;

-- DRIVER(Driver_id, First_name, Middle_name, Last_name, Suffix, Date_of_birth, Weight, Height, Sex_assigned_at_birth, Nationality, Civil_status, Contact_number, Blood_type, House_number, Street_village, Barangay, City_municipality, Province, Region, Zip_code)
-- DRIVER table (address fields embedded, age derived from DOB)
-- All 'NOT NULL' attributes are required in the LTO driver's license.
CREATE TABLE DRIVER ( 
    Driver_id       INT AUTO_INCREMENT PRIMARY KEY,
    First_name      VARCHAR(50) NOT NULL,
    Middle_name     VARCHAR(50),
    Last_name       VARCHAR(50) NOT NULL,
    Suffix          VARCHAR(10),
    Date_of_birth   DATE NOT NULL,
    Weight          DECIMAL(5,2) NOT NULL,   -- in kg
    Height          DECIMAL(5,2) NOT NULL,   -- in cm
    Sex_assigned_at_birth ENUM('Male','Female','Other') NOT NULL,
    Nationality     VARCHAR(50) DEFAULT 'Filipino',
    Civil_status ENUM('Single','Married','Divorced','Widowed') NOT NULL,
    Contact_number  VARCHAR(11) NOT NULL,
    Blood_type      VARCHAR(3) NOT NULL,
    House_number    VARCHAR(4) NOT NULL,
    Street_village  VARCHAR(100) NOT NULL,
    Barangay        VARCHAR(100) NOT NULL,
    City_municipality VARCHAR(100) NOT NULL,
    Province        VARCHAR(100) NOT NULL,
    Region          VARCHAR(100) NOT NULL,
    Zip_code        VARCHAR(4) NOT NULL
);

-- LICENSE(License_number, License_type, License_status, License_issue_date, License_expiry_date, Driver_id)
-- LICENSE (current license of a driver)
CREATE TABLE LICENSE (
    License_number VARCHAR(13) PRIMARY KEY,
    License_type ENUM('Student Permit','Non-Professional','Professional') NOT NULL,
    License_status ENUM('valid','expired','suspended','revoked') NOT NULL,
    License_issue_date DATE NOT NULL,
    License_expiry_date DATE NOT NULL,
    Driver_id INT NOT NULL,
    FOREIGN KEY (Driver_id) REFERENCES DRIVER(Driver_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_license_driver (Driver_id),
    INDEX idx_license_status (License_status),
    INDEX idx_license_expiry (License_expiry_date)
);

-- LICENSE_DLCODES(License_number, Dl_codes)
CREATE TABLE LICENSE_DLCODES (
    License_number VARCHAR(13) NOT NULL,
    Dl_codes VARCHAR(10) NOT NULL,
    PRIMARY KEY (License_number, Dl_codes),
    FOREIGN KEY (License_number) REFERENCES LICENSE(License_number) ON DELETE CASCADE ON UPDATE CASCADE
);

-- LICENSE_CONDITION(License_number, Condition)
CREATE TABLE LICENSE_CONDITION (
    License_number VARCHAR(13) NOT NULL,
    `Condition` VARCHAR(100) NOT NULL,
    PRIMARY KEY (License_number, `Condition`),
    FOREIGN KEY (License_number) REFERENCES LICENSE(License_number) ON DELETE CASCADE ON UPDATE CASCADE
);

-- VEHICLE(Vehicle_id, Engine_number, Plate_number, Chassis_number, Vehicle_type, Make, Model, Year, Body_type, Capacity, Color, Driver_id)
CREATE TABLE VEHICLE (
    Vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    Engine_number VARCHAR(12) UNIQUE NOT NULL,
    Plate_number VARCHAR(7) UNIQUE NOT NULL,
    Chassis_number VARCHAR(17) UNIQUE NOT NULL,
    Vehicle_type ENUM('motorcycle','private car','public utility vehicle','truck','others') NOT NULL,
    Make VARCHAR(50) NOT NULL,
    Model VARCHAR(50) NOT NULL,
    Year INT NOT NULL,
    Body_type VARCHAR(50),
    Capacity INT,   -- passenger capacity or engine displacement?
    Color VARCHAR(30) NOT NULL,
    Driver_id INT NOT NULL,   -- current registered owner
    FOREIGN KEY (Driver_id) REFERENCES DRIVER(Driver_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_vehicle_owner (Driver_id),
    INDEX idx_plate (Plate_number)
);

-- VEHICLE_REGISTRATION(Registration_number, Registration_date, Expiration_date, Registration_status, Official_receipt_number, Official_receipt_date, Document_ref_no, Ownership_type, Transfer_reason, Ownership_start_date, Ownership_end_date, Vehicle_id)
CREATE TABLE VEHICLE_REGISTRATION (
    Registration_number VARCHAR(10) PRIMARY KEY,
    Registration_date DATE NOT NULL,
    Expiration_date DATE NOT NULL,
    Registration_status ENUM('active','expired','suspended') NOT NULL,
    Official_receipt_number VARCHAR(10) NOT NULL,
    Official_receipt_date DATE NOT NULL,
    Document_ref_no VARCHAR(50),
    Ownership_type ENUM('owned','financed','leased') NOT NULL,
    Transfer_reason VARCHAR(255),
    Ownership_start_date DATE NOT NULL,
    Ownership_end_date DATE,
    Vehicle_id INT NOT NULL,
    FOREIGN KEY (Vehicle_id) REFERENCES VEHICLE(Vehicle_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_reg_vehicle (Vehicle_id),
    INDEX idx_reg_expiration (Expiration_date),
    INDEX idx_reg_status (Registration_status)
);

-- TRAFFIC_VIOLATION_TYPE(Violation_type_id, Name, Base_fine, Description)
CREATE TABLE TRAFFIC_VIOLATION_TYPE (
    Violation_type_id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL UNIQUE,
    Base_fine DECIMAL(10,2) NOT NULL,
    Description TEXT
);

-- OFFICER(Officer_id, Station, Rank, Badge_number, First_name, Middle_name, Last_name, Suffix)
CREATE TABLE OFFICER (
    Officer_id INT AUTO_INCREMENT PRIMARY KEY,
    Station VARCHAR(100) NOT NULL,
    Rank VARCHAR(50) NOT NULL,
    Badge_number VARCHAR(20) UNIQUE NOT NULL,
    First_name VARCHAR(50) NOT NULL,
    Middle_name VARCHAR(50),
    Last_name VARCHAR(50) NOT NULL,
    Suffix VARCHAR(10)
);

-- LOCATION(Location_id, City, Region)
CREATE TABLE LOCATION (
    Location_id INT AUTO_INCREMENT PRIMARY KEY,
    City VARCHAR(100) NOT NULL,
    Region VARCHAR(100) NOT NULL,
    -- optionally add street/barangay if needed
    INDEX idx_location_city (City),
    INDEX idx_location_region (Region)
);

-- TRAFFIC_VIOLATION(Violation_id, Violation_date, Violation_status, Fine_amount, Payment_date, Driver_id, Vehicle_id, Violation_type_id, Officer_id, Location_id)
CREATE TABLE TRAFFIC_VIOLATION (
    Violation_id INT(6) AUTO_INCREMENT PRIMARY KEY,
    Violation_date DATE NOT NULL,
    Violation_status ENUM('unpaid','paid','contested') NOT NULL,
    Fine_amount DECIMAL(10,2) NOT NULL,
    Payment_date DATE,
    Driver_id INT NOT NULL,
    Vehicle_id INT NOT NULL,
    Violation_type_id INT NOT NULL,
    Officer_id INT NOT NULL,
    Location_id INT NOT NULL,
    FOREIGN KEY (Driver_id) REFERENCES DRIVER(Driver_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (Vehicle_id) REFERENCES VEHICLE(Vehicle_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (Violation_type_id) REFERENCES TRAFFIC_VIOLATION_TYPE(Violation_type_id),
    FOREIGN KEY (Officer_id) REFERENCES OFFICER(Officer_id),
    FOREIGN KEY (Location_id) REFERENCES LOCATION(Location_id),
    INDEX idx_violation_driver (Driver_id),
    INDEX idx_violation_vehicle (Vehicle_id),
    INDEX idx_violation_date (Violation_date),
    INDEX idx_violation_status (Violation_status)
);


-- =================================================================

-- =====================================================
-- Operations for DRIVER

-- For adding row to DRIVER (INSERT)
DELIMITER //
CREATE PROCEDURE AddDriver(
    IN p_first_name VARCHAR(50),
    IN p_middle_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_suffix VARCHAR(10),
    IN p_dob DATE,
    IN p_weight DECIMAL(5,2),
    IN p_height DECIMAL(5,2),
    IN p_sex ENUM('Male','Female','Other'),
    IN p_nationality VARCHAR(50),
    IN p_civil_status ENUM('Single','Married','Divorced','Widowed'),
    IN p_contact VARCHAR(11),
    IN p_blood_type VARCHAR(3),
    IN p_house VARCHAR(4),
    IN p_street VARCHAR(100),
    IN p_barangay VARCHAR(100),
    IN p_city VARCHAR(100),
    IN p_province VARCHAR(100),
    IN p_region VARCHAR(100),
    IN p_zip VARCHAR(4)
)
BEGIN
    INSERT INTO DRIVER (
        First_name, Middle_name, Last_name, Suffix, 
        Date_of_birth,
        Weight, Height, 
        Sex_assigned_at_birth, 
        Nationality, Civil_status,
        Contact_number, 
        Blood_type, 
        House_number, Street_village, Barangay,City_municipality, Province, Region, Zip_code
    ) VALUES (
        p_first_name, p_middle_name, p_last_name, p_suffix, 
        p_dob,
        p_weight, p_height, 
        p_sex, 
        p_nationality, p_civil_status,
        p_contact, p_blood_type, 
        p_house, p_street, p_barangay, p_city, p_province, p_region, p_zip
    );
    SELECT LAST_INSERT_ID() AS NewDriverID;
END //
DELIMITER ;



-- ======================================================================
-- UI hierarchy views and stored procedures (exact names requested)
-- These definitions do not change the schema or any INSERT statements.

-- =====================================================
-- DRIVER / LICENSE / VEHICLE DETAIL VIEWS

CREATE OR REPLACE VIEW ViewDriverVehicle AS
SELECT
    d.Driver_id,
    d.First_name,
    d.Middle_name,
    d.Last_name,
    d.Suffix,
    d.Contact_number,
    v.Vehicle_id,
    v.Engine_number,
    v.Plate_number,
    v.Chassis_number,
    v.Vehicle_type,
    v.Make,
    v.Model,
    v.Year,
    v.Body_type,
    v.Capacity,
    v.Color
FROM DRIVER d
JOIN VEHICLE v ON v.Driver_id = d.Driver_id;

CREATE OR REPLACE VIEW ViewDriverLicense AS
SELECT
    d.Driver_id,
    d.First_name,
    d.Middle_name,
    d.Last_name,
    d.Suffix,
    d.Date_of_birth,
    TIMESTAMPDIFF(YEAR, d.Date_of_birth, CURDATE()) AS Age,
    d.Sex_assigned_at_birth,
    d.Nationality,
    d.Civil_status,
    d.Contact_number,
    d.Blood_type,
    d.House_number,
    d.Street_village,
    d.Barangay,
    d.City_municipality,
    d.Province,
    d.Region,
    d.Zip_code,
    l.License_number,
    l.License_type,
    l.License_status,
    l.License_issue_date,
    l.License_expiry_date,
    COALESCE(
        (SELECT GROUP_CONCAT(DISTINCT dl.Dl_codes ORDER BY dl.Dl_codes SEPARATOR ', ')
         FROM LICENSE_DLCODES dl
         WHERE dl.License_number = l.License_number),
        'N/A'
    ) AS Dl_codes,
    COALESCE(
        (SELECT GROUP_CONCAT(DISTINCT lc.`Condition` ORDER BY lc.`Condition` SEPARATOR ', ')
         FROM LICENSE_CONDITION lc
         WHERE lc.License_number = l.License_number),
        'N/A'
    ) AS Conditions
FROM DRIVER d
LEFT JOIN LICENSE l ON l.Driver_id = d.Driver_id;

CREATE OR REPLACE VIEW ViewDriverTrafficViolationVehicle AS
SELECT
    tv.Violation_id,
    tv.Violation_date,
    tv.Violation_status,
    tv.Fine_amount,
    tv.Payment_date,
    d.Driver_id,
    CONCAT(d.First_name, ' ', COALESCE(d.Middle_name, ''), ' ', d.Last_name) AS Driver_Name,
    v.Vehicle_id,
    v.Plate_number,
    v.Make,
    v.Model,
    v.Vehicle_type,
    tvt.Violation_type_id,
    tvt.Name AS Violation_Type,
    tvt.Base_fine,
    o.Officer_id,
    CONCAT(o.First_name, ' ', COALESCE(o.Middle_name, ''), ' ', o.Last_name) AS Officer_Name,
    o.Badge_number,
    o.Station,
    l.Location_id,
    l.City,
    l.Region
FROM TRAFFIC_VIOLATION tv
JOIN DRIVER d ON d.Driver_id = tv.Driver_id
JOIN VEHICLE v ON v.Vehicle_id = tv.Vehicle_id
JOIN TRAFFIC_VIOLATION_TYPE tvt ON tvt.Violation_type_id = tv.Violation_type_id
JOIN OFFICER o ON o.Officer_id = tv.Officer_id
JOIN LOCATION l ON l.Location_id = tv.Location_id;

CREATE OR REPLACE VIEW ViewVehicleRegistration AS
SELECT
    vr.Registration_number,
    vr.Registration_date,
    vr.Expiration_date,
    vr.Registration_status,
    vr.Official_receipt_number,
    vr.Official_receipt_date,
    vr.Document_ref_no,
    vr.Ownership_type,
    vr.Transfer_reason,
    vr.Ownership_start_date,
    vr.Ownership_end_date,
    v.Vehicle_id,
    v.Plate_number,
    v.Vehicle_type,
    v.Make,
    v.Model,
    v.Year,
    v.Color,
    d.Driver_id,
    CONCAT(d.First_name, ' ', COALESCE(d.Middle_name, ''), ' ', d.Last_name) AS Driver_Name
FROM VEHICLE_REGISTRATION vr
JOIN VEHICLE v ON v.Vehicle_id = vr.Vehicle_id
JOIN DRIVER d ON d.Driver_id = v.Driver_id;

CREATE OR REPLACE VIEW ViewVehicleViolations AS
SELECT
    tv.Violation_id,
    tv.Violation_date,
    tv.Violation_status,
    tv.Fine_amount,
    tv.Payment_date,
    tv.Driver_id,
    CONCAT(d.First_name, ' ', COALESCE(d.Middle_name, ''), ' ', d.Last_name) AS Driver_Name,
    tv.Vehicle_id,
    v.Plate_number,
    v.Vehicle_type,
    v.Make,
    v.Model,
    tvt.Violation_type_id,
    tvt.Name AS Violation_Type,
    o.Officer_id,
    CONCAT(o.First_name, ' ', COALESCE(o.Middle_name, ''), ' ', o.Last_name) AS Officer_Name,
    l.Location_id,
    l.City,
    l.Region
FROM TRAFFIC_VIOLATION tv
JOIN DRIVER d ON d.Driver_id = tv.Driver_id
JOIN VEHICLE v ON v.Vehicle_id = tv.Vehicle_id
JOIN TRAFFIC_VIOLATION_TYPE tvt ON tvt.Violation_type_id = tv.Violation_type_id
JOIN OFFICER o ON o.Officer_id = tv.Officer_id
JOIN LOCATION l ON l.Location_id = tv.Location_id;

CREATE OR REPLACE VIEW ViewExpiredVehicleRegistration AS
SELECT *
FROM ViewVehicleRegistration
WHERE Registration_status = 'expired';

CREATE OR REPLACE VIEW ViewExpiredSuspendedDriverLicenses AS
SELECT *
FROM ViewDriverLicense
WHERE License_status IN ('expired', 'suspended');

CREATE OR REPLACE VIEW ViewTotalViolationsForGivenYear AS
SELECT
    YEAR(tv.Violation_date) AS Violation_Year,
    d.Driver_id,
    CONCAT(d.First_name, ' ', COALESCE(d.Middle_name, ''), ' ', d.Last_name) AS Driver_Name,
    tvt.Violation_type_id,
    tvt.Name AS Violation_Type,
    COUNT(tv.Violation_id) AS Total_Count,
    SUM(tv.Fine_amount) AS Total_Fines_Collected
FROM TRAFFIC_VIOLATION tv
JOIN DRIVER d ON d.Driver_id = tv.Driver_id
JOIN TRAFFIC_VIOLATION_TYPE tvt ON tvt.Violation_type_id = tv.Violation_type_id
GROUP BY
    YEAR(tv.Violation_date),
    d.Driver_id,
    d.First_name,
    d.Middle_name,
    d.Last_name,
    tvt.Violation_type_id,
    tvt.Name;

-- Views for filters used by the registered drivers report
CREATE OR REPLACE VIEW ViewDriverLicenseStudentPermit AS
SELECT * FROM ViewDriverLicense WHERE License_type = 'Student Permit';

CREATE OR REPLACE VIEW ViewDriverLicenseProfessional AS
SELECT * FROM ViewDriverLicense WHERE License_type = 'Professional';

CREATE OR REPLACE VIEW ViewDriverLicenseNonProfessional AS
SELECT * FROM ViewDriverLicense WHERE License_type = 'Non-Professional';

CREATE OR REPLACE VIEW ViewDriverLicenseValid AS
SELECT * FROM ViewDriverLicense WHERE License_status = 'valid';

CREATE OR REPLACE VIEW ViewDriverLicenseExpired AS
SELECT * FROM ViewDriverLicense WHERE License_status = 'expired';

CREATE OR REPLACE VIEW ViewDriverLicenseSuspended AS
SELECT * FROM ViewDriverLicense WHERE License_status = 'suspended';

CREATE OR REPLACE VIEW ViewDriverLicenseRevoked AS
SELECT * FROM ViewDriverLicense WHERE License_status = 'revoked';

CREATE OR REPLACE VIEW ShowMaleDrivers AS
SELECT * FROM ViewDriverLicense WHERE Sex_assigned_at_birth = 'Male';

CREATE OR REPLACE VIEW ShowFemaleDrivers AS
SELECT * FROM ViewDriverLicense WHERE Sex_assigned_at_birth = 'Female';

-- =====================================================
-- STORED PROCEDURES (exact names requested)

DROP PROCEDURE IF EXISTS ShowDriverVehicles;
DELIMITER //
CREATE PROCEDURE ShowDriverVehicles(IN p_driver_id INT)
BEGIN
    SELECT *
    FROM ViewDriverVehicle
    WHERE Driver_id = p_driver_id
    ORDER BY Vehicle_id ASC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowDriverLicense;
DELIMITER //
CREATE PROCEDURE ShowDriverLicense(IN p_driver_id INT)
BEGIN
    SELECT *
    FROM ViewDriverLicense
    WHERE Driver_id = p_driver_id
    ORDER BY License_number ASC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowTrafficViolations;
DELIMITER //
CREATE PROCEDURE ShowTrafficViolations(IN p_driver_id INT)
BEGIN
    SELECT *
    FROM ViewDriverTrafficViolationVehicle
    WHERE Driver_id = p_driver_id
    ORDER BY Violation_id ASC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowVehicleOwner;
DELIMITER //
CREATE PROCEDURE ShowVehicleOwner(IN p_vehicle_id INT)
BEGIN
    SELECT *
    FROM ViewDriverVehicle
    WHERE Vehicle_id = p_vehicle_id
    ORDER BY Driver_id ASC
    LIMIT 1;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowVehicleRegistrations;
DELIMITER //
CREATE PROCEDURE ShowVehicleRegistrations(IN p_vehicle_id INT)
BEGIN
    SELECT *
    FROM ViewVehicleRegistration
    WHERE Vehicle_id = p_vehicle_id
    ORDER BY Registration_date DESC, Registration_number DESC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowVehicleTrafficViolations;
DELIMITER //
CREATE PROCEDURE ShowVehicleTrafficViolations(IN p_vehicle_id INT)
BEGIN
    SELECT *
    FROM ViewVehicleViolations
    WHERE Vehicle_id = p_vehicle_id
    ORDER BY Violation_id ASC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowDriverAgeRange;
DELIMITER //
CREATE PROCEDURE ShowDriverAgeRange(IN p_min_age INT, IN p_max_age INT)
BEGIN
    SELECT *
    FROM ViewDriverLicense
    WHERE Age BETWEEN p_min_age AND p_max_age
    ORDER BY Age ASC, Driver_id ASC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowVehicleViolationCity;
DELIMITER //
CREATE PROCEDURE ShowVehicleViolationCity(IN p_city VARCHAR(100))
BEGIN
    SELECT *
    FROM ViewVehicleViolations
    WHERE City = p_city
    ORDER BY Vehicle_id ASC, Violation_id ASC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowVehicleViolationRegion;
DELIMITER //
CREATE PROCEDURE ShowVehicleViolationRegion(IN p_region VARCHAR(100))
BEGIN
    SELECT *
    FROM ViewVehicleViolations
    WHERE Region = p_region
    ORDER BY Vehicle_id ASC, Violation_id ASC;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS ShowDriverTrafficViolationsWithinDates;
DELIMITER //
CREATE PROCEDURE ShowDriverTrafficViolationsWithinDates(
    IN p_driver_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT *
    FROM ViewDriverTrafficViolationVehicle
    WHERE Driver_id = p_driver_id
      AND DATE(Violation_date) BETWEEN p_start_date AND p_end_date
    ORDER BY Violation_date ASC, Violation_id ASC;
END //
DELIMITER ;


-- =====================================================
-- Additional procedures for UI detailed views and renewal
-- =====================================================

-- =================================================================
-- Alias/wrapper procedures to match requested exact names
-- These call or mirror existing procedures/queries so behaviour is unchanged.
-- =================================================================

-- FindDriver: return driver row by id
DROP PROCEDURE IF EXISTS FindDriver;
DELIMITER //
CREATE PROCEDURE FindDriver(IN p_driver_id INT)
BEGIN
    SELECT * FROM DRIVER WHERE Driver_id = p_driver_id;
END //
DELIMITER ;

-- FindVehicle: return vehicle row by id
DROP PROCEDURE IF EXISTS FindVehicle;
DELIMITER //
CREATE PROCEDURE FindVehicle(IN p_vehicle_id INT)
BEGIN
    SELECT * FROM VEHICLE WHERE Vehicle_id = p_vehicle_id;
END //
DELIMITER ;

-- FindVehicleRegistration: return registration row by registration number
DROP PROCEDURE IF EXISTS FindVehicleRegistration;
DELIMITER //
CREATE PROCEDURE FindVehicleRegistration(IN p_registration_number VARCHAR(10))
BEGIN
    SELECT * FROM VEHICLE_REGISTRATION WHERE Registration_number = p_registration_number;
END //
DELIMITER ;

-- FindTrafficViolation: return violation row by id
DROP PROCEDURE IF EXISTS FindTrafficViolation;
DELIMITER //
CREATE PROCEDURE FindTrafficViolation(IN p_violation_id INT)
BEGIN
    SELECT * FROM TRAFFIC_VIOLATION WHERE Violation_id = p_violation_id;
END //
DELIMITER ;

-- -- AddVehicleRegistration: wrapper that calls AddRegistration
-- DROP PROCEDURE IF EXISTS AddVehicleRegistration;
-- DELIMITER //
-- CREATE PROCEDURE AddVehicleRegistration(
--     IN p_reg_number VARCHAR(10),
--     IN p_reg_date DATE,
--     IN p_exp_date DATE,
--     IN p_status ENUM('active','expired','suspended'),
--     IN p_or_number VARCHAR(10),
--     IN p_or_date DATE,
--     IN p_doc_ref VARCHAR(50),
--     IN p_ownership ENUM('owned','financed','leased'),
--     IN p_transfer_reason VARCHAR(255),
--     IN p_start_date DATE,
--     IN p_end_date DATE,
--     IN p_vehicle_id INT
-- )
-- BEGIN
--     CALL AddRegistration(p_reg_number, p_reg_date, p_exp_date, p_status, p_or_number, p_or_date, p_doc_ref, p_ownership, p_transfer_reason, p_start_date, p_end_date, p_vehicle_id);
-- END //
-- DELIMITER ;

-- RenewVehicleRegistration: wrapper for RenewRegistration (same signature)
DROP PROCEDURE IF EXISTS RenewVehicleRegistration;
DELIMITER //
CREATE PROCEDURE RenewVehicleRegistration(
    IN p_old_registration_number VARCHAR(10),
    IN p_new_registration_number VARCHAR(10),
    IN p_registration_date DATE,
    IN p_expiration_date DATE
)
BEGIN
    -- Wrapper: do not ask for OR info; RenewRegistration will reuse previous OR data
    CALL RenewRegistration(p_old_registration_number, p_new_registration_number, p_registration_date, p_expiration_date);
END //
DELIMITER ;

-- UpdateVehicleRegistration: full updater that mirrors requested signature
DROP PROCEDURE IF EXISTS UpdateVehicleRegistration;
DELIMITER //
CREATE PROCEDURE UpdateVehicleRegistration(
    IN p_reg_number VARCHAR(10),
    IN p_registration_date DATE,
    IN p_expiration_date DATE,
    IN p_registration_status ENUM('active','expired','suspended'),
    IN p_official_receipt_number VARCHAR(10),
    IN p_official_receipt_date DATE,
    IN p_document_ref_no VARCHAR(50),
    IN p_ownership_type ENUM('owned','financed','leased'),
    IN p_transfer_reason VARCHAR(255),
    IN p_ownership_start_date DATE,
    IN p_ownership_end_date DATE,
    IN p_vehicle_id INT
)
BEGIN
    UPDATE VEHICLE_REGISTRATION SET
        Registration_date = COALESCE(p_registration_date, Registration_date),
        Expiration_date = COALESCE(p_expiration_date, Expiration_date),
        Registration_status = COALESCE(p_registration_status, Registration_status),
        Official_receipt_number = COALESCE(p_official_receipt_number, Official_receipt_number),
        Official_receipt_date = COALESCE(p_official_receipt_date, Official_receipt_date),
        Document_ref_no = COALESCE(p_document_ref_no, Document_ref_no),
        Ownership_type = COALESCE(p_ownership_type, Ownership_type),
        Transfer_reason = COALESCE(p_transfer_reason, Transfer_reason),
        Ownership_start_date = COALESCE(p_ownership_start_date, Ownership_start_date),
        Ownership_end_date = COALESCE(p_ownership_end_date, Ownership_end_date),
        Vehicle_id = COALESCE(p_vehicle_id, Vehicle_id)
    WHERE Registration_number = p_reg_number;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- -- DeleteVehicleRegistration: wrapper to existing DeleteRegistration
-- DROP PROCEDURE IF EXISTS DeleteVehicleRegistration;
-- DELIMITER //
-- CREATE PROCEDURE DeleteVehicleRegistration(IN p_registration_number VARCHAR(10))
-- BEGIN
--     CALL DeleteRegistration(p_registration_number);
-- END //
-- DELIMITER ;

-- AddTrafficViolation: wrapper for AddViolation
DROP PROCEDURE IF EXISTS AddTrafficViolation;
DELIMITER //
CREATE PROCEDURE AddTrafficViolation(
    IN p_violation_date DATETIME,
    IN p_status ENUM('unpaid','paid','contested'),
    IN p_fine DECIMAL(10,2),
    IN p_payment_date DATE,
    IN p_driver_id INT,
    IN p_vehicle_id INT,
    IN p_violation_type_id INT,
    IN p_officer_id INT,
    IN p_location_id INT
)
BEGIN
    CALL AddViolation(p_violation_date, p_status, p_fine, p_payment_date, p_driver_id, p_vehicle_id, p_violation_type_id, p_officer_id, p_location_id);
END //
DELIMITER ;

-- UpdateTrafficViolation: full updater matching requested signature
DROP PROCEDURE IF EXISTS UpdateTrafficViolation;
DELIMITER //
CREATE PROCEDURE UpdateTrafficViolation(
    IN p_violation_id INT,
    IN p_violation_date DATETIME,
    IN p_violation_status ENUM('unpaid','paid','contested'),
    IN p_fine_amount DECIMAL(10,2),
    IN p_payment_date DATE,
    IN p_driver_id INT,
    IN p_vehicle_id INT,
    IN p_violation_type_id INT,
    IN p_officer_id INT,
    IN p_location_id INT
)
BEGIN
    UPDATE TRAFFIC_VIOLATION SET
        Violation_date = COALESCE(p_violation_date, Violation_date),
        Violation_status = COALESCE(p_violation_status, Violation_status),
        Fine_amount = COALESCE(p_fine_amount, Fine_amount),
        Payment_date = COALESCE(p_payment_date, Payment_date),
        Driver_id = COALESCE(p_driver_id, Driver_id),
        Vehicle_id = COALESCE(p_vehicle_id, Vehicle_id),
        Violation_type_id = COALESCE(p_violation_type_id, Violation_type_id),
        Officer_id = COALESCE(p_officer_id, Officer_id),
        Location_id = COALESCE(p_location_id, Location_id)
    WHERE Violation_id = p_violation_id;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- DeleteTrafficViolation: wrapper to existing DeleteViolation
DROP PROCEDURE IF EXISTS DeleteTrafficViolation;
DELIMITER //
CREATE PROCEDURE DeleteTrafficViolation(IN p_violation_id INT)
BEGIN
    CALL DeleteViolation(p_violation_id);
END //
DELIMITER ;

-- AddVehicle alias view for compatibility (non-destructive)
DROP VIEW IF EXISTS DriverVehicle;
CREATE OR REPLACE VIEW DriverVehicle AS
SELECT * FROM ViewDriverVehicle;

-- ViewTotalViolationsForGivenYear: procedure wrapper that returns counts for a year
DROP PROCEDURE IF EXISTS ViewTotalViolationsForGivenYear;
DELIMITER //
CREATE PROCEDURE ViewTotalViolationsForGivenYear(IN p_year INT)
BEGIN
    CALL GetViolationCountsByTypePerYear(p_year);
END //
DELIMITER ;


-- Renew a vehicle registration by inserting a new registration row
DELIMITER //
CREATE PROCEDURE RenewRegistration(
    IN p_old_registration_number VARCHAR(10),
    IN p_new_registration_number VARCHAR(10),
    IN p_registration_date DATE,
    IN p_expiration_date DATE
)
BEGIN
    DECLARE v_vehicle_id INT;
    DECLARE v_ownership_type VARCHAR(20);
    DECLARE v_document_ref_no VARCHAR(50);
    DECLARE v_transfer_reason VARCHAR(255);
    DECLARE v_ownership_start_date DATE;
    DECLARE v_ownership_end_date DATE;
    DECLARE v_official_receipt_number VARCHAR(10);
    DECLARE v_official_receipt_date DATE;
    SELECT Vehicle_id, Ownership_type, Document_ref_no, Transfer_reason, Ownership_start_date, Ownership_end_date, Official_receipt_number, Official_receipt_date
    INTO v_vehicle_id, v_ownership_type, v_document_ref_no, v_transfer_reason, v_ownership_start_date, v_ownership_end_date, v_official_receipt_number, v_official_receipt_date
    FROM VEHICLE_REGISTRATION
    WHERE Registration_number = p_old_registration_number
    LIMIT 1;

    -- If the old registration was not found, raise a clear error
    IF v_vehicle_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Old registration not found for renewal';
    END IF;

    -- Ensure we have non-NULL OR fields to satisfy NOT NULL constraints in VEHICLE_REGISTRATION
    SET v_official_receipt_number = COALESCE(v_official_receipt_number, 'UNKNOWN');
    SET v_official_receipt_date = COALESCE(v_official_receipt_date, p_registration_date);

    INSERT INTO VEHICLE_REGISTRATION(
        Registration_number, Registration_date, Expiration_date, Registration_status,
        Official_receipt_number, Official_receipt_date, Document_ref_no, Ownership_type, Transfer_reason, Ownership_start_date, Ownership_end_date, Vehicle_id
    ) VALUES (
        p_new_registration_number, p_registration_date, p_expiration_date, 'active',
        v_official_receipt_number,
        v_official_receipt_date,
        v_document_ref_no, v_ownership_type, v_transfer_reason, p_registration_date, v_ownership_end_date, v_vehicle_id
    );

    SELECT p_new_registration_number AS NewRegistrationNumber;
END //
DELIMITER ;

-- Return all vehicles owned by a driver (simple list)
DELIMITER //
CREATE PROCEDURE GetDriverVehicles(IN p_driver_id INT)
BEGIN
    SELECT v.Vehicle_id, v.Engine_number, v.Plate_number, v.Chassis_number, v.Vehicle_type, v.Make, v.Model, v.Year, v.Body_type, v.Capacity, v.Color
    FROM VEHICLE v
    WHERE v.Driver_id = p_driver_id
    ORDER BY v.Vehicle_id;
END //
DELIMITER ;

-- Return licenses for a driver with aggregated DL codes and conditions
DELIMITER //
CREATE PROCEDURE GetDriverLicenses(IN p_driver_id INT)
BEGIN
    SELECT l.License_number, l.License_type, l.License_status, l.License_issue_date, l.License_expiry_date,
           COALESCE((SELECT GROUP_CONCAT(DISTINCT Dl_codes SEPARATOR ',') FROM LICENSE_DLCODES d WHERE d.License_number = l.License_number), '') AS Dl_codes,
           COALESCE((SELECT GROUP_CONCAT(DISTINCT `Condition` SEPARATOR ',') FROM LICENSE_CONDITION c WHERE c.License_number = l.License_number), '') AS Conditions
    FROM LICENSE l
    WHERE l.Driver_id = p_driver_id
    ORDER BY l.License_issue_date DESC;
END //
DELIMITER ;

-- Return violations for a driver with vehicle plate and location
DELIMITER //
CREATE PROCEDURE GetDriverViolations(IN p_driver_id INT)
BEGIN
    SELECT tv.Violation_id, tv.Violation_date, tv.Violation_status, tv.Fine_amount, tv.Payment_date,
           tvt.Name AS Violation_Type, v.Plate_number, l.City, l.Region
    FROM TRAFFIC_VIOLATION tv
    JOIN TRAFFIC_VIOLATION_TYPE tvt ON tv.Violation_type_id = tvt.Violation_type_id
    LEFT JOIN VEHICLE v ON tv.Vehicle_id = v.Vehicle_id
    LEFT JOIN LOCATION l ON tv.Location_id = l.Location_id
    WHERE tv.Driver_id = p_driver_id
    ORDER BY tv.Violation_date DESC;
END //
DELIMITER ;

-- Return owner info for a vehicle
DELIMITER //
CREATE PROCEDURE GetVehicleOwner(IN p_vehicle_id INT)
BEGIN
    SELECT d.Driver_id, d.First_name, d.Middle_name, d.Last_name, d.Suffix, d.Date_of_birth, d.Contact_number
    FROM DRIVER d
    JOIN VEHICLE v ON v.Driver_id = d.Driver_id
    WHERE v.Vehicle_id = p_vehicle_id
    LIMIT 1;
END //
DELIMITER ;

-- Return registrations for a vehicle (history)
DELIMITER //
CREATE PROCEDURE GetVehicleRegistrations(IN p_vehicle_id INT)
BEGIN
    SELECT vr.Registration_number, vr.Registration_date, vr.Expiration_date, vr.Registration_status, vr.Official_receipt_number, vr.Official_receipt_date, vr.Ownership_type, vr.Transfer_reason
    FROM VEHICLE_REGISTRATION vr
    WHERE vr.Vehicle_id = p_vehicle_id
    ORDER BY vr.Registration_date DESC;
END //
DELIMITER ;

-- Return violations for a vehicle
DELIMITER //
CREATE PROCEDURE GetVehicleViolations(IN p_vehicle_id INT)
BEGIN
    SELECT tv.Violation_id, tv.Violation_date, tv.Violation_status, tv.Fine_amount, tv.Payment_date,
           tvt.Name AS Violation_Type, l.City, l.Region
    FROM TRAFFIC_VIOLATION tv
    JOIN TRAFFIC_VIOLATION_TYPE tvt ON tv.Violation_type_id = tvt.Violation_type_id
    LEFT JOIN LOCATION l ON tv.Location_id = l.Location_id
    WHERE tv.Vehicle_id = p_vehicle_id
    ORDER BY tv.Violation_date DESC;
END //
DELIMITER ;

-- For updating row in DRIVER by Driver_id (UPDATE)
DELIMITER //
CREATE PROCEDURE UpdateDriver(
    IN p_driver_id INT,
    IN p_first_name VARCHAR(50),
    IN p_middle_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_suffix VARCHAR(10),
    IN p_dob DATE,
    IN p_weight DECIMAL(5,2),
    IN p_height DECIMAL(5,2),
    IN p_sex ENUM('Male','Female','Other'),
    IN p_nationality VARCHAR(50),
    IN p_civil_status ENUM('Single','Married','Divorced','Widowed'),
    IN p_contact VARCHAR(11),
    IN p_blood_type VARCHAR(3),
    IN p_house VARCHAR(4),
    IN p_street VARCHAR(100),
    IN p_barangay VARCHAR(100),
    IN p_city VARCHAR(100),
    IN p_province VARCHAR(100),
    IN p_region VARCHAR(100),
    IN p_zip VARCHAR(4)
)
BEGIN
    UPDATE DRIVER SET
        First_name = p_first_name,
        Middle_name = p_middle_name,
        Last_name = p_last_name,
        Suffix = p_suffix,
        Date_of_birth = p_dob,
        Weight = p_weight,
        Height = p_height,
        Sex_assigned_at_birth = p_sex,
        Nationality = p_nationality,
        Civil_status = p_civil_status,
        Contact_number = p_contact,
        Blood_type = p_blood_type,
        House_number = p_house,
        Street_village = p_street,
        Barangay = p_barangay,
        City_municipality = p_city,
        Province = p_province,
        Region = p_region,
        Zip_code = p_zip
    WHERE Driver_id = p_driver_id;
    SET @rows_affected = ROW_COUNT();
    SELECT @rows_affected AS RowsAffected;
END //
DELIMITER ;

-- For deleting row in DRIVER (only when the driver_id is not referenced by a vehicle)
DELIMITER //
CREATE PROCEDURE DeleteDriver(IN p_driver_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Cannot delete driver with existing vehicles or licenses. Remove related records (references) first.' AS Error;
    END;
    START TRANSACTION;
    DELETE FROM DRIVER WHERE Driver_id = p_driver_id;
    SET @rows_affected = ROW_COUNT();
    COMMIT;
    SELECT @rows_affected AS RowsAffected;
END //
DELIMITER ;

-- For searching DRIVER records (by first name, last name, license number, or contact number)
DELIMITER //
CREATE PROCEDURE SearchDriver(
    IN p_first_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_license_number VARCHAR(13),
    IN p_contact VARCHAR(11)
)
BEGIN
    SELECT d.*, 
           l.License_number, l.License_type, l.License_status
    FROM DRIVER d
    LEFT JOIN LICENSE l ON d.Driver_id = l.Driver_id
    WHERE (p_first_name IS NULL OR d.First_name LIKE CONCAT('%', p_first_name, '%'))
      AND (p_last_name IS NULL OR d.Last_name LIKE CONCAT('%', p_last_name, '%'))
      AND (p_license_number IS NULL OR l.License_number = p_license_number)
      AND (p_contact IS NULL OR d.Contact_number = p_contact);
END //
DELIMITER ;

-- View for listing drivers (includes current license info if any)

-- View for listing drivers (includes current license info if any) and computed Age
CREATE OR REPLACE VIEW vw_driver AS
SELECT
	d.Driver_id,
	d.First_name,
	d.Middle_name,
	d.Last_name,
	d.Suffix,
	d.Date_of_birth,
	d.Weight,
	d.Height,
	d.Sex_assigned_at_birth,
	d.Nationality,
	d.Civil_status,
	d.Contact_number,
	d.Blood_type,
	d.House_number,
	d.Street_village,
	d.Barangay,
	d.City_municipality,
	d.Province,
	d.Region,
	d.Zip_code,
	l.License_number,
	l.License_type,
	l.License_status,
	TIMESTAMPDIFF(YEAR, d.Date_of_birth, CURDATE()) AS Age
FROM DRIVER d
LEFT JOIN LICENSE l ON d.Driver_id = l.Driver_id;

-- Views for license types
CREATE OR REPLACE VIEW vw_driver_license_student AS
SELECT * FROM vw_driver WHERE License_type = 'Student Permit';

CREATE OR REPLACE VIEW vw_driver_license_nonprofessional AS
SELECT * FROM vw_driver WHERE License_type = 'Non-Professional';

CREATE OR REPLACE VIEW vw_driver_license_professional AS
SELECT * FROM vw_driver WHERE License_type = 'Professional';

-- Views for license status
CREATE OR REPLACE VIEW vw_driver_status_valid AS
SELECT * FROM vw_driver WHERE License_status = 'valid';

CREATE OR REPLACE VIEW vw_driver_status_expired AS
SELECT * FROM vw_driver WHERE License_status = 'expired';

CREATE OR REPLACE VIEW vw_driver_status_suspended AS
SELECT * FROM vw_driver WHERE License_status = 'suspended';

CREATE OR REPLACE VIEW vw_driver_status_revoked AS
SELECT * FROM vw_driver WHERE License_status = 'revoked';

-- Views for sex assigned at birth
CREATE OR REPLACE VIEW vw_driver_sex_male AS
SELECT * FROM vw_driver WHERE Sex_assigned_at_birth = 'Male';

CREATE OR REPLACE VIEW vw_driver_sex_female AS
SELECT * FROM vw_driver WHERE Sex_assigned_at_birth = 'Female';

CREATE OR REPLACE VIEW vw_driver_sex_other AS
SELECT * FROM vw_driver WHERE Sex_assigned_at_birth = 'Other';

-- =====================================================
-- Operations for VEHICLE 

-- For adding row in VEHICLE (INSERT)
DELIMITER //
CREATE PROCEDURE AddVehicle(
    IN p_engine VARCHAR(12),
    IN p_plate VARCHAR(7),
    IN p_chassis VARCHAR(17),
    IN p_type ENUM('motorcycle','private car','public utility vehicle','truck','others'),
    IN p_make VARCHAR(50),
    IN p_model VARCHAR(50),
    IN p_year INT,
    IN p_body_type VARCHAR(50),
    IN p_capacity INT,
    IN p_color VARCHAR(30),
    IN p_owner_id INT
)
BEGIN
    INSERT INTO VEHICLE (
        Engine_number, 
        Plate_number, 
        Chassis_number, 
        Vehicle_type,
        Make, 
        Model, 
        Year, 
        Body_type, 
        Capacity, 
        Color, 
        Driver_id
    ) VALUES (
        p_engine, 
        p_plate, 
        p_chassis, 
        p_type,
        p_make, 
        p_model, 
        p_year, 
        p_body_type, 
        p_capacity, 
        p_color, 
        p_owner_id
    );
    SELECT LAST_INSERT_ID() AS NewVehicleID;
END //
DELIMITER ;

-- For updating row in VEHICLE (UPDATE)
DELIMITER //
CREATE PROCEDURE UpdateVehicle(
    IN p_vehicle_id INT,
    IN p_engine VARCHAR(12),
    IN p_plate VARCHAR(7),
    IN p_chassis VARCHAR(17),
    IN p_type ENUM('motorcycle','private car','public utility vehicle','truck','others'),
    IN p_make VARCHAR(50),
    IN p_model VARCHAR(50),
    IN p_year INT,
    IN p_body_type VARCHAR(50),
    IN p_capacity INT,
    IN p_color VARCHAR(30),
    IN p_owner_id INT
)
BEGIN
    UPDATE VEHICLE SET
        Engine_number = p_engine,
        Plate_number = p_plate,
        Chassis_number = p_chassis,
        Vehicle_type = p_type,
        Make = p_make,
        Model = p_model,
        Year = p_year,
        Body_type = p_body_type,
        Capacity = p_capacity,
        Color = p_color,
        Driver_id = p_owner_id
    WHERE Vehicle_id = p_vehicle_id;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For deleting row in VEHICLE (DELETE) {cascades to registrations but not violations if any}
DELIMITER //
CREATE PROCEDURE DeleteVehicle(IN p_vehicle_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Cannot delete vehicle with existing violations. Remove violations first.' AS Error;
    END;
    START TRANSACTION;
    DELETE FROM VEHICLE WHERE Vehicle_id = p_vehicle_id;
    COMMIT;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For searching row/s in VEHICLE (by plate, owner's last name, or type)
DELIMITER //
CREATE PROCEDURE SearchVehicle(
    IN p_plate VARCHAR(7),
    IN p_owner_lastname VARCHAR(50),
    IN p_vehicle_type VARCHAR(20)
)
BEGIN
    SELECT v.*, 
           CONCAT(d.First_name, ' ', d.Last_name) AS OwnerName
    FROM VEHICLE v
    JOIN DRIVER d ON v.Driver_id = d.Driver_id
    WHERE (p_plate IS NULL OR v.Plate_number LIKE CONCAT('%', p_plate, '%'))
      AND (p_owner_lastname IS NULL OR d.Last_name LIKE CONCAT('%', p_owner_lastname, '%'))
      AND (p_vehicle_type IS NULL OR v.Vehicle_type = p_vehicle_type);
END //
DELIMITER ;





-- =====================================================
-- Operations for VEHICLE_REGISTRATION

-- For adding row in VEHICLE_REGISTRATION (like a new registration or renewal)
DELIMITER //
CREATE PROCEDURE AddVehicleRegistration(
    IN p_reg_number VARCHAR(10),
    IN p_reg_date DATE,
    IN p_exp_date DATE,
    IN p_status ENUM('active','expired','suspended'),
    IN p_or_number VARCHAR(10),
    IN p_or_date DATE,
    IN p_doc_ref VARCHAR(50),
    IN p_ownership ENUM('owned','financed','leased'),
    IN p_transfer_reason VARCHAR(255),
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_vehicle_id INT
)
BEGIN
    INSERT INTO VEHICLE_REGISTRATION (
        Registration_number, 
        Registration_date, 
        Expiration_date, 
        Registration_status,
        Official_receipt_number, 
        Official_receipt_date, 
        Document_ref_no,
        Ownership_type, 
        Transfer_reason, 
        Ownership_start_date, 
        Ownership_end_date, 
        Vehicle_id
    ) VALUES (
        p_reg_number, 
        p_reg_date, 
        p_exp_date, 
        p_status,
        p_or_number, 
        p_or_date, 
        p_doc_ref,
        p_ownership, 
        p_transfer_reason, 
        p_start_date, 
        p_end_date, 
        p_vehicle_id
    );
    SELECT 'Registration added' AS Message;
END //
DELIMITER ;

-- For updating row in VEHICLE_REGISTRATION (like changing status or extending expiration)
DELIMITER //
CREATE PROCEDURE UpdateRegistration(
    IN p_reg_number VARCHAR(10),
    IN p_new_status ENUM('active','expired','suspended'),
    IN p_new_exp_date DATE
)
BEGIN
    UPDATE VEHICLE_REGISTRATION SET
        Registration_status = COALESCE(p_new_status, Registration_status),
        Expiration_date = COALESCE(p_new_exp_date, Expiration_date)
    WHERE Registration_number = p_reg_number;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For deleting row in VEHICLE_REGISTRATION (ONLY if allowed – rarely used, not sure if they do this in real LTO system)
DELIMITER //
CREATE PROCEDURE DeleteVehicleRegistration(IN p_reg_number VARCHAR(10))
BEGIN
    DELETE FROM VEHICLE_REGISTRATION WHERE Registration_number = p_reg_number;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For searching row/s in VEHICLE_REGISTRATION (by vehicle plate, status, or expiration range)
DELIMITER //
CREATE PROCEDURE SearchRegistration(
    IN p_plate VARCHAR(7),
    IN p_status VARCHAR(10),
    IN p_expired_before DATE
)
BEGIN
    SELECT vr.*, v.Plate_number, v.Make, v.Model
    FROM VEHICLE_REGISTRATION vr
    JOIN VEHICLE v ON vr.Vehicle_id = v.Vehicle_id
    WHERE (p_plate IS NULL OR v.Plate_number LIKE CONCAT('%', p_plate, '%'))
      AND (p_status IS NULL OR vr.Registration_status = p_status)
      AND (p_expired_before IS NULL OR vr.Expiration_date < p_expired_before);
END //
DELIMITER ;





-- =====================================================
-- Operations for TRAFFIC_VIOLATION

-- for adding row in TRAFFIC_VIOLATION (INSERT)
DELIMITER //
CREATE PROCEDURE AddViolation(
    IN p_violation_date DATETIME,
    IN p_status ENUM('unpaid','paid','contested'),
    IN p_fine DECIMAL(10,2),
    IN p_payment_date DATE,
    IN p_driver_id INT,
    IN p_vehicle_id INT,
    IN p_violation_type_id INT,
    IN p_officer_id INT,
    IN p_location_id INT
)
BEGIN
    INSERT INTO TRAFFIC_VIOLATION (
        Violation_date, 
        Violation_status, 
        Fine_amount, 
        Payment_date,
        Driver_id, 
        Vehicle_id, 
        Violation_type_id, 
        Officer_id, 
        Location_id
    ) VALUES (
        p_violation_date, 
        p_status, 
        p_fine, 
        p_payment_date,
        p_driver_id, 
        p_vehicle_id, 
        p_violation_type_id, 
        p_officer_id, 
        p_location_id
    );
    SELECT LAST_INSERT_ID() AS NewViolationID;
END //
DELIMITER ;

-- For updating row in TRAFFIC_VIOLATION (like marking as paid or changing status)
DELIMITER //
CREATE PROCEDURE UpdateViolation(
    IN p_violation_id INT,
    IN p_new_status ENUM('unpaid','paid','contested'),
    IN p_payment_date DATE
)
BEGIN
    UPDATE TRAFFIC_VIOLATION SET
        Violation_status = COALESCE(p_new_status, Violation_status),
        Payment_date = COALESCE(p_payment_date, Payment_date)
    WHERE Violation_id = p_violation_id;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For deleting row in TRAFFIC_VIOLATION (not sure if they also do this in the real LTO system)
DELIMITER //
CREATE PROCEDURE DeleteViolation(IN p_violation_id INT)
BEGIN
    DELETE FROM TRAFFIC_VIOLATION WHERE Violation_id = p_violation_id;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For searching row/s in TRAFFIC_VIOLATION (by driver's last name, vehicle, date range, or status)
DELIMITER //
CREATE PROCEDURE SearchViolation(
    IN p_driver_lastname VARCHAR(50),
    IN p_plate VARCHAR(7),
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_status VARCHAR(10)
)
BEGIN
    SELECT tv.*, 
           CONCAT(d.First_name, ' ', d.Last_name) AS DriverName,
           v.Plate_number,
           tvt.Name AS ViolationType,
           l.City, l.Region
    FROM TRAFFIC_VIOLATION tv
    JOIN DRIVER d ON tv.Driver_id = d.Driver_id
    JOIN VEHICLE v ON tv.Vehicle_id = v.Vehicle_id
    JOIN TRAFFIC_VIOLATION_TYPE tvt ON tv.Violation_type_id = tvt.Violation_type_id
    JOIN LOCATION l ON tv.Location_id = l.Location_id
    WHERE (p_driver_lastname IS NULL OR d.Last_name LIKE CONCAT('%', p_driver_lastname, '%'))
      AND (p_plate IS NULL OR v.Plate_number LIKE CONCAT('%', p_plate, '%'))
      AND (p_start_date IS NULL OR DATE(tv.Violation_date) >= p_start_date)
      AND (p_end_date IS NULL OR DATE(tv.Violation_date) <= p_end_date)
      AND (p_status IS NULL OR tv.Violation_status = p_status);
END //
DELIMITER ;





-- =====================================================
-- Operations for LICENSE

-- For adding row in LICENSE
DELIMITER //
CREATE PROCEDURE AddLicense(
    IN p_license_number VARCHAR(13),
    IN p_license_type ENUM('Student Permit','Non-Professional','Professional'),
    IN p_license_status ENUM('valid','expired','suspended','revoked'),
    IN p_issue_date DATE,
    IN p_expiry_date DATE,
    IN p_driver_id INT
)
BEGIN
    INSERT INTO LICENSE (
        License_number, 
        License_type, 
        License_status,
        License_issue_date, 
        License_expiry_date, 
        Driver_id
    ) VALUES (
        p_license_number, 
        p_license_type, 
        p_license_status,
        p_issue_date, 
        p_expiry_date, 
        p_driver_id
    );
    SELECT 'License added' AS Message;
END //
DELIMITER ;

-- UPDATE License (e.g., renew, change status)
DELIMITER //
CREATE PROCEDURE UpdateLicense(
    IN p_license_number VARCHAR(13),
    IN p_new_type ENUM('Student Permit','Non-Professional','Professional'),
    IN p_new_status ENUM('valid','expired','suspended','revoked'),
    IN p_new_expiry DATE
)
BEGIN
    UPDATE LICENSE SET
        License_type = COALESCE(p_new_type, License_type),
        License_status = COALESCE(p_new_status, License_status),
        License_expiry_date = COALESCE(p_new_expiry, License_expiry_date)
    WHERE License_number = p_license_number;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- DELETE License (cascades to child tables automatically due to ON DELETE CASCADE)
DELIMITER //
CREATE PROCEDURE DeleteLicense(IN p_license_number VARCHAR(13))
BEGIN
    DELETE FROM LICENSE WHERE License_number = p_license_number;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- SEARCH License (by driver, status, expiration)
DELIMITER //
CREATE PROCEDURE SearchLicense(
    IN p_driver_lastname VARCHAR(50),
    IN p_license_status VARCHAR(20),
    IN p_expired_before DATE
)
BEGIN
    SELECT l.*, CONCAT(d.First_name, ' ', d.Last_name) AS DriverName
    FROM LICENSE l
    JOIN DRIVER d ON l.Driver_id = d.Driver_id
    WHERE (p_driver_lastname IS NULL OR d.Last_name LIKE CONCAT('%', p_driver_lastname, '%'))
      AND (p_license_status IS NULL OR l.License_status = p_license_status)
      AND (p_expired_before IS NULL OR l.License_expiry_date < p_expired_before);
END //
DELIMITER ;





-- =====================================================
-- Operations for LICENSE_DLCODES

-- For adding a DL code to a license
DELIMITER //
CREATE PROCEDURE AddLicenseDLCodes(
    IN p_license_number VARCHAR(13),
    IN p_dl_code VARCHAR(10)
)
BEGIN
    INSERT INTO LICENSE_DLCODES (License_number, Dl_codes) VALUES (p_license_number, p_dl_code);
    SELECT 'DL code added' AS Message;
END //
DELIMITER ;

-- For removing a DL code from a license
DELIMITER //
CREATE PROCEDURE RemoveLicenseDLCodes(
    IN p_license_number VARCHAR(13),
    IN p_dl_code VARCHAR(10)
)
BEGIN
    DELETE FROM LICENSE_DLCODES 
    WHERE License_number = p_license_number AND Dl_codes = p_dl_code;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For viewing all DL codes for a license
DELIMITER //
CREATE PROCEDURE GetLicenseDLCodes(IN p_license_number VARCHAR(13))
BEGIN
    SELECT Dl_codes FROM LICENSE_DLCODES WHERE License_number = p_license_number;
END //
DELIMITER ;





-- =====================================================
-- Operations for LICENSE_CONDITION

-- For adding a condition to a license
DELIMITER //
CREATE PROCEDURE AddLicenseCondition(
    IN p_license_number VARCHAR(13),
    IN p_condition VARCHAR(100)
)
BEGIN
    INSERT INTO LICENSE_CONDITION (License_number, `Condition`) VALUES (p_license_number, p_condition);
    SELECT 'Condition added' AS Message;
END //
DELIMITER ;

-- For removing a condition from a license
DELIMITER //
CREATE PROCEDURE RemoveLicenseCondition(
    IN p_license_number VARCHAR(13),
    IN p_condition VARCHAR(100)
)
BEGIN
    DELETE FROM LICENSE_CONDITION 
    WHERE License_number = p_license_number AND `Condition` = p_condition;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For viewing all conditions for a license
DELIMITER //
CREATE PROCEDURE GetLicenseConditions(IN p_license_number VARCHAR(13))
BEGIN
    SELECT `Condition` FROM LICENSE_CONDITION WHERE License_number = p_license_number;
END //
DELIMITER ;





-- =====================================================
-- Operations for TRAFFIC_VIOLATION_TYPE 

-- For adding a row in TRAFFIC_VIOLATION_TYPE
DELIMITER //
CREATE PROCEDURE AddViolationType(
    IN p_name VARCHAR(100),
    IN p_base_fine DECIMAL(10,2),
    IN p_description TEXT
)
BEGIN
    INSERT INTO TRAFFIC_VIOLATION_TYPE (Name, Base_fine, Description)
    VALUES (p_name, p_base_fine, p_description);
    SELECT LAST_INSERT_ID() AS NewViolationTypeID;
END //
DELIMITER ;

-- For update a row in TRAFFIC_VIOLATION_TYPE
DELIMITER //
CREATE PROCEDURE UpdateViolationType(
    IN p_type_id INT,
    IN p_new_name VARCHAR(100),
    IN p_new_fine DECIMAL(10,2),
    IN p_new_description TEXT
)
BEGIN
    UPDATE TRAFFIC_VIOLATION_TYPE SET
        Name = COALESCE(p_new_name, Name),
        Base_fine = COALESCE(p_new_fine, Base_fine),
        Description = COALESCE(p_new_description, Description)
    WHERE Violation_type_id = p_type_id;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For deleting a row in TRAFFIC_VIOLATION_TYPE (only if not referenced by any violation)
DELIMITER //
CREATE PROCEDURE DeleteViolationType(IN p_type_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Cannot delete violation type with existing violations.' AS Error;
    END;
    START TRANSACTION;
    DELETE FROM TRAFFIC_VIOLATION_TYPE WHERE Violation_type_id = p_type_id;
    COMMIT;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For searching row/s in TRAFFIC_VIOLATION_TYPE
DELIMITER //
CREATE PROCEDURE SearchViolationType(IN p_name_keyword VARCHAR(100))
BEGIN
    SELECT * FROM TRAFFIC_VIOLATION_TYPE
    WHERE p_name_keyword IS NULL OR Name LIKE CONCAT('%', p_name_keyword, '%');
END //
DELIMITER ;





-- =====================================================
-- Operations for OFFICER 

-- For adding a row in OFFICER
DELIMITER //
CREATE PROCEDURE AddOfficer(
    IN p_station VARCHAR(100),
    IN p_rank VARCHAR(50),
    IN p_badge VARCHAR(20),
    IN p_first VARCHAR(50),
    IN p_middle VARCHAR(50),
    IN p_last VARCHAR(50),
    IN p_suffix VARCHAR(10)
)
BEGIN
    INSERT INTO OFFICER (
        Station, 
        `Rank`, 
        Badge_number, 
        First_name, 
        Middle_name, 
        Last_name, 
        Suffix
    ) VALUES (
        p_station, 
        p_rank, 
        p_badge, 
        p_first, 
        p_middle, 
        p_last, 
        p_suffix);
    SELECT LAST_INSERT_ID() AS NewOfficerID;
END //
DELIMITER ;

-- FOr updating a row in OFFICER
DELIMITER //
CREATE PROCEDURE UpdateOfficer(
    IN p_officer_id INT,
    IN p_station VARCHAR(100),
    IN p_rank VARCHAR(50),
    IN p_badge VARCHAR(20),
    IN p_first VARCHAR(50),
    IN p_middle VARCHAR(50),
    IN p_last VARCHAR(50),
    IN p_suffix VARCHAR(10)
)
BEGIN
    UPDATE OFFICER SET
        Station = COALESCE(p_station, Station),
        `Rank` = COALESCE(p_rank, `Rank`),
        Badge_number = COALESCE(p_badge, Badge_number),
        First_name = COALESCE(p_first, First_name),
        Middle_name = COALESCE(p_middle, Middle_name),
        Last_name = COALESCE(p_last, Last_name),
        Suffix = COALESCE(p_suffix, Suffix)
    WHERE Officer_id = p_officer_id;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For deleting a row in OFFICER (only if no violations reference it)
DELIMITER //
CREATE PROCEDURE DeleteOfficer(IN p_officer_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Cannot delete officer with recorded violations.' AS Error;
    END;
    START TRANSACTION;
    DELETE FROM OFFICER WHERE Officer_id = p_officer_id;
    COMMIT;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- Fow searching row/s in OFFICER (by officer's last name, badge, station)
DELIMITER //
CREATE PROCEDURE SearchOfficer(
    IN p_lastname VARCHAR(50),
    IN p_badge VARCHAR(20),
    IN p_station VARCHAR(100)
)
BEGIN
    SELECT * FROM OFFICER
    WHERE (p_lastname IS NULL OR Last_name LIKE CONCAT('%', p_lastname, '%'))
      AND (p_badge IS NULL OR Badge_number = p_badge)
      AND (p_station IS NULL OR Station LIKE CONCAT('%', p_station, '%'));
END //
DELIMITER ;


-- =====================================================
-- Operations for LOCATION

-- For adding a row in LOCATION
DELIMITER //
CREATE PROCEDURE AddLocation(
    IN p_city VARCHAR(100),
    IN p_region VARCHAR(100)
)
BEGIN
    INSERT INTO LOCATION (City, Region) VALUES (p_city, p_region);
    SELECT LAST_INSERT_ID() AS NewLocationID;
END //
DELIMITER ;

-- For updating a row in LOCATION
DELIMITER //
CREATE PROCEDURE UpdateLocation(
    IN p_location_id INT,
    IN p_city VARCHAR(100),
    IN p_region VARCHAR(100)
)
BEGIN
    UPDATE LOCATION SET
        City = COALESCE(p_city, City),
        Region = COALESCE(p_region, Region)
    WHERE Location_id = p_location_id;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For deleting a row in LOCATION (only if not used in any violation)
DELIMITER //
CREATE PROCEDURE DeleteLocation(IN p_location_id INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Cannot delete location with recorded violations.' AS Error;
    END;
    START TRANSACTION;
    DELETE FROM LOCATION WHERE Location_id = p_location_id;
    COMMIT;
    SELECT ROW_COUNT() AS RowsAffected;
END //
DELIMITER ;

-- For searching row/s in LOCATION
DELIMITER //
CREATE PROCEDURE SearchLocation(
    IN p_city VARCHAR(100),
    IN p_region VARCHAR(100)
)
BEGIN
    SELECT * FROM LOCATION
    WHERE (p_city IS NULL OR City LIKE CONCAT('%', p_city, '%'))
      AND (p_region IS NULL OR Region LIKE CONCAT('%', p_region, '%'));
END //
DELIMITER ;





-- ==================================================
-- For populating the tables
-- I used the "INSERT INTO" statements instead of the stored procedures kasi maramihan na insert.

-- LOCATION (cities and regions)
INSERT INTO LOCATION (Location_id, City, Region) VALUES
(1,     'Quezon City',  'National Capital Region (NCR)'),
(2,     'Manila',       'National Capital Region (NCR)'),
(3,     'Makati',       'National Capital Region (NCR)'),
(4,     'Taguig',       'National Capital Region (NCR)'),
(5,     'Pasig',        'National Capital Region (NCR)'),
(6,     'Calamba',      'CALABARZON'),
(7,     'Sta. Rosa',    'CALABARZON'),
(8,     'Baguio',       'Cordillera Administrative Region (CAR)'),
(9,     'Cebu City',    'Central Visayas'),
(10,    'Davao City',   'Davao Region');

-- TRAFFIC VIOLATION TYPE (common violations in PH)
INSERT INTO TRAFFIC_VIOLATION_TYPE (Violation_type_id, Name, Base_fine, Description) VALUES
(1, 'Overspeeding',                         2000.00,    'Exceeding the maximum speed limit by more than 20 km/h'),
(2, 'Reckless Driving',                     2500.00,    'Driving without due care or in a manner dangerous to the public'),
(3, 'Illegal Parking',                      1000.00,    'Parking in no-parking zones, sidewalks, or obstructing traffic'),
(4, 'No Seatbelt',                          500.00,     'Driver or passenger not wearing seatbelt'),
(5, 'Using Mobile Phone While Driving',     1500.00,    'Handling a mobile device while vehicle is in motion'),
(6, 'No OR/CR',                             3000.00,    'Failure to present Official Receipt and Certificate of Registration'),
(7, 'Disregarding Traffic Sign',            1000.00,    'Ignoring stop signs, no left/right turn signs, etc.'),
(8, 'Driving Without License',              3500.00,    'Driver not carrying or without a valid license');

-- OFFICER (LTO or PNP traffic enforcers)
INSERT INTO OFFICER (Officer_id, Station, `Rank`, Badge_number, First_name, Middle_name, Last_name, Suffix) VALUES
(1,     'LTO Central Office - Quezon City',     'Senior Traffic Officer',   'LTO-001',      'Ramon',    'Santos',       'Dela Cruz',    NULL),
(2,     'PNP Highway Patrol - Manila',          'Police Corporal',          'PNP-8823',     'Maria',    'Reyes',        'Garcia',       NULL),
(3,     'LTO Makati District Office',           'Traffic Investigator',     'LTO-045',      'Jose',     'Mendoza',      'Ramos', 'Jr.'),
(4,     'MMDA - Pasig',                         'Traffic Enforcer',         'MMDA-231',     'Antonio',  'Luna',         'Fernandez',    NULL),
(5,     'LTO Calamba',                          'Senior Traffic Officer',   'LTO-112',      'Carmela',  'Villanueva',   'Torres',       NULL),
(6,     'PNP Taguig',                           'Patrolman',                'PNG-5561',     'Ricardo',  'Gomez',        'Santillan',    NULL),
(7,     'LTO Baguio',                           'Traffic Investigator',     'LTO-089',      'Eduardo',  'Cruz',         'Aquino',       'III'),
(8,     'Cebu City Traffic Office',             'Traffic Enforcer',         'CCTO-442',     'Andrea',   'Sotto',        'Lim',          NULL),
(9,     'LTO Davao',                            'Senior Traffic Officer',   'LTO-367',      'Roberto',  'Dizon',        'Magsaysay',    NULL),
(10,    'MMDA - EDSA',                          'Traffic Enforcer',         'MMDA-780',     'Kristine', 'Castro',       'Rivera',       NULL);

-- DRIVER (20 drivers)
INSERT INTO DRIVER (Driver_id, First_name, Middle_name, Last_name, Suffix, Date_of_birth, Weight, Height, Sex_assigned_at_birth, Nationality, Civil_status, Contact_number, Blood_type, House_number, Street_village, Barangay, City_municipality, Province, Region, Zip_code) VALUES
(1,     'Juan',         'Dimagiba',     'Santos',       NULL,   '1985-03-12', 72.5, 168.0, 'Male',      'Filipino', 'Married',  '09123456789', 'O+',    '12',   'Rizal St.',            'Brgy. San Antonio',        'Quezon City',  'Metro Manila',     'NCR',              '1100'),
(2,     'Maria',        'Cruz',         'Reyes',        NULL,   '1990-07-22', 58.0, 162.0, 'Female',    'Filipino', 'Single',   '09234567890', 'A+',    '8',    'Mabini Ave.',          'Brgy. Poblacion',          'Manila',       'Metro Manila',     'NCR',              '1000'),
(3,     'Jose',         'Protacio',     'Mercado',      'Jr.',  '1978-11-05', 80.0, 175.0, 'Male',      'Filipino', 'Married',  '09345678901', 'B+',    '22',   'Luna St.',             'Brgy. North',              'Makati',       'Metro Manila',     'NCR',              '1200'),
(4,     'Ana',          'Victoria',     'Lopez',        NULL,   '2000-01-15', 52.0, 158.0, 'Female',    'Filipino', 'Single',   '09456789012', 'AB+',   '5',    'Sampaguita St.',       'Brgy. South',              'Taguig',       'Metro Manila',     'NCR',              '1630'),
(5,     'Ricardo',      'Salvador',     'Gonzales',     NULL,   '1982-09-30', 85.0, 180.0, 'Male',      'Filipino', 'Divorced', '09567890123', 'O-',    '77',   'Bonifacio Drive',      'Brgy. Kapitolyo',          'Pasig',        'Metro Manila',     'NCR',              '1600'),
(6,     'Cristina',     'Luz',          'Fernandez',    NULL,   '1995-04-18', 60.0, 165.0, 'Female',    'Filipino', 'Married',  '09678901234', 'A-',    '3',    'J.P. Rizal St.',       'Brgy. Halang',             'Calamba',      'Laguna',           'CALABARZON',       '4027'),
(7,     'Roberto',      'Mabini',       'Villanueva',   NULL,   '1975-12-01', 78.0, 172.0, 'Male',      'Filipino', 'Widowed',  '09789012345', 'B-',    '99',   'P. Burgos St.',        'Brgy. Balibago',           'Sta. Rosa',    'Laguna',           'CALABARZON',       '4026'),
(8,     'Teresita',     'Guevarra',     'Ramirez',      NULL,   '1988-06-25', 62.0, 160.0, 'Female',    'Filipino', 'Single',   '09890123456', 'O+',    '14',   'Session Road',         'Brgy. Upper Session',      'Baguio',       'Benguet',          'CAR',              '2600'),
(9,     'Manuel',       'Aquino',       'Torres',       'III',  '1992-02-10', 70.0, 170.0, 'Male',      'Filipino', 'Married',  '09901234567', 'AB-',   '6',    'Osmeña Blvd.',         'Brgy. Capitol',            'Cebu City',    'Cebu',             'Central Visayas',  '6000'),
(10,    'Luzviminda',   'Dimagiba',     'Sarmiento',    NULL,   '1980-08-19', 65.0, 163.0, 'Female',    'Filipino', 'Married',  '09012345678', 'A+',    '25',   'San Pedro St.',        'Brgy. 5-A',                'Davao City',   'Davao del Sur',    'Davao Region',     '8000'),
(11,    'Gregorio',     'Hizon',        'Panganiban',   NULL,   '1998-05-05', 68.0, 174.0, 'Male',      'Filipino', 'Single',   '09123456780', 'B+',    '11',   'Taft Ave.',            'Brgy. 720',                'Manila',       'Metro Manila',     'NCR',              '1000'),
(12,    'Fe',           'Corazon',      'Natividad',    NULL,   '1972-10-20', 55.0, 155.0, 'Female',    'Filipino', 'Widowed',  '09234567891', 'O+',    '4',    'Gil Puyat St.',        'Brgy. Bel-Air',            'Makati',       'Metro Manila',     'NCR',              '1209'),
(13,    'Rogelio',      'Serrano',      'Dizon',        NULL,   '1987-07-14', 82.0, 178.0, 'Male',      'Filipino', 'Divorced', '09345678902', 'AB+',   '33',   'Shaw Blvd.',           'Brgy. Wack-Wack',          'Mandaluyong',  'Metro Manila',     'NCR',              '1550'),
(14,    'Marilou',      'Santiago',     'Castro',       NULL,   '1993-03-28', 59.0, 164.0, 'Female',    'Filipino', 'Single',   '09456789013', 'A-',    '7',    'McArthur Highway',     'Brgy. Balatas',            'Calamba',      'Laguna',           'Calabarzon',       '4027'),
(15,    'Ferdinand',    'Lacsamana',    'Marcelo',      NULL,   '1984-12-12', 90.0, 185.0, 'Male',      'Filipino', 'Married',  '09567890124', 'B+',    '45',   'Roxas Blvd.',          'Brgy. Baclaran',           'Pasay',        'Metro Manila',     'NCR',              '1300'),
(16,    'Gloria',       'Rivera',       'Alvarez',      NULL,   '1970-09-09', 67.0, 162.0, 'Female',    'Filipino', 'Married',  '09678901235', 'O-',    '2',    'Leonard Wood Rd.',     'Brgy. PMA',                'Baguio',       'Benguet',          'CAR',              '2600'),
(17,    'Ramon',        'Bautista',     'Valdez',       'Jr.',  '1996-01-01', 74.0, 176.0, 'Male',      'Filipino', 'Single',   '09789012346', 'A+',    '19',   'Nacional Highway',     'Brgy. Pulong Sta. Cruz',   'Sta. Rosa',    'Laguna',           'CALABRZON',        '4026'),
(18,    'Rosario',      'Magsaysay',    'Flores',       NULL,   '1989-11-30', 61.0, 159.0, 'Female',    'Filipino', 'Single',   '09890123457', 'AB-',   '88',   'Gov. M. Cuenco Ave.',  'Brgy. Banilad',            'Cebu City',    'Cebu',             'Central Visayas',  '6000'),
(19,    'Efren',        'Peña',         'Gatchalian',   NULL,   '1977-06-17', 79.0, 173.0, 'Male',      'Filipino', 'Married',  '09901234568', 'O+',    '56',   'J.P. Laurel Ave.',     'Brgy. Buhangin',           'Davao City',   'Davao del Sur',    'Davao Region',     '8000'),
(20,    'Lorna',        'Dimagiba',     'Cruz',         NULL,   '2002-08-08', 50.0, 156.0, 'Female',    'Filipino', 'Single',   '09012345679', 'B-',    '10',   'Katipunan Ave.',       'Brgy. Loyola Heights',     'Quezon City',  'Metro Manila',     'NCR',              '1108');

-- LICENSE (one per driver)
INSERT INTO LICENSE (License_number, License_type, License_status, License_issue_date, License_expiry_date, Driver_id) VALUES
('D12-34-567890', 'Professional',       'valid',        '2020-01-15', '2025-01-15', 1),
('D98-76-543210', 'Non-Professional',   'expired',      '2018-05-20', '2023-05-20', 2),
('D45-67-890123', 'Professional',       'suspended',    '2019-09-10', '2024-09-10', 3),
('D23-45-678901', 'Student Permit',     'valid',        '2024-02-01', '2025-02-01', 4),
('D56-78-901234', 'Professional',       'valid',        '2021-07-18', '2026-07-18', 5),
('D67-89-012345', 'Non-Professional',   'valid',        '2020-12-05', '2025-12-05', 6),
('D78-90-123456', 'Professional',       'revoked',      '2017-03-22', '2022-03-22', 7),
('D89-01-234567', 'Non-Professional',   'expired',      '2019-11-14', '2024-11-14', 8),
('D90-12-345678', 'Professional',       'valid',        '2022-06-30', '2027-06-30', 9),
('D01-23-456789', 'Student Permit',     'valid',        '2023-10-10', '2024-10-10', 10),
('D12-34-567891', 'Non-Professional',   'valid',        '2021-04-25', '2026-04-25', 11),
('D23-45-678902', 'Professional',       'expired',      '2016-08-08', '2021-08-08', 12),
('D34-56-789013', 'Professional',       'valid',        '2020-09-17', '2025-09-17', 13),
('D45-67-890124', 'Non-Professional',   'suspended',    '2019-12-03', '2024-12-03', 14),
('D56-78-901235', 'Professional',       'valid',        '2023-02-28', '2028-02-28', 15),
('D67-89-012346', 'Non-Professional',   'valid',        '2020-05-19', '2025-05-19', 16),
('D78-90-123457', 'Professional',       'valid',        '2022-11-11', '2027-11-11', 17),
('D89-01-234568', 'Student Permit',     'valid',        '2024-03-01', '2025-03-01', 18),
('D90-12-345679', 'Non-Professional',   'expired',      '2017-07-07', '2022-07-07', 19),
('D01-23-456790', 'Professional',       'valid',        '2021-01-21', '2026-01-21', 20);

-- LICENSE DL CODES (restriction codes - common in PH)
-- A = Motorcycle, B = Light vehicle, B1 = Light vehicle automatic, C = Heavy vehicle, etc.
INSERT INTO LICENSE_DLCODES (License_number, Dl_codes) VALUES
('D12-34-567890', 'A'), ('D12-34-567890', 'B'), ('D12-34-567890', 'B1'),
('D98-76-543210', 'A'),
('D45-67-890123', 'B'), ('D45-67-890123', 'C'),
('D23-45-678901', 'A'),
('D56-78-901234', 'B'), ('D56-78-901234', 'B1'),
('D67-89-012345', 'A'), ('D67-89-012345', 'B'),
('D78-90-123456', 'B'), ('D78-90-123456', 'C'),
('D89-01-234567', 'A'),
('D90-12-345678', 'B'), ('D90-12-345678', 'B1'), ('D90-12-345678', 'C'),
('D01-23-456789', 'A'),
('D12-34-567891', 'A'), ('D12-34-567891', 'B'),
('D23-45-678902', 'B'),
('D34-56-789013', 'B'), ('D34-56-789013', 'C'),
('D45-67-890124', 'A'),
('D56-78-901235', 'B'), ('D56-78-901235', 'B1'),
('D67-89-012346', 'A'), ('D67-89-012346', 'B'),
('D78-90-123457', 'B'),
('D89-01-234568', 'A'),
('D90-12-345679', 'B'),
('D01-23-456790', 'B'), ('D01-23-456790', 'C');

-- LICENSE CONDITIONS (for some drivers)
INSERT INTO LICENSE_CONDITION (License_number, `Condition`) VALUES
('D12-34-567890', 'Wear corrective lenses'),
('D45-67-890123', 'Automatic transmission only'),
('D90-12-345678', 'Wear corrective lenses'),
('D23-45-678902', 'Daylight driving only'),
('D01-23-456790', 'Must have vehicle with hand controls');

-- VEHICLE (30 vehicles)
INSERT INTO VEHICLE (Vehicle_id, Engine_number, Plate_number, Chassis_number, Vehicle_type, Make, Model, Year, Body_type, Capacity, Color, Driver_id) VALUES
(1,     'ENG1001A',     'ABC1234', 'CHS1001XYZ', 'private car',             'Toyota',       'Vios',             2020, 'Sedan',          5, 'White',     1),
(2,     'ENG1002B',     'DEF5678', 'CHS1002XYZ', 'motorcycle',              'Honda',        'Click 125i',       2022, 'Scooter',        2, 'Black',     2),
(3,     'ENG1003C',     'GHI9012', 'CHS1003XYZ', 'private car',             'Mitsubishi',   'Mirage',           2019, 'Hatchback',      5, 'Red',       3),
(4,     'ENG1004D',     'JKL3456', 'CHS1004XYZ', 'motorcycle',              'Yamaha',       'Mio i125',         2021, 'Scooter',        2, 'Blue',      4),
(5,     'ENG1005E',     'MNO7890', 'CHS1005XYZ', 'public utility vehicle',  'Toyota',       'Hi-Ace',           2018, 'Van',            15, 'White',    5),
(6,     'ENG1006F',     'PQR2345', 'CHS1006XYZ', 'private car',             'Honda',        'Civic',            2021, 'Sedan',          5, 'Gray',      6),
(7,     'ENG1007G',     'STU6789', 'CHS1007XYZ', 'truck',                   'Isuzu',        'NPR',              2017, 'Cargo Truck',    3, 'White',     7),
(8,     'ENG1008H',     'VWX0123', 'CHS1008XYZ', 'motorcycle',              'Kawasaki',     'Barako 175',       2020, 'Standard',       2, 'Green',     8),
(9,     'ENG1009I',     'YZA4567', 'CHS1009XYZ', 'private car',             'Ford',         'Everest',          2022, 'SUV',            7, 'Silver',    9),
(10,    'ENG1010J',     'BCD8901', 'CHS1010XYZ', 'private car',             'Suzuki',       'Swift',            2020, 'Hatchback',      5, 'Yellow',    10),
(11,    'ENG1011K',     'EFG2345', 'CHS1011XYZ', 'motorcycle',              'Honda',        'Beat',             2023, 'Scooter',        2, 'Red',       11),
(12,    'ENG1012L',     'HIJ6789', 'CHS1012XYZ', 'private car',             'Nissan',       'Navara',           2019, 'Pickup',         5, 'Black',     12),
(13,    'ENG1013M',     'KLM0123', 'CHS1013XYZ', 'private car',             'Toyota',       'Innova',           2021, 'MPV',            7, 'Brown',     13),
(14,    'ENG1014N',     'NOP4567', 'CHS1014XYZ', 'motorcycle',              'Yamaha',       'NMAX 155',         2022, 'Scooter',        2, 'Gray',      14),
(15,    'ENG1015O',     'QRS8901', 'CHS1015XYZ', 'public utility vehicle',  'Hyundai',      'County',           2016, 'Bus',            30, 'White',    15),
(16,    'ENG1016P',     'TUV2345', 'CHS1016XYZ', 'private car',             'Mitsubishi',   'Montero Sport',    2020, 'SUV',            7, 'Black',     16),
(17,    'ENG1017Q',     'WXY6789', 'CHS1017XYZ', 'truck',                   'Foton',        'Thunder',          2018, 'Dump Truck',     3, 'Orange',    17),
(18,    'ENG1018R',     'ZAB0123', 'CHS1018XYZ', 'motorcycle',              'Kymco',        'Like 150i',        2021, 'Scooter',        2, 'White',     18),
(19,    'ENG1019S',     'CDE4567', 'CHS1019XYZ', 'private car',             'Hyundai',      'Accent',           2020, 'Sedan',          5, 'Blue',      19),
(20,    'ENG1020T',     'FGH8901', 'CHS1020XYZ', 'private car',             'Toyota',       'Wigo',             2022, 'Hatchback',      5, 'Green',     20),
(21,    'ENG1021U',     'IJK2345', 'CHS1021XYZ', 'motorcycle',              'Suzuki',       'Skydrive',         2020, 'Scooter',        2, 'Black',     1),
(22,    'ENG1022V',     'LMN6789', 'CHS1022XYZ', 'private car',             'Honda',        'BR-V',             2021, 'SUV',            7, 'White',     2),
(23,    'ENG1023W',     'OPQ0123', 'CHS1023XYZ', 'public utility vehicle',  'Toyota',       'Coaster',          2019, 'Mini Bus',       24, 'White',    3),
(24,    'ENG1024X',     'RST4567', 'CHS1024XYZ', 'motorcycle',              'Honda',        'TMX 125 Alpha',    2022, 'Standard',       2, 'Red',       4),
(25,    'ENG1025Y',     'UVW8901', 'CHS1025XYZ', 'private car',             'Ford',         'Ranger',           2020, 'Pickup',         5, 'Orange',    5),
(26,    'ENG1026Z',     'XYZ2345', 'CHS1026XYZ', 'truck',                   'Mitsubishi',   'Canter',           2017, 'Cargo Truck',    3, 'White',     6),
(27,    'ENG1027AA',    'BCD6789', 'CHS1027XYZ', 'private car',             'Nissan',       'Almera',           2021, 'Sedan',          5, 'Silver',    7),
(28,    'ENG1028AB',    'EFG0123', 'CHS1028XYZ', 'motorcycle',              'Kawasaki',     'CT150',            2019, 'Standard',       2, 'Blue',      8),
(29,    'ENG1029AC',    'HIJ4567', 'CHS1029XYZ', 'private car',             'Geely',        'Coolray',          2022, 'SUV',            5, 'Red',       9),
(30,    'ENG1030AD',    'KLM8901', 'CHS1030XYZ', 'private car',             'Toyota',       'Corolla Altis',    2018, 'Sedan',          5, 'Gray',      10);

-- VEHICLE REGISTRATION (one per vehicle)
INSERT INTO VEHICLE_REGISTRATION (Registration_number, Registration_date, Expiration_date, Registration_status, Official_receipt_number, Official_receipt_date, Document_ref_no, Ownership_type, Transfer_reason, Ownership_start_date, Ownership_end_date, Vehicle_id) VALUES
('REG10001', '2020-01-20', '2021-01-19', 'expired', 'OR10001', '2020-01-20', NULL,      'owned',        NULL,                       '2020-01-20',   NULL,           1),
('REG10002', '2022-03-15', '2023-03-14', 'expired', 'OR10002', '2022-03-15', NULL,      'owned',        NULL,                       '2022-03-15',   NULL,           2),
('REG10003', '2021-05-10', '2025-05-09', 'active',  'OR10003', '2021-05-10', NULL,      'financed',     NULL,                       '2021-05-10',   '2025-05-09',   3),
('REG10004', '2023-01-30', '2024-01-29', 'active',  'OR10004', '2023-01-30', NULL,      'owned',        NULL,                       '2023-01-30',   NULL,           4),
('REG10005', '2018-06-01', '2019-05-31', 'expired', 'OR10005', '2018-06-01', 'DR-001',  'owned',        NULL,                       '2018-06-01',   '2019-05-31',   5),
('REG10006', '2021-07-12', '2025-07-11', 'active',  'OR10006', '2021-07-12', NULL,      'owned',        NULL,                       '2021-07-12',   NULL,           6),
('REG10007', '2017-11-20', '2018-11-19', 'expired', 'OR10007', '2017-11-20', NULL,      'owned',        NULL,                       '2017-11-20',   '2018-11-19',   7),
('REG10008', '2020-08-08', '2024-08-07', 'active',  'OR10008', '2020-08-08', NULL,      'owned',        NULL,                       '2020-08-08',   NULL,           8),
('REG10009', '2022-10-05', '2023-10-04', 'expired', 'OR10009', '2022-10-05', NULL,      'leased',       'Leased from ABC Corp',     '2022-10-05',   '2023-10-04',   9),
('REG10010', '2023-02-14', '2024-02-13', 'active',  'OR10010', '2023-02-14', NULL,      'owned',        NULL,                       '2023-02-14',   NULL,           10),
('REG10011', '2021-04-22', '2025-04-21', 'active',  'OR10011', '2021-04-22', NULL,      'owned',        NULL,                       '2021-04-22',   NULL,           11),
('REG10012', '2019-09-09', '2020-09-08', 'expired', 'OR10012', '2019-09-09', NULL,      'financed',     NULL,                       '2019-09-09',   '2020-09-08',   12),
('REG10013', '2022-12-01', '2026-11-30', 'active',  'OR10013', '2022-12-01', 'DR-045',  'owned',        NULL,                       '2022-12-01',   NULL,           13),
('REG10014', '2023-03-18', '2024-03-17', 'active',  'OR10014', '2023-03-18', NULL,      'owned',        NULL,                       '2023-03-18',   NULL,           14),
('REG10015', '2016-05-25', '2017-05-24', 'expired', 'OR10015', '2016-05-25', NULL,      'owned',        NULL,                       '2016-05-25',   '2017-05-24',   15),
('REG10016', '2020-07-19', '2024-07-18', 'active',  'OR10016', '2020-07-19', NULL,      'owned',        NULL,                       '2020-07-19',   NULL,           16),
('REG10017', '2018-10-11', '2019-10-10', 'expired', 'OR10017', '2018-10-11', NULL,      'owned',        NULL,                       '2018-10-11',   '2019-10-10',   17),
('REG10018', '2021-11-27', '2025-11-26', 'active',  'OR10018', '2021-11-27', NULL,      'owned',        NULL,                       '2021-11-27',   NULL,           18),
('REG10019', '2022-01-05', '2026-01-04', 'active',  'OR10019', '2022-01-05', NULL,      'financed',     NULL,                       '2022-01-05',   NULL,           19),
('REG10020', '2023-04-30', '2024-04-29', 'active',  'OR10020', '2023-04-30', NULL,      'owned',        NULL,                       '2023-04-30',   NULL,           20),
('REG10021', '2020-06-15', '2021-06-14', 'expired', 'OR10021', '2020-06-15', NULL,      'owned',        NULL,                       '2020-06-15',   '2021-06-14',   21),
('REG10022', '2021-08-20', '2025-08-19', 'active',  'OR10022', '2021-08-20', NULL,      'owned',        NULL,                       '2021-08-20',   NULL,           22),
('REG10023', '2019-12-12', '2020-12-11', 'expired', 'OR10023', '2019-12-12', NULL,      'owned',        NULL,                       '2019-12-12',   '2020-12-11',   23),
('REG10024', '2022-05-09', '2026-05-08', 'active',  'OR10024', '2022-05-09', NULL,      'owned',        NULL,                       '2022-05-09',   NULL,           24),
('REG10025', '2020-09-30', '2021-09-29', 'expired', 'OR10025', '2020-09-30', NULL,      'leased',       'Leased from Rent-A-Car',   '2020-09-30',   '2021-09-29',   25),
('REG10026', '2021-12-14', '2025-12-13', 'active',  'OR10026', '2021-12-14', NULL,      'owned',        NULL,                       '2021-12-14',   NULL,           26),
('REG10027', '2023-02-28', '2024-02-27', 'active',  'OR10027', '2023-02-28', NULL,      'owned',        NULL,                       '2023-02-28',   NULL,           27),
('REG10028', '2019-04-05', '2020-04-04', 'expired', 'OR10028', '2019-04-05', NULL,      'owned',        NULL,                       '2019-04-05',   '2020-04-04',   8),
('REG10029', '2022-07-17', '2026-07-16', 'active',  'OR10029', '2022-07-17', NULL,      'financed',     NULL,                       '2022-07-17',   NULL,           29),
('REG10030', '2021-10-25', '2025-10-24', 'active',  'OR10030', '2021-10-25', NULL,      'owned',        NULL,                       '2021-10-25',   NULL,           30);

-- TRAFFIC VIOLATION (15 violations)
INSERT INTO TRAFFIC_VIOLATION (Violation_id, Violation_date, Violation_status, Fine_amount, Payment_date, Driver_id, Vehicle_id, Violation_type_id, Officer_id, Location_id) VALUES
(1,  '2023-06-15', 'paid',         2000.00, '2023-06-20',  1,  1,  1, 1,  1),
(2,  '2023-07-22', 'unpaid',       1000.00, NULL,          3,  3,  3, 2,  2),
(3,  '2023-08-05', 'paid',         500.00, '2023-08-10',   2,  2,  4, 3,  3),
(4,  '2023-09-12', 'contested',    2500.00, NULL,          5,  5,  2, 4,  4),
(5,  '2023-10-01', 'paid',         1500.00, '2023-10-05',  7,  7,  5, 5,  5),
(6,  '2023-11-18', 'unpaid',       3000.00, NULL,          9,  9,  6, 6,  6),
(7,  '2024-01-10', 'paid',         1000.00, '2024-01-15',  11, 11, 7, 7,  7),
(8,  '2024-02-14', 'paid',         3500.00, '2024-02-20',  13, 13, 8, 8,  8),
(9,  '2024-03-05', 'unpaid',       2000.00, NULL,          15, 15, 1, 9,  9),
(10, '2024-03-20', 'paid',         1000.00, '2024-03-25',  17, 17, 3, 10, 10),
(11, '2024-04-02', 'contested',    2500.00, NULL,          19, 19, 2, 1,  1),
(12, '2024-04-15', 'paid',         1500.00, '2024-04-18',  4,  4,  5, 2,  2),
(13, '2024-05-01', 'unpaid',       3000.00, NULL,          6,  6,  6, 3,  3),
(14, '2024-05-12', 'paid',         500.00, '2024-05-15',   8,  8,  4, 4,  4),
(15, '2024-05-25', 'unpaid',       2000.00, NULL,          10, 10, 1, 5,  5),
(16, '2023-12-05', 'paid',         1000.00, '2023-12-10',  1,  21, 7, 6,  6),
(17, '2024-01-25', 'unpaid',       3500.00, NULL,          2,  22, 8, 7,  7),
(18, '2024-04-10', 'paid',         2000.00, '2024-04-14',  3,  23, 1, 8,  8);





-- ===========================================
 -- This is for the views and stored procedures for reports

-- View all registered drivers filtered by: License type, License status, Age range, Sex
DELIMITER //
CREATE PROCEDURE GetDriversByFilters(
    IN p_license_type VARCHAR(20),
    IN p_license_status VARCHAR(20),
    IN p_min_age INT,
    IN p_max_age INT,
    IN p_sex VARCHAR(10))
BEGIN
    SELECT  d.Driver_id, 
            CONCAT(d.First_name, ' ',COALESCE(d.Middle_name, "N/A"), ' ', d.Last_name) AS Full_Name, 
            d.Sex_assigned_at_birth AS Sex,
            d.Date_of_birth, 
            TIMESTAMPDIFF(YEAR, d.Date_of_birth, CURDATE()) AS Age, 
            l.License_number, 
            l.License_type, 
            l.License_status
    FROM DRIVER d
    JOIN LICENSE l ON d.Driver_id = l.Driver_id
    WHERE (p_license_type IS NULL OR l.License_type = p_license_type)
      AND (p_license_status IS NULL OR l.License_status = p_license_status)
      AND (p_min_age IS NULL OR TIMESTAMPDIFF(YEAR, d.Date_of_birth, CURDATE()) >= p_min_age)
      AND (p_max_age IS NULL OR TIMESTAMPDIFF(YEAR, d.Date_of_birth, CURDATE()) <= p_max_age)
      AND (p_sex IS NULL OR d.Sex_assigned_at_birth = p_sex);
END //
DELIMITER ;

-- View all vehicles owned by a given driver.
DELIMITER //
CREATE PROCEDURE GetVehiclesByDriver(IN p_driver_id INT)
BEGIN
    SELECT v.*
    FROM VEHICLE v
    WHERE v.Driver_id = p_driver_id;
END //
DELIMITER ;

-- View all vehicles with expired registrations as of a given date.
-- Create a debug version to see what date is being used
DELIMITER //
CREATE PROCEDURE GetExpiredRegistrations(IN p_as_of_date DATE)
BEGIN
    SELECT  v.Vehicle_id, 
            v.Plate_number, 
            v.Make, 
            v.Model, 
            vr.Registration_number, 
            vr.Expiration_date, 
            vr.Registration_status  
    FROM VEHICLE v
    JOIN VEHICLE_REGISTRATION vr ON v.Vehicle_id = vr.Vehicle_id
    WHERE vr.Expiration_date <= p_as_of_date;
END //
DELIMITER ;


-- View all drivers with expired or suspended licenses.
CREATE VIEW ExpiredOrSuspendedLicenses AS
SELECT  d.Driver_id,
        CONCAT(d.First_name, ' ', d.Last_name) AS Full_Name,
        l.License_number,
        l.License_type,
        l.License_status,
        l.License_expiry_date
FROM DRIVER d
JOIN LICENSE l ON d.Driver_id = l.Driver_id
WHERE l.License_status IN ('expired', 'suspended');

-- View all traffic violations committed by a given driver within a specified date range.
DELIMITER //
CREATE PROCEDURE GetViolationsByDriverAndDateRange(
    IN p_driver_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE)
BEGIN
    SELECT  tv.Violation_id, 
            tv.Violation_date, 
            tv.Fine_amount, 
            tv.Violation_status,
            tvt.Name AS Violation_Type,
            l.City, 
            l.Region,
            v.Plate_number
    FROM TRAFFIC_VIOLATION tv
    JOIN TRAFFIC_VIOLATION_TYPE tvt ON tv.Violation_type_id = tvt.Violation_type_id
    JOIN LOCATION l ON tv.Location_id = l.Location_id
    JOIN VEHICLE v ON tv.Vehicle_id = v.Vehicle_id
    WHERE tv.Driver_id = p_driver_id
      AND DATE(tv.Violation_date) BETWEEN p_start_date AND p_end_date;
END //
DELIMITER ;

-- View the total number of violations per violation type for a given year.
DELIMITER //
CREATE PROCEDURE GetViolationCountsByTypePerYear(IN p_year INT)
BEGIN
    SELECT  tvt.Name AS Violation_Type,
            COALESCE(COUNT(tv.Violation_id), 0) AS Total_Count,
            COALESCE(SUM(tv.Fine_amount), 0) AS Total_Fines_Collected
    FROM TRAFFIC_VIOLATION_TYPE tvt
    LEFT JOIN TRAFFIC_VIOLATION tv
        ON tv.Violation_type_id = tvt.Violation_type_id
       AND YEAR(tv.Violation_date) = p_year
    GROUP BY tvt.Violation_type_id, tvt.Name
    ORDER BY tvt.Violation_type_id;
END //
DELIMITER ;

-- View all vehicles involved in violations within a given city or region.
DELIMITER //
CREATE PROCEDURE GetViolatedVehiclesByLocation(
    IN p_city VARCHAR(100),
    IN p_region VARCHAR(100))
BEGIN
    SELECT  DISTINCT v.Vehicle_id, 
            v.Plate_number, 
            v.Make, 
            v.Model,
            l.City, 
            l.Region, 
            COUNT(tv.Violation_id) AS Violation_Count
    FROM VEHICLE v 
        JOIN TRAFFIC_VIOLATION tv ON v.Vehicle_id = tv.Vehicle_id
        JOIN LOCATION l ON tv.Location_id = l.Location_id
    WHERE (p_city IS NULL OR l.City = p_city) AND (p_region IS NULL OR l.Region = p_region)
    GROUP BY v.Vehicle_id;
END //
DELIMITER ;

