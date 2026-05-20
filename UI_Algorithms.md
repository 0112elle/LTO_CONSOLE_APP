# LTO Console App UI Algorithms

This document explains how each menu selection in the current console application works, based on `view/ui.py`, `controller/db_controller.py`, and the SQL endpoints in `SQL_Statements.sql`.

The console app follows a repeating pattern:

1. A menu-printing function displays choices.
2. `get_menu_choice(...)` or `get_user_input(...)` collects and validates user input.
3. A flow function decides which database call is needed.
4. The flow function calls `DBController`.
5. `DBController` forwards the request to `MariaDBInstance`.
6. `MariaDBInstance` executes a stored procedure or SQL query and returns the result.
7. The UI prints the result using `_display_record(...)`, `_present_proc_result(...)`, or a report helper.

---

## 1. Application Entry Point

### `main.py`

Execution starts in `main()`:

1. Create `MariaDBInstance`.
2. Wrap it with `DBController`.
3. Pass `DBController` to `UserInterface`.
4. Call `ui.start()`.
5. On exit, close the database connection.

---

## 2. Main Menu Routing

### `UserInterface.start()`

The main loop does this repeatedly:

1. Call `print_main_menu()`.
2. Ask the user for a main menu choice with `get_menu_choice(5)`.
3. Route the selection:
   - `[1]` Driver Management
   - `[2]` Vehicle Management
   - `[3]` Vehicle Registration Management
   - `[4]` Traffic Violation Management
   - `[5]` Generate Reports
   - `[0]` Exit

Each branch prints a submenu, validates another choice, then calls the corresponding flow method.

---

## 3. Driver Management

### Path: `[1] -> [1]` Add a Driver Record

Function chain:

`start()` -> `print_driver_menu()` -> `get_menu_choice(6)` -> `add_driver()` -> `DBController.add_driver(...)` -> `MariaDBInstance.callproc('AddDriver', ...)`

Algorithm sequence:

1. Prompt for all required driver fields.
2. Validate dates with `validate_date(...)`.
3. Validate enums with `validate_enum(...)`.
4. Validate numeric fields such as weight, height, and zip code length.
5. Build a preview dictionary.
6. Call `_display_record(preview, title='New driver preview:')`.
7. Ask for confirmation with `_confirm(...)`.
8. If confirmed, call `AddDriver` through `DBController`.
9. Show the procedure result with `_present_proc_result(...)`.

Database endpoint used:

- Stored procedure: `AddDriver(Driver_id, First_name, Middle_name, Last_name, Suffix, Date_of_birth, Weight, Height, Sex_assigned_at_birth, Nationality, Civil_status, Contact_number, Blood_type, House_number, Street_village, Barangay, City_municipality, Province, Region, Zip_code)`

---

### Path: `[1] -> [2]` Update a Driver Record

Function chain:

`start()` -> `print_driver_menu()` -> `get_menu_choice(6)` -> `update_driver_flow()` -> `DBController.find_driver(...)` -> `DBController.update_driver(...)` -> `MariaDBInstance.callproc(...)`

Algorithm sequence:

1. Ask for `Driver ID`.
2. Convert the input to `int`.
3. Search for the driver with `FindDriver`.
4. If no row is found, stop.
5. Display the current record with `_display_record(...)`.
6. Ask for confirmation with `_confirm(...)`.
7. Prompt for updated fields.
8. Keep existing values when the user enters blank or `n/a`.
9. Validate dates and enums again where needed.
10. Call `UpdateDriver`.
11. Display the result.

Database endpoints used:

- Stored procedure: `FindDriver(Driver_id)`
- Stored procedure: `UpdateDriver(Driver_id, First_name, Middle_name, Last_name, Suffix, Date_of_birth, Weight, Height, Sex_assigned_at_birth, Nationality, Civil_status, Contact_number, Blood_type, House_number, Street_village, Barangay, City_municipality, Province, Region, Zip_code)`

---

### Path: `[1] -> [3]` Delete a Driver Record

Function chain:

`start()` -> `print_driver_menu()` -> `get_menu_choice(6)` -> `delete_driver_flow()` -> `DBController.find_driver(...)` -> `DBController.delete_driver(...)`

Algorithm sequence:

1. Ask for `Driver ID`.
2. Convert to `int`.
3. Fetch the driver with `FindDriver`.
4. If the driver does not exist, stop.
5. Display the record to be deleted.
6. Ask for confirmation.
7. Call `DeleteDriver` if confirmed.
8. Display the stored procedure result.

