from typing import Any, List
from sql.sql_connector import MariaDBInstance

class DBController:
    
    # This funciton initializes the DBController with a MariaDBInstance, which is used to execute stored procedures and queries against the database. 
    # Provides a set of convenience wrapper methods for common actions related to drivers, vehicles, registrations, violations, and licenses, 
    # which internally call the appropriate stored procedures or execute queries. 
    # This has a close method to cleanly close the database connection when done. 
    # This class serves as an abstraction layer between the UI and the database, allowing the UI to interact with the database through high-level methods 
    # without needing to know the details of the database interactions.
    def __init__(self, db: MariaDBInstance):
        self.db = db

    # Generic wrapper for calling stored procedures with the given name and parameters. 
    # It uses the MariaDBInstance's callproc method to execute the procedure and returns the result.
    def call_proc(self, name: str, params: List[Any] = None):
        return self.db.callproc(name, params)

    # Generic wrapper for executing SQL queries with optional parameters. 
    # Uses the MariaDBInstance's query method to execute the query and returns the result.
    def query(self, sql: str, params: List[Any] = None):
        return self.db.query(sql, params)


    # CONVENIENCE WRAPPERS FOR COMMON ACTIONS =================================================================================================================

    # For calling the ShowDriverVehicles stored procedure, which retrieves all vehicles associated with a given driver ID.
    def show_driver_vehicles(self, driver_id: int):
        return self.call_proc('ShowDriverVehicles', [driver_id])

    # For calling the GetVehiclesByDriver stored procedure, which retrieves all vehicles associated with a given driver ID.
    def get_vehicles_by_driver(self, driver_id: int):
        return self.call_proc('GetVehiclesByDriver', [driver_id])

    # For executing a query to retrieve registered drivers based on their license type.
    def show_registered_drivers_by_license_type(self, view_name: str):
        return self.query(f'SELECT * FROM {view_name}')

    # For executing a query to retrieve registered drivers based on their status.
    def show_registered_drivers_by_status(self, view_name: str):
        return self.query(f'SELECT * FROM {view_name}')

    # For executing a query to retrieve registered drivers based on their sex.
    def show_registered_drivers_by_sex(self, view_name: str):
        return self.query(f'SELECT * FROM {view_name}')

    # For executing a query to retrieve expired or suspended licenses.
    def show_expired_or_suspended_licenses(self):
        return self.query('SELECT * FROM ViewExpiredSuspendedDriverLicenses')

    # For executing a query to retrieve vehicle registration given a Vehicle_id.
    def show_vehicle_registrations(self, vehicle_id: int):
        return self.call_proc('ShowVehicleRegistrations', [vehicle_id])

    # For executing a query to retrieve expired vehicle registrations.
    def show_expired_vehicle_registration(self):
        return self.query('SELECT * FROM ViewExpiredVehicleRegistration')

    # For executing a query to retrieve expired vehicle registrations as of a given date.
    def get_expired_registrations(self, as_of_date: str):
        return self.call_proc('GetExpiredRegistrations', [as_of_date])

    # For calling the AddVehicleRegistration stored procedure.
    # Adds a new vehicle registration with the given parameters and returns the new registration number.
    def add_vehicle_registration(self, reg_number: str, reg_date: str, exp_date: str, status: str, or_number: str, or_date: str, doc_ref: str, ownership: str, transfer_reason: str, start_date: str, end_date: str, vehicle_id: int):
        return self.call_proc('AddVehicleRegistration', [reg_number, reg_date, exp_date, status, or_number, or_date, doc_ref, ownership, transfer_reason, start_date, end_date, vehicle_id])

    # For calling the RenewVehicleRegistration stored procedure.
    # Renews an existing vehicle registration with a new registration number and updated dates.
    def renew_vehicle_registration(self, old_reg: str, new_reg: str, reg_date: str, exp_date: str):
        return self.call_proc('RenewVehicleRegistration', [old_reg, new_reg, reg_date, exp_date])

    # This method cleanly closes the database connection when the controller is no longer needed.
    def close(self):
        self.db.close()


    # FOR DRIVER PROCEDURES ===================================================================================================================================

    # Calls the AddDriver stored procedure.
    # Which adds a new driver to the database with the given parameters and returns the new driver ID.
    def add_driver(self, *params):
        return self.call_proc('AddDriver', list(params))

    # Calls the UpdateDriver stored procedure.
    # This updates an existing driver record in the database based on the given parameters.
    def update_driver(self, *params):
        return self.call_proc('UpdateDriver', list(params))

    # Calls the DeleteDriver stored procedure.
    # Deletes a driver record from the database based on the given driver ID.
    def delete_driver(self, driver_id: int):
        return self.call_proc('DeleteDriver', [driver_id])

    # Calls the SearchDriver stored procedure.
    # For searching drivers in the database based on the given search criteria (first name,
    def search_driver(self, first_name: str = None, last_name: str = None, license_number: str = None, contact: str = None):
        return self.call_proc('SearchDriver', [first_name, last_name, license_number, contact])

    # For calling the FindDriver stored procedure.
    # This finds a specific driver in the database based on the given driver ID.
    def find_driver(self, driver_id: int):
        return self.call_proc('FindDriver', [driver_id])

    # For calling the FindVehicle stored procedure.
    # This finds a specific vehicle in the database based on the given vehicle ID.
    def find_vehicle(self, vehicle_id: int):
        return self.call_proc('FindVehicle', [vehicle_id])


    # FOR VEHICLE PROCEDURES ==================================================================================================================================

    # Calls the AddVehicle stored procedure.
    # Adds a new vehicle to the database with the given parameters and returns the new vehicle
    def add_vehicle(self, *params):
        return self.call_proc('AddVehicle', list(params))

    # Calls the UpdateVehicle stored procedure.
    # Updates an existing vehicle record in the database based on the given parameters.
    def update_vehicle(self, *params):
        return self.call_proc('UpdateVehicle', list(params))

    # Calls the DeleteVehicle stored procedure.
    # Deletes a vehicle record from the database based on the given vehicle ID.
    def delete_vehicle(self, vehicle_id: int):
        return self.call_proc('DeleteVehicle', [vehicle_id])

    # Calls the SearchVehicle stored procedure.
    # Searches for vehicles in the database based on the given search criteria.
    def search_vehicle(self, plate: str = None, owner_lastname: str = None, vehicle_type: str = None):
        return self.call_proc('SearchVehicle', [plate, owner_lastname, vehicle_type])


    # FOR VEHICLE REGISTRATION HELPERS ========================================================================================================================

    # Calls the FindVehicleRegistration stored procedure.
    # Finds the registration details of a vehicle based on the given registration number.
    def find_vehicle_registration(self, reg_number: str):
        return self.call_proc('FindVehicleRegistration', [reg_number])

    # Calls the UpdateVehicleRegistration stored procedure.
    # Updates the registration details of a vehicle based on the given parameters.
    def update_vehicle_registration(self, reg_number: str, registration_date: str = None, expiration_date: str = None, status: str = None, or_number: str = None, or_date: str = None, doc_ref: str = None, ownership: str = None, transfer_reason: str = None, start_date: str = None, end_date: str = None, vehicle_id: int = None):
        # Use the UI-facing UpdateVehicleRegistration signature
        return self.call_proc('UpdateVehicleRegistration', [reg_number, registration_date, expiration_date, status, or_number, or_date, doc_ref, ownership, transfer_reason, start_date, end_date, vehicle_id])

    # Calls the DeleteVehicleRegistration stored procedure.
    # Deletes a vehicle registration record from the database based on the given registration number.
    def delete_vehicle_registration(self, reg_number: str):
        return self.call_proc('DeleteVehicleRegistration', [reg_number])

    # Calls the SearchRegistration stored procedure.
    # Searches for vehicle registrations in the database based on the given search criteria (plate number, status, expiration date).
    def search_registration(self, plate: str = None, status: str = None, expired_before: str = None):
        return self.call_proc('SearchRegistration', [plate, status, expired_before])


    # FOR VIOLATION PROCEDURES ================================================================================================================================
    
    # Calls the AddViolation stored procedure.
    # Adds a new traffic violation record to the database with the given parameters and returns the new violation ID.
    def add_traffic_violation(self, *params):
        return self.call_proc('AddTrafficViolation', list(params))

    # Calls the GetViolationById stored procedure.
    # Retrieves the details of a specific traffic violation based on the given violation ID.
    def update_traffic_violation(self, *params):
        return self.call_proc('UpdateTrafficViolation', list(params))

    # Looks up a traffic violation type by ID.
    def find_violation_type(self, violation_type_id: int):
        return self.query('SELECT * FROM TRAFFIC_VIOLATION_TYPE WHERE Violation_type_id = %s', [violation_type_id])

    # Looks up an officer by ID.
    def find_officer(self, officer_id: int):
        return self.query('SELECT * FROM OFFICER WHERE Officer_id = %s', [officer_id])

    # Looks up a location by ID.
    def find_location(self, location_id: int):
        return self.query('SELECT * FROM LOCATION WHERE Location_id = %s', [location_id])

    # Calls the DeleteViolation stored procedure.
    # Deletes a traffic violation record from the database based on the given violation ID.
    def delete_traffic_violation(self, violation_id: int):
        return self.call_proc('DeleteTrafficViolation', [violation_id])

    # Calls the SearchViolation stored procedure.
    # Searches for traffic violations in the database based on the given search criteria (plate number, driver ID, date range, status).
    def search_violation(self, driver_lastname: str = None, plate: str = None, start_date: str = None, end_date: str = None, status: str = None):
        return self.call_proc('SearchViolation', [driver_lastname, plate, start_date, end_date, status])


    # FOR GENERATING REPORTS ==================================================================================================================================

    # Calls the ShowDriverAgeRange stored procedure.
    # Generates a report of drivers within a specified age range.
    def show_driver_age_range(self, min_age: int, max_age: int):
        return self.call_proc('ShowDriverAgeRange', [min_age, max_age])

    # Calls the ShowDriverTrafficViolationsWithinDates stored procedure.
    # Generates a report of traffic violations for a specific driver within a given date range.
    def show_driver_traffic_violations_within_dates(self, driver_id: int, start_date: str, end_date: str):
        return self.call_proc('ShowDriverTrafficViolationsWithinDates', [driver_id, start_date, end_date])

    # Calls the ViewTotalViolationsForGivenYear stored procedure.
    # Generates a report of the total number of traffic violations that occurred in a given year.
    def view_total_violations_for_given_year(self, year: int):
        return self.call_proc('ViewTotalViolationsForGivenYear', [year])

    # Calls the ShowVehicleViolationCity stored procedure.
    # Generates a report of vehicles involved in traffic violations within a specified city.
    def show_vehicle_violation_city(self, city: str):
        return self.call_proc('ShowVehicleViolationCity', [city])

    # Calls the ShowVehicleViolationRegion stored procedure.
    # Generates a report of vehicles involved in traffic violations within a specified region.
    def show_vehicle_violation_region(self, region: str):
        return self.call_proc('ShowVehicleViolationRegion', [region])


    # FOR LICENSE PROCEDURES ==================================================================================================================================

    # Calls the AddLicense stored procedure.
    # Adds a new driver's license record to the database with the given parameters and returns the new
    def add_license(self, license_number: str, license_type: str, license_status: str, issue_date: str, expiry_date: str, driver_id: int):
        return self.call_proc('AddLicense', [license_number, license_type, license_status, issue_date, expiry_date, driver_id])

    # Calls the UpdateLicense stored procedure.
    # Updates an existing driver's license record in the database based on the given parameters.
    def add_license_dlcode(self, license_number: str, dl_code: str):
        return self.call_proc('AddLicenseDLCodes', [license_number, dl_code])

    # Calls the AddLicenseCondition stored procedure.
    # Adds a new condition to an existing driver's license record in the database based on the given
    def add_license_condition(self, license_number: str, condition: str):
        return self.call_proc('AddLicenseCondition', [license_number, condition])

    # This is for executing a query to find the license record(s) associated with a given driver ID.
    def find_license_by_driver(self, driver_id: int):
        return self.query('SELECT * FROM LICENSE WHERE Driver_id = %s', [driver_id])

    # Calls the UpdateLicense stored procedure.
    # Updates an existing driver's license record in the database based on the given parameters.
    def update_license(self, license_number: str, new_type: str = None, new_status: str = None, new_expiry: str = None):
        return self.call_proc('UpdateLicense', [license_number, new_type, new_status, new_expiry])

    # Executes a query to retrieve the license details associated with a given license number.
    def get_license_by_number(self, license_number: str):
        return self.query('SELECT * FROM ViewDriverLicense WHERE License_number = %s', [license_number])

    # Executes a query to retrieve the license DL codes associated with a given license number.
    def get_license_dlcodes(self, license_number: str):
        return self.call_proc('GetLicenseDLCodes', [license_number])

    # Executes a query to retrieve the license conditions associated with a given license number.
    def get_license_conditions(self, license_number: str):
        return self.call_proc('GetLicenseConditions', [license_number])

    # Calls the RemoveLicenseDLCodes stored procedure.
    # Removes a specific DL code from an existing driver's license record in the database based on the given license number and DL code.
    def remove_license_dlcode(self, license_number: str, dl_code: str):
        return self.call_proc('RemoveLicenseDLCodes', [license_number, dl_code])

    # Calls the RemoveLicenseCondition stored procedure.
    # Removes a specific condition from an existing driver's license record in the database based on the given license number and condition.
    def remove_license_condition(self, license_number: str, condition: str):
        return self.call_proc('RemoveLicenseCondition', [license_number, condition])