Database endpoints used:

- Stored procedure: `FindDriver(Driver_id)`
- Stored procedure: `DeleteDriver(Driver_id)`

---

### Path: `[1] -> [4]` Search Driver Records

Function chain:

`start()` -> `print_driver_menu()` -> `get_menu_choice(6)` -> `print_driver_search_menu()` -> `get_menu_choice(3)` -> one of the search report branches

This submenu has three branches:

#### `[1] -> [4] -> [1]` Show Owned Vehicles

1. Ask for `Driver ID`.
2. Convert to `int`.
3. Call `ShowDriverVehicles`.
4. Display each row with `_display_record(...)`.

Database endpoints used:

- View: `ViewDriverVehicle`
- Stored procedure: `ShowDriverVehicles(Driver_id)`

#### `[1] -> [4] -> [2]` Show License Information

1. Ask for `Driver ID`.
2. Convert to `int`.
3. Call `ShowDriverLicense`.
4. Display the returned license row(s).

Database endpoints used:

- View: `ViewDriverLicense`
- Stored procedure: `ShowDriverLicense(Driver_id)`

#### `[1] -> [4] -> [3]` Show Traffic Violations

1. Ask for `Driver ID`.
2. Convert to `int`.
3. Call `ShowTrafficViolations`.
4. Display each violation row.

Database endpoints used:

- View: `ViewDriverTrafficViolationVehicle`
- Stored procedure: `ShowTrafficViolations(Driver_id)`

---

### Path: `[1] -> [5]` Add a License Record

Function chain:

`start()` -> `print_driver_menu()` -> `get_menu_choice(6)` -> `add_license_flow()` -> `DBController.find_driver(...)` -> `DBController.find_license_by_driver(...)` -> `DBController.add_license(...)` -> `DBController.add_license_dlcode(...)` -> `DBController.add_license_condition(...)`

Algorithm sequence:

1. Ask for `Driver ID`.
2. Convert to `int`.
3. Verify the driver exists with `FindDriver`.
4. Check if the driver already has a license using a direct license query.
5. Prompt for license number, type, status, issue date, and expiry date.
6. Validate license type and status with `validate_enum(...)`.
7. Validate issue and expiry date format with `validate_date(...)`.
8. Collect at least one DL code.
9. Collect optional conditions.
10. Show a preview of the license record.
11. Ask for confirmation.
12. Call `AddLicense`.
13. For each DL code, call `AddLicenseDLCodes`.
14. For each condition, call `AddLicenseCondition`.
15. Print the stored procedure results.

Database endpoints used:

- Stored procedure: `FindDriver(Driver_id)`
- Query: `SELECT * FROM LICENSE WHERE Driver_id = %s`
- Stored procedure: `AddLicense(License_number, License_type, License_status, License_issue_date, License_expiry_date, Driver_id)`
- Stored procedure: `AddLicenseDLCodes(License_number, Dl_codes)`
- Stored procedure: `AddLicenseCondition(License_number, Condition)`

Important validation rule:

- The expiry date must not be earlier than the issue date.

---

### Path: `[1] -> [6]` Update a License Record

Function chain:

`start()` -> `print_driver_menu()` -> `get_menu_choice(6)` -> `update_license_flow()` -> `DBController.get_license_by_number(...)` or `DBController.call_proc('ShowDriverLicense', ...)` -> `DBController.get_license_dlcodes(...)` -> `DBController.get_license_conditions(...)` -> `DBController.update_license(...)`

Algorithm sequence:

1. Accept either `Driver ID`, `License number`, or both.
2. Require at least one of them.
3. If `Driver ID` is provided, convert to `int`.
4. If only the license number is provided, use `ViewDriverLicense` filtered by license number.
5. If only the driver ID is provided, use `ShowDriverLicense`.
6. If both are provided, cross-check that they match the same record.
7. Display the current license record.
8. Ask for confirmation.
9. Prompt for new license type, new status, new issue date, and new expiry date.
10. Keep existing values if the user enters blank or `n/a`.
11. Validate any new dates and enums.
12. Display current DL codes and current conditions.
13. Allow the user to remove existing DL codes.
14. Allow the user to add new DL codes.
15. Allow the user to remove existing conditions.
16. Allow the user to add new conditions.
17. Call `UpdateLicense` for the main license row.
18. Retrieve the updated row again and display it.

Database endpoints used:

- Stored procedure: `ShowDriverLicense(Driver_id)`
- Query: `SELECT * FROM ViewDriverLicense WHERE License_number = %s`
- Stored procedure: `GetLicenseDLCodes(License_number)`
- Stored procedure: `GetLicenseConditions(License_number)`
- Stored procedure: `UpdateLicense(License_number, License_type, License_status, License_expiry_date)`
- Stored procedure: `AddLicenseDLCodes(License_number, Dl_codes)`
- Stored procedure: `RemoveLicenseDLCodes(License_number, Dl_codes)`
- Stored procedure: `AddLicenseCondition(License_number, Condition)`
- Stored procedure: `RemoveLicenseCondition(License_number, Condition)`

Important validation rule:

- The expiry date must not be earlier than the issue date.

---

## 4. Vehicle Management

### Path: `[2] -> [1]` Add Vehicle Record

Function chain:

`start()` -> `print_vehicle_menu()` -> `get_menu_choice(4)` -> `add_vehicle()` -> `DBController.add_vehicle(...)`

Algorithm sequence:

1. Prompt for vehicle fields.
2. Validate `Year` and `Owner Driver ID` as integers.
3. Build a preview dictionary.
4. Display the preview.
5. Ask for confirmation.
6. Call `AddVehicle`.
7. Display the result.

Database endpoint used:

- Stored procedure: `AddVehicle(Vehicle_id, Engine_number, Plate_number, Chassis_number, Vehicle_type, Make, Model, Year, Body_type, Capacity, Color, Driver_id)`

---

### Path: `[2] -> [2]` Update Vehicle Record

Function chain:

`start()` -> `print_vehicle_menu()` -> `get_menu_choice(4)` -> `update_vehicle_flow()` -> `DBController.call_proc('FindVehicle', ...)` -> `DBController.update_vehicle(...)`

Algorithm sequence:

1. Ask for `Vehicle ID`.
2. Convert to `int`.
3. Fetch the vehicle with `FindVehicle`.
4. If no row is found, stop.
5. Display the current record.
6. Ask for confirmation.
7. Prompt for updated vehicle fields.
8. Keep existing values when the user enters blank or `n/a`.
9. Convert numeric fields where needed.
10. Call `UpdateVehicle`.
11. Display the result.

Database endpoints used:

- Stored procedure: `FindVehicle(Vehicle_id)`
- Stored procedure: `UpdateVehicle(Vehicle_id, Engine_number, Plate_number, Chassis_number, Vehicle_type, Make, Model, Year, Body_type, Capacity, Color, Driver_id)`

---

### Path: `[2] -> [3]` Delete Vehicle Record

Function chain:

`start()` -> `print_vehicle_menu()` -> `get_menu_choice(4)` -> `delete_vehicle_flow()` -> `DBController.call_proc('FindVehicle', ...)` -> `DBController.delete_vehicle(...)`

Algorithm sequence:

1. Ask for `Vehicle ID`.
2. Convert to `int`.
3. Fetch the vehicle with `FindVehicle`.
4. If not found, stop.
5. Display the current record.
6. Ask for confirmation.
7. Call `DeleteVehicle`.
8. Display the result.

Database endpoints used:

- Stored procedure: `FindVehicle(Vehicle_id)`
- Stored procedure: `DeleteVehicle(Vehicle_id)`

---

### Path: `[2] -> [4]` Search Vehicle Records

Function chain:

`start()` -> `print_vehicle_menu()` -> `get_menu_choice(4)` -> `print_vehicle_search_menu()` -> `get_menu_choice(3)` -> search branch

#### `[2] -> [4] -> [1]` Show Vehicle Owner

1. Ask for `Vehicle ID`.
2. Convert to `int`.
3. Call `ShowVehicleOwner`.
4. Display the owner record.

Database endpoints used:

- View: `ViewDriverVehicle`
- Stored procedure: `ShowVehicleOwner(Vehicle_id)`

#### `[2] -> [4] -> [2]` Show Vehicle Registrations

1. Ask for `Vehicle ID`.
2. Convert to `int`.
3. Call `ShowVehicleRegistrations`.
4. Display each registration.

Database endpoints used:

- View: `ViewVehicleRegistration`
- Stored procedure: `ShowVehicleRegistrations(Vehicle_id)`

#### `[2] -> [4] -> [3]` Show Associated Traffic Violations

1. Ask for `Vehicle ID`.
2. Convert to `int`.
3. Call `ShowVehicleTrafficViolations`.
4. Display each violation.

Database endpoints used:

- View: `ViewDriverTrafficViolationVehicle`
- Stored procedure: `ShowVehicleTrafficViolations(Vehicle_id)`

---

## 5. Vehicle Registration Management

### Path: `[3] -> [1]` Add a Vehicle Registration Record

Function chain:

`start()` -> `print_registration_menu()` -> `get_menu_choice(4)` -> `add_vehicle_registration()` -> `DBController.add_vehicle_registration(...)`

Algorithm sequence:

1. Prompt for registration number.
2. Prompt for registration date and expiration date.
3. Validate both dates.
4. Validate registration status.
5. Prompt for OR number, OR date, document reference, ownership type, transfer reason, ownership start date, ownership end date, and vehicle ID.
6. Validate date fields and ownership enum.
7. Build the final procedure call.
8. Call `AddVehicleRegistration`.
9. Display the result.

Database endpoint used:

- Stored procedure: `AddVehicleRegistration(Registration_number, Registration_date, Expiration_date, Registration_status, Official_receipt_number, Official_receipt_date, Document_ref_no, Ownership_type, Transfer_reason, Ownership_start_date, Ownership_end_date, Vehicle_id)`

Important validation rule:

- `Expiration_date` must not be earlier than `Registration_date`.
- `Ownership_end_date` must not be earlier than `Ownership_start_date`.

---

### Path: `[3] -> [2]` Renew a Vehicle Registration

Function chain:

`start()` -> `print_registration_menu()` -> `get_menu_choice(4)` -> `renew_vehicle_registration()` -> `DBController.renew_vehicle_registration(...)`

Algorithm sequence:

1. Ask for the old registration number.
2. Ask for the new registration number.
3. Ask for registration date.
4. Ask for expiration date.
5. Validate both dates.
6. Call `RenewVehicleRegistration`.
7. Display the result.

Database endpoints used:

- Stored procedure: `FindVehicleRegistration(Registration_number)`
- Stored procedure: `RenewVehicleRegistration(Old_Registration_number, New_Registration_number, Registration_date, Expiration_date)`

Important validation rule:

- `Expiration_date` must not be earlier than `Registration_date`.

---

### Path: `[3] -> [3]` Update a Vehicle Registration Record

Function chain:

`start()` -> `print_registration_menu()` -> `get_menu_choice(4)` -> `update_vehicle_registration_flow()` -> `DBController.find_vehicle_registration(...)` -> `DBController.update_vehicle_registration(...)`

Algorithm sequence:

1. Ask for registration number.
2. Fetch the registration using `FindVehicleRegistration`.
3. Display the current record.
4. Ask for confirmation.
5. Prompt for updated registration date, expiration date, status, OR number, OR date, document reference, ownership type, transfer reason, ownership start date, ownership end date, and vehicle ID.
6. Keep existing values when the user enters blank or `n/a`.
7. Validate dates and enums.
8. Call `UpdateVehicleRegistration`.
9. Display the result.

Database endpoints used:

- Stored procedure: `FindVehicleRegistration(Registration_number)`
- Stored procedure: `UpdateVehicleRegistration(Registration_number, Registration_date, Expiration_date, Registration_status, Official_receipt_number, Official_receipt_date, Document_ref_no, Ownership_type, Transfer_reason, Ownership_start_date, Ownership_end_date, Vehicle_id)`

Important validation rule:

- `Expiration_date` must not be earlier than `Registration_date`.
- `Ownership_end_date` must not be earlier than `Ownership_start_date`.

---

### Path: `[3] -> [4]` Delete a Vehicle Registration Record

Function chain:

`start()` -> `print_registration_menu()` -> `get_menu_choice(4)` -> `delete_vehicle_registration_flow()` -> `DBController.find_vehicle_registration(...)` -> `DBController.delete_vehicle_registration(...)`

Algorithm sequence:

1. Ask for registration number.
2. Fetch the record using `FindVehicleRegistration`.
3. Display the record.
4. Ask for confirmation.
5. Call `DeleteVehicleRegistration`.
6. Display the result.

Database endpoints used:

- Stored procedure: `FindVehicleRegistration(Registration_number)`
- Stored procedure: `DeleteVehicleRegistration(Registration_number)`

---

## 6. Traffic Violation Management

### Path: `[4] -> [1]` Add a Traffic Violation Record

Function chain:

`start()` -> `print_violation_menu()` -> `get_menu_choice(3)` -> `add_violation_flow()` -> `DBController.add_traffic_violation(...)`

Algorithm sequence:

1. Prompt for violation datetime.
2. Parse it with `datetime.strptime(...)`.
3. Prompt for violation status.
4. Prompt for fine amount.
5. Prompt for payment date.
6. Prompt for driver ID, vehicle ID, violation type ID, officer ID, and location ID.
7. Convert all IDs to integers.
8. Call `AddTrafficViolation`.
9. Display the result.

Database endpoint used:

- Stored procedure: `AddTrafficViolation(Violation_date, Violation_status, Fine_amount, Payment_date, Driver_id, Vehicle_id, Violation_type_id, Officer_id, Location_id)`

Important validation rule:

- `Payment_date` must not be earlier than `Violation_date`.

---

### Path: `[4] -> [2]` Update a Traffic Violation Record

Function chain:

`start()` -> `print_violation_menu()` -> `get_menu_choice(3)` -> `update_violation_flow()` -> `DBController.call_proc('FindTrafficViolation', ...)` -> `DBController.update_traffic_violation(...)`

Algorithm sequence:

1. Ask for violation ID.
2. Convert to `int`.
3. Fetch the record with `FindTrafficViolation`.
4. Display the current violation.
5. Ask for confirmation.
6. Prompt for updated datetime, status, fine amount, payment date, driver ID, vehicle ID, violation type ID, officer ID, and location ID.
7. Keep existing values when blank or `n/a`.
8. Validate datetime, date, enum, and numeric fields.
9. Call `UpdateTrafficViolation`.
10. Display the result.

Database endpoints used:

- Stored procedure: `FindTrafficViolation(Violation_id)`
- Stored procedure: `UpdateTrafficViolation(Violation_id, Violation_date, Violation_status, Fine_amount, Payment_date, Driver_id, Vehicle_id, Violation_type_id, Officer_id, Location_id)`

Important validation rule:

- `Payment_date` must not be earlier than `Violation_date`.

---

### Path: `[4] -> [3]` Delete a Traffic Violation Record

Function chain:

`start()` -> `print_violation_menu()` -> `get_menu_choice(3)` -> `delete_violation_flow()` -> `DBController.call_proc('FindTrafficViolation', ...)` -> `DBController.delete_traffic_violation(...)`

Algorithm sequence:

1. Ask for violation ID.
2. Convert to `int`.
3. Fetch the record with `FindTrafficViolation`.
4. Display the record.
5. Ask for confirmation.
6. Call `DeleteTrafficViolation`.
7. Display the result.

Database endpoints used:

- Stored procedure: `FindTrafficViolation(Violation_id)`
- Stored procedure: `DeleteTrafficViolation(Violation_id)`

---

## 7. Generate Reports

### Path: `[5] -> [1]` View All Registered Drivers

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_driver_reports()` -> `print_registered_drivers_menu()` -> `get_menu_choice(4)`

This report group contains four filters.

#### `[5] -> [1] -> [1]` License Type

1. Print the license type submenu.
2. Ask the user to choose the license type.
3. Map the choice to the corresponding filtered view.
4. Call `show_registered_drivers_by_license_type(view_name)`.
5. Display each row.

Database views used:

- `ViewDriverLicenseStudentPermit`
- `ViewDriverLicenseProfessional`
- `ViewDriverLicenseNonProfessional`

#### `[5] -> [1] -> [2]` License Status

1. Print the license status submenu.
2. Ask the user to choose the status.
3. Map the choice to the corresponding filtered view.
4. Call `show_registered_drivers_by_status(view_name)`.
5. Display each row.

Database views used:

- `ViewDriverLicenseValid`
- `ViewDriverLicenseExpired`
- `ViewDriverLicenseSuspended`
- `ViewDriverLicenseRevoked`

#### `[5] -> [1] -> [3]` Age Range

1. Ask for minimum age.
2. Ask for maximum age.
3. Convert both inputs to integers.
4. Verify that maximum age is not lower than minimum age.
5. Call `show_driver_age_range(min_age, max_age)`.
6. Display the rows.

Database endpoint used:

- Stored procedure: `ShowDriverAgeRange(MinAge, MaxAge)`

#### `[5] -> [1] -> [4]` Sex Assigned at Birth

1. Print the sex submenu.
2. Ask the user to choose the sex.
3. Map the choice to the corresponding view name.
4. Call `show_registered_drivers_by_sex(view_name)`.
5. Display each row.

Database views used:

- `ShowMaleDrivers`
- `ShowFemaleDrivers`

---

### Path: `[5] -> [2]` View All Vehicles Owned by a Given Driver

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_vehicle_by_driver_report()` -> `DBController.show_driver_vehicles(...)`

Algorithm sequence:

1. Ask for `Driver ID`.
2. Convert to `int`.
3. Call `ShowDriverVehicles`.
4. Display each vehicle row.

Database endpoint used:

- Stored procedure: `ShowDriverVehicles(Driver_id)`

---

### Path: `[5] -> [3]` View All Vehicles with Expired Registrations as of a Given Date

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_expired_registrations_report()` -> `DBController.get_expired_registrations(...)`

Algorithm sequence:

1. Ask for the date to evaluate against.
2. Validate the date.
3. Call `GetExpiredRegistrations`.
4. Display results in table format.

Database endpoints used:

- View: `ViewExpiredVehicleRegistration`
- Stored procedure: `GetExpiredRegistrations(AsOfDate)`

---

### Path: `[5] -> [4]` View All Drivers with Expired or Suspended Licenses

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_expired_or_suspended_licenses_report()` -> `DBController.show_expired_or_suspended_licenses()`

Algorithm sequence:

1. Call the report query directly.
2. Display rows using the shared report helper.

Database view used:

- `ViewExpiredSuspendedDriverLicenses`

---

### Path: `[5] -> [5]` View All Traffic Violations Committed by a Given Driver Within Specific Dates

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_driver_violations_within_dates_report()` -> `DBController.show_driver_traffic_violations_within_dates(...)`

Algorithm sequence:

1. Ask for `Driver ID`.
2. Convert to `int`.
3. Ask for start date.
4. Ask for end date.
5. Validate both dates.
6. Call `ShowDriverTrafficViolationsWithinDates`.
7. Display the rows.

Database endpoint used:

- View: `ViewDriverTrafficViolationVehicle`
- Stored procedure: `ShowDriverTrafficViolationsWithinDates(Driver_id, DateStart, DateEnd)`

---

### Path: `[5] -> [6]` View Total Number of Violations per Violation Type for a Given Year

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_total_violations_for_year_report()` -> `DBController.view_total_violations_for_given_year(...)`

Algorithm sequence:

1. Ask for year.
2. Convert to `int`.
3. Call `ViewTotalViolationsForGivenYear`.
4. Display results in table format.

Database endpoint used:

- View: `ViewTotalViolationsForGivenYear`
- Stored procedure: `ViewTotalViolationsForGivenYear(Year)`

---

### Path: `[5] -> [7] -> [1]` View All Vehicles Involved in Violations Within a Given City

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_vehicle_violation_area_report()` -> city branch -> `DBController.show_vehicle_violation_city(...)`

Algorithm sequence:

1. Print the city/region submenu.
2. Choose `City`.
3. Ask for city name.
4. Call `ShowVehicleViolationCity`.
5. Display each row.

Database endpoint used:

- Stored procedure: `ShowVehicleViolationCity(City)`

---

### Path: `[5] -> [7] -> [2]` View All Vehicles Involved in Violations Within a Given Region

Function chain:

`start()` -> `print_reports_menu()` -> `get_menu_choice(7)` -> `_run_vehicle_violation_area_report()` -> region branch -> `DBController.show_vehicle_violation_region(...)`

Algorithm sequence:

1. Print the city/region submenu.
2. Choose `Region`.
3. Ask for region name.
4. Call `ShowVehicleViolationRegion`.
5. Display each row.

Database endpoint used:

- Stored procedure: `ShowVehicleViolationRegion(Region)`

---

## 8. Notes on the Design

The current code is already close to the structure you described:

- Menu printing is separated from action execution.
- Input collection is centralized in `get_user_input(...)` and `get_menu_choice(...)`.
- Database access is isolated in `DBController`.
- `DBController` hides the raw connector and gives the UI clear action methods.

That makes the app easier to organize around the menu hierarchy and easier to keep aligned with the SQL backend.

The main thing you still need to keep consistent is the contract between the UI and the SQL file:

- Every UI endpoint should map to a specific stored procedure or view.
- Any validation that prevents bad inputs should happen before the DB call.
- If a submenu is only a filter, it should resolve to a single view or procedure.

## 9. Recommended Next Step

If you want the database layer to match this document cleanly, the next improvement would be to make the stored procedures and views in `SQL_Statements.sql` follow the same hierarchy naming and return shape used by the UI.
