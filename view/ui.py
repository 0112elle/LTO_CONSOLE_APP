from typing import Optional
from datetime import datetime
import shutil
import textwrap
import re
from controller.db_controller import DBController
from typing import Any, Dict, List


def validate_date(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        return None


def validate_dates(start_date: Any, end_date: Any) -> Optional[tuple[str, str]]:
    """Validate two dates and ensure the second is not earlier than the first."""
    def normalize_date(value: Any) -> Optional[str]:
        if value is None:
            return None
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        text = str(value)
        return text[:10] if len(text) > 10 else text

    start_text = normalize_date(start_date)
    end_text = normalize_date(end_date)
    start_valid = validate_date(start_text)
    end_valid = validate_date(end_text)
    if start_valid is None or end_valid is None:
        return None
    if datetime.strptime(end_valid, '%Y-%m-%d') < datetime.strptime(start_valid, '%Y-%m-%d'):
        return None
    return start_valid, end_valid


def validate_enum(value: Optional[str], allowed: list) -> Optional[str]:
    if value is None:
        return None
    if value in allowed:
        return value
    return None


class UserInterface:
    def __init__(self, db_ctrl: DBController):
        self.db = db_ctrl

    # Funciton that prints the main menu.
    def print_main_menu(self):
        print("="*100)
        print('''
    WELCOME TO THE LTO SYSTEM

    [1] Driver Management
    [2] Vehicle Management
    [3] Vehicle Registration Management
    [4] Traffic Violation Management
    [5] Generate Reports
    [0] Exit
''')

    # Function that prints the driver management menu.
    def print_driver_menu(self):
        print("_"*100)
        print('''
    DRIVER MANAGEMENT

    [1] Add a Driver Record
    [2] Update a Driver Record
    [3] Delete a Driver Record
    [4] Search Driver Records
    [5] Add a License Record
    [6] Update a License Record
    [0] Return
''')

    # Function that prints the sub-menu for searching driver records.
    def print_driver_search_menu(self):
        print("_"*100)
        print('''
    SEARCH DRIVER RECORDS
    
    [1] Show Owned Vehicles
    [2] Show License Information
    [3] Show Traffic Violations
    [0] Return
''')

    # Function that prints the vehicle management menu.
    def print_vehicle_menu(self):
        print("_"*100)
        print('''
    VEHICLE MANAGEMENT

    [1] Add Vehicle Record
    [2] Update Vehicle Record
    [3] Delete Vehicle Record
    [4] Search Vehicle Records
    [0] Return
''')

    # Function that prints the sub-menu for searching vehicle records.
    def print_vehicle_search_menu(self):
        print("_"*100)
        print('''
    SEARCH VEHICLE RECORDS
    
    [1] Show Vehicle Owner
    [2] Show Vehicle Registrations
    [3] Show Associated Traffic Violations
    [0] Return
''')

    # Function that prints the vehicle registration management menu.
    def print_registration_menu(self):
        print("_"*100)
        print('''
    VEHICLE REGISTRATION MANAGEMENT

    [1] Add a Vehicle Registration Record
    [2] Renew a Vehicle Registration
    [3] Update a Vehicle Registration Record
    [4] Delete a Vehicle Registration Record
    [0] Return
''')

    # Function that prints the traffic violation management menu.
    def print_violation_menu(self):
        print("_"*100)
        print('''
    TRAFFIC VIOLATION MANAGEMENT

    [1] Add a Traffic Violation Record
    [2] Update a Traffic Violation Record
    [3] Delete a Traffic Violation Record
    [0] Return
''')

    # Function that prints the generate reports menu.
    def print_reports_menu(self):
        print("_"*100)
        print('''
    GENERATE REPORTS
    
    [1] View All Registered Drivers
    [2] View All Vehicles Owned by a Given Driver
    [3] View All Vehicles with Expired Registrations as of a Given Date
    [4] View All Drivers with Expired or Suspended Licenses
    [5] View All Traffic Violations Committed by a Given Driver Within Specific Dates
    [6] View Total Number of Violations per Violation Type for a Given Year
    [7] View All Vehicle Involved in Violations Within a Given City or Region
    [0] Return
''')

    # Function that prints the sub-menu for viewing all registered drivers with filters.
    def print_registered_drivers_menu(self):
        print("_"*100)
        print('''
    GENERATE REPORTS: VIEW ALL REGISTERED DRIVERS
    
    FILTERS:
    [1] License Type
    [2] License Status
    [3] Age Range
    [4] Sex Assigned at Birth
    [0] Return
''')

    # Function that prints the sub-menu for viewing all registered drivers by license type.
    def print_license_type_menu(self):
        print("_"*100)
        print('''
    GENERATE REPORTS: VIEW ALL REGISTERED DRIVERS (FILTER BY LICENSE TYPE)
    
    LICENSE TYPES:
    [1] Student Permit
    [2] Professional
    [3] Non-Professional
    [0] Return
''')

    # Funciton that prints the sub-menu for viewing all registered drivers by license status.
    def print_license_status_menu(self):
        print("_"*100)
        print('''
    GENERATE REPORTS: VIEW ALL REGISTERED DRIVERS (FILTER BY LICENSE STATUS)
    
    LICENSE STATUS:
    [1] Valid
    [2] Expired
    [3] Suspended
    [4] Revoked
    [0] Return
''')

    # Function that prints the sub-menu for viewing all registered drivers by sex assigned at birth.
    def print_sex_menu(self):
        print("_"*100)
        print('''
    GENERATE REPORTS: VIEW ALL REGISTERED DRIVERS (FILTER BY SEX ASSIGNED AT BIRTH)
              
    SEX ASSIGNED AT BIRTH:
    [1] Male
    [2] Female
    [0] Return
''')

    # Function that prints the sub-menu for viewing all vehicles involved in violations within a given city or region.
    def print_vehicle_violation_area_menu(self):
        print("_"*100)
        print('''
    GENERATE REPORTS: VIEW ALL VEHICLE INVOLVED IN VIOLATIONS WITHIN A GIVEN CITY OR REGION
              
    AREA FILTERS:
    [1] City
    [2] Region
    [0] Return
''')

    # This function gets the user input with a standardized prompt and validation for required fields. It also allows the user to cancel the input by typing '/cancel' and handles 'n/a' as None.
    def get_user_input(self, prompt: str, required: bool = True) -> Optional[str]:
        while True:
            val = input(prompt + " ")
            if val == '/cancel':
                return None
            if val == '' and required:
                print('    Input required! Type \'n/a\' or leave blank only if null is allowed.')
                continue
            if val == 'n/a':
                return None
            return val

    # This function is for standardized menu choice input, validating that the input is an integer within the specified range. It also allows cancellation with '/cancel'.
    def get_menu_choice(self, max_choice: int, prompt_prefix: str = "Please enter your choice") -> Optional[int]:
        """Prompt the user with standardized menu input and validate 0..max_choice. Input is inline after prompt."""
        while True:
            raw = input("    "+f"Please enter your choice (0-{max_choice}): ")
            if raw == '/cancel':
                return None
            raw = raw.strip()
            if raw == '':
                print('    Input required.')
                continue
            try:
                val = int(raw)
            except ValueError:
                print('    Please enter a whole number.')
                continue
            if val < 0 or val > max_choice:
                print(f'    Please enter a number between 0 and {max_choice}.')
                continue
            return val

    # Formats a date value into a more human-readable form. 
    # This accepts various input formats and attempts to parse them into a standardized date format for display.
    def _fmt_date(self, val: Any) -> Optional[str]:
        if val is None:
            return None
        if isinstance(val, str):
            try:
                d = datetime.strptime(val, "%Y-%m-%d")
            except Exception:
                try:
                    d = datetime.fromisoformat(val)
                except Exception:
                    return val
        else:
            d = val
        try:
            return d.strftime("%b. %d, %Y")
        except Exception:
            return str(val)

    # Formats a numeric value as currency, ensuring it has two decimal places. 
    # If the value cannot be converted to a float, it returns the original value as a string.
    def _fmt_currency(self, val: Any) -> Optional[str]:
        if val is None:
            return None
        try:
            return f"{float(val):.2f}"
        except Exception:
            return str(val)

    # Formats an enum-like value by capitalizing it. 
    # If value is None, it returns None. 
    # If the value cannot be converted to a string, it returns the original value as a string.
    def _fmt_enum(self, val: Any) -> Optional[str]:
        if val is None:
            return None
        try:
            s = str(val)
            return s.capitalize()
        except Exception:
            return str(val)

    # Validates a value against a simple spec where '#' => digit and 'X' => uppercase letter.
    def validate_pattern(self, value: Optional[str], spec: str) -> bool:
        if value is None:
            return False
        # Build regex from spec: '#' -> \d, 'X' -> [A-Z], other chars are escaped
        parts = []
        for ch in spec:
            if ch == '#':
                parts.append(r"\d")
            elif ch == 'X':
                parts.append(r"[A-Z]")
            else:
                parts.append(re.escape(ch))
        pattern = '^' + ''.join(parts) + '$'
        try:
            return re.match(pattern, value) is not None
        except re.error:
            return False

    # This function displays a record (dictionary of key-value pairs) in a formatted manner. 
    # This also aligns labels and wraps values for better readability, 
    # and also applies specific formatting rules based on the key names (e.g., dates, currency, enums). 
    # Includes an optional title for the record display.
    def _display_record(self, rec: Dict[str, Any], title: str = None):
        sep = '-' * 50
        print("\n" + sep)
        if title:
            print(title)
        # Left-right layout: aligned labels with wrapped values for readability.
        label_width = min(max((len(str(k)) for k in rec.keys()), default=0), 28)
        term_width = shutil.get_terminal_size(fallback=(100, 30)).columns
        value_width = max(20, term_width - label_width - 5)
        for k, v in rec.items():
            out = v
            # Basic formatting rules by column name
            key = k.lower()
            if 'date' in key or 'birth' in key:
                # This applies date formatting to any field that has 'date' or 'birth' in its name, making it more human-readable.
                out = self._fmt_date(v)
            elif 'fine' in key or 'amount' in key:
                # This applies currency formatting to any field that has 'fine' or 'amount' in its name, 
                # ensuring it is displayed with two decimal places.
                out = self._fmt_currency(v)
            elif key in ('registration_status', 'license_status', 'license_type', 'ownership_type', 'vehicle_type', 'sex_assigned_at_birth', 'civil_status') or key.endswith('_type'):
                # This applies enum formatting to any field that matches the specified keys or ends with '_type', 
                # capitalizing the value for better readability.
                out = self._fmt_enum(v)
            # Wrap long values and print with aligned labels. 
            # This ensures that even if the value is too long for the terminal width, it will be wrapped neatly under the label.
            value_str = '' if out is None else str(out)
            # Wrap the value string to fit within the calculated value width, 
            # ensuring that long values are displayed in a readable format without overflowing the terminal width.
            wrapped = textwrap.wrap(value_str, width=value_width) or ['']
            # Print the first line with the label, and subsequent lines with indentation for continuation.
            print(f"    {k:<{label_width}} : {wrapped[0]}")
            # Continuation lines for wrapped values are indented to align with the value column, 
            # providing a clean and organized display of the record's information even when values are lengthy.
            continuation_pad = ' ' * (label_width + 3)
            # If the value was wrapped into multiple lines, print the continuation lines with appropriate indentation.
            for line in wrapped[1:]:
                print(f"{continuation_pad}{line}")

    # Prompts the user for confirmation with a yes/no question.
    # Requires an explicit 'Y' or 'N' response (no defaults allowed).
    def _confirm(self, prompt: str) -> bool:
        # Require explicit Y or N, no defaults
        while True:
            ans = self.get_user_input(f"{prompt} (Y/N):", True)
            if ans is None:
                return False
            a = ans.strip().lower()
            if a == 'y':
                return True
            if a == 'n':
                return False
            print("    Please answer 'Y' or 'N'.")
        return False

    # Processes the result of a stored procedure call and presents it to the user in a friendly manner.
    # This function checks for common keys in the result to determine how to display success messages or affected rows, 
    # and falls back to printing the raw result if no specific formatting is applicable.
    def _present_proc_result(self, res: Any, action: str = None):
        if res is None:
            print('Operation failed (no result).')
            return
        # To check if result is a list of dicts with common keys for new IDs or messages
        if isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict):
            first = res[0]
            # Common keys
            if 'NewDriverID' in first:
                print(f'    Added successfully. New Driver ID: {first["NewDriverID"]}')
                return
            if 'NewVehicleID' in first:
                print(f'    Added successfully. New Vehicle ID: {first["NewVehicleID"]}')
                return
            if 'NewViolationID' in first:
                print(f'    Added successfully. New Violation ID: {first["NewViolationID"]}')
                return
            if 'NewRegistrationNumber' in first:
                print(f'    Registration created: {first["NewRegistrationNumber"]}')
                return
            if 'Message' in first:
                print(f'    {first["Message"]}')
                return
            if 'RowsAffected' in first:
                try:
                    n = int(first['RowsAffected'])
                except Exception:
                    n = None
                if n is None:
                    print(first)
                    return
                # Infer entity from action for friendlier messages
                ent = 'record'
                if action:
                    la = action.lower()
                    if 'vehicle' in la:
                        ent = 'vehicle'
                    elif 'driver' in la:
                        ent = 'driver'
                    elif 'registration' in la or 'reg' in la:
                        ent = 'registration'
                    elif 'violation' in la:
                        ent = 'violation'
                # Determine success based on rows affected and print appropriate message.
                if n > 0:
                    if action and 'delete' in action.lower():
                        print(f'    {ent.capitalize()} deleted!')
                    elif action and 'update' in action.lower():
                        print(f'    {ent.capitalize()} updated!')
                    elif action and 'add' in action.lower():
                        print(f'    {ent.capitalize()} added successfully!')
                    else:
                        print(f'    Rows affected: {n}')
                else:
                    if action and 'delete' in action.lower():
                        print(f'    {ent.capitalize()} not found or deletion failed.')
                    elif action and 'update' in action.lower():
                        print(f'    {ent.capitalize()} not found or update failed.')
                    else:
                        print('    No rows affected.')
                return
            # Fallback: If first dict contains a single textual value, print it
            if len(first) == 1:
                v = list(first.values())[0]
                print(f'    {v}')
                return
        # Otherwise just print raw result
        print(res)
        
    # Attempts to infer the primary key field from a record dictionary by looking for common ID field names or patterns.
    # This is important for sorting and displaying records in a user-friendly manner, especially when the exact schema may not be known in advance.
    def _infer_pk_key(self, rec: Dict[str, Any]) -> Optional[str]:
        # Try common pk names
        keys = list(rec.keys())
        # Check for common ID field names first, then fallback to any field that ends with '_id' or is 'id', 
        # and finally just take the first key if no better option is found.
        for candidate in ('Driver_id', 'driver_id', 'Vehicle_id', 'vehicle_id', 'Registration_number', 'registration_number', 'Violation_id', 'violation_id', 'id'):
            if candidate in rec:
                return candidate
        # Fallback to first key that endswith _id or 'id'
        for k in keys:
            if k.lower().endswith('_id') or k.lower() == 'id':
                return k
        return keys[0] if keys else None

    # Sorts a list of record dictionaries by their inferred primary key in ascending order, handling missing or non-integer keys gracefully.
    def _sort_rows_by_pk(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not rows:
            return rows
        pk = self._infer_pk_key(rows[0])
        if pk is None:
            return rows
        try:
            # Sort by primary key, treating missing or non-integer keys as greater than any integer value 
            # to ensure they appear at the end of the sorted list.
            return sorted(rows, key=lambda r: (r.get(pk) is None, r.get(pk)))
        except Exception:
            return rows

    # For the Vehicle CRUD implementations (adding, searching, updating, and deleting vehicle records in the system).
    
    # This function prompts the user for details about a new vehicle, displays a preview of the entered information, 
    # and then calls the database controller to add the vehicle record if the user confirms.
    def add_vehicle(self):
        engine      = self.get_user_input('    Engine number (Format: ENG####X):', True)
        if not self.validate_pattern(engine, 'ENG####X'):
            print('    Engine number must match format ENG####X!')
            return
        plate       = self.get_user_input('    Plate number (Format: XXX####):', True)
        if not self.validate_pattern(plate, 'XXX####'):
            print('    Plate number must match format XXX####')
            return
        chassis     = self.get_user_input('    Chassis number (Format: CHS####XXX):', True)
        if not self.validate_pattern(chassis, 'CHS####XXX'):
            print('    Chassis number must match format CHS####XXX')
            return
        vtype       = self.get_user_input("    Vehicle type ('motorcycle'|'private car'|'public utility vehicle'|'truck'|'others'):", True)
        make        = self.get_user_input('    Make:', True)
        model       = self.get_user_input('    Model:', True)
        year        = self.get_user_input('    Year (Format: YYYY):', True)
        try:
            year_i  = int(year)
        except Exception:
            print('Invalid year')
            return
        body        = self.get_user_input('    Body type (E.g.: sedan, SUV. etc.):', True)
        capacity    = self.get_user_input('    Capacity (Integer):', True)
        try:
            cap_i = int(capacity)
            if cap_i <= 0:
                raise ValueError
        except Exception:
            print('    Capacity must be a positive integer.')
            return
        color       = self.get_user_input('    Color:', True)
        owner_id    = self.get_user_input('    Owner Driver ID:', True)
        try:
            # Validate that the owner ID is an integer, which is necessary for linking the vehicle to a driver record in the database. 
            # If the input is invalid, it informs the user and exits the add vehicle flow.
            owner = int(owner_id)
        except Exception:
            print('    Owner must be integer Driver ID.')
            return
        # Preview of the entered data before confirming the addition of the vehicle record to the database. 
        # This allows the user to review the information and cancel if there are any errors or if they change their mind.
        preview = {
            'Engine_number': engine, 
            'Plate_number': plate, 
            'Chassis_number': chassis, 
            'Vehicle_type': vtype, 
            'Make': make, 
            'Model': model, 
            'Year': year_i, 
            'Color': color, 
            'Owner_id': owner}
        self._display_record(preview, title='    New vehicle preview:')
        if not self._confirm('    Proceed to add this vehicle?'):
            print('    Aborted')
            return
        # Calls the database controller to add the new vehicle record with the provided details,
        res = self.db.add_vehicle(
            engine,         # Engine_number  (E.g.: ENG####A)
            plate,          # Plate_number   (E.g.: ABC####)
            chassis,        # Chassis_number (E.g.: CHS####XYZ)
            vtype,          # Vehicle_type   (E.g.: 'motorcycle', 'private car', 'public utility vehicle', 'truck', 'others')
            make,           # Make           (E.g.: 'Toyota',  'Honda', 'Ford',  'Mitsubishi', 'Nissan', 'Isuzu',  'Hyundai', 'Kia',      'Subaru',   'Mazda', etc.)
            model,          # Model          (E.g.: 'Corolla', 'Civic', 'F-150', 'L300',       'Accord', 'Triton', 'Elantra', 'Sportage', 'Forester', 'CX-5', etc.)
            year_i,         # Year           (E.g.: 1995, 2020, etc.)
            body or None,   # Body_type      (E.g.: 'sedan', 'hatchback', 'SUV', 'pickup', 'van', etc.)
            cap_i,          # Capacity       (Positive integer, number of passengers for cars or cargo capacity for trucks in kg)
            color,          # Color          (E.g.: 'white', 'black', 'red', 'blue', 'gray', 'silver', 'green', 'yellow', etc.)
            owner)          # Driver_id      (Driver ID of the vehicle owner, must correspond to an existing driver record)
        # Presents the result of the add operation to the user, 
        # indicating whether the addition was successful or if any errors occurred.
        self._present_proc_result(res, 'add vehicle')

    # Prompts the user for search criteria (plate, owner last name, vehicle type) to find matching vehicle records in the database.
    # The search results are then displayed in a formatted manner, allowing the user to review the details of each matching vehicle. 
    # If no matches are found, an appropriate message is shown.
    def search_vehicle_flow(self):
        plate       = self.get_user_input('    Plate (n/a if none):', False)
        owner_ln    = self.get_user_input('    Owner last name (n/a if none):', False)
        vtype       = self.get_user_input('    Vehicle type (n/a if none):', False)
        rows        = self.db.search_vehicle(plate, owner_ln, vtype)
        if not rows:
            print('    No matching vehicles')
            return
        rows = self._sort_rows_by_pk(rows)
        for r in rows:
            self._display_record(r, title=f"    Vehicle {r.get(self._infer_pk_key(r))}")

    # Allows the user to update an existing vehicle record by first searching for the vehicle using its ID, 
    # displaying the current details, and then prompting for new values for each field.
    def update_vehicle_flow(self):
        vid_raw = self.get_user_input('    Enter Vehicle ID to update:', True)
        if vid_raw is None:     # User cancelled input
            return
        try:
            vid = int(vid_raw)
        except Exception:       # Invalid integer input for Vehicle ID
            print('    Invalid Vehicle ID.')
            return
        try:
            # Attempt to find the vehicle record in the database using the provided Vehicle ID. 
            # If not found, handle the exception and set found to None.
            found = self.db.call_proc('FindVehicle', [vid])
        except Exception:
            found = None
        # If the vehicle record is not found, inform the user and exit the update flow.
        if not found:
            print('    Vehicle not found')
            return
        rec = found[0]
        self._display_record(rec, title='    Current record:')
        if not self._confirm('    Proceed to update this vehicle?'):
            print('    Aborted')
            return
        # Prompt fields in the same order as UpdateVehicle stored-proc
        engine      = self.get_user_input('    Engine number (Enter to keep):', False)
        if engine and not self.validate_pattern(engine, 'ENG####X'):
            print('    Engine number must match format ENG####X')
            return
        plate       = self.get_user_input('    Plate number (Enter to keep):', False)
        if plate and not self.validate_pattern(plate, 'XXX####'):
            print('    Plate number must match format XXX####')
            return
        chassis     = self.get_user_input('    Chassis number (Enter to keep):', False)
        if chassis and not self.validate_pattern(chassis, 'CHS####XXX'):
            print('    Chassis number must match format CHS####XXX')
            return
        vtype       = self.get_user_input('    Vehicle type (Enter to keep):', False)
        make        = self.get_user_input('    Make (Enter to keep):', False)
        model       = self.get_user_input('    Model (Enter to keep):', False)
        year        = self.get_user_input('    Year (Enter to keep):', False)
        year_i      = int(year) if year else None
        body        = self.get_user_input('    Body type (Enter to keep):', False)
        capacity    = self.get_user_input('    Capacity (Enter to keep):', False)
        try:
            cap_i = int(capacity) if capacity else None
            if cap_i is not None and cap_i <= 0:
                raise ValueError
        except Exception:
            print('    Capacity must be a positive integer.')
            return
        color       = self.get_user_input('    Color (Enter to keep):', False)
        owner       = self.get_user_input('    Owner Driver ID (Enter to keep):', False)
        owner_id    = int(owner) if owner else None
        # Call the database controller to update the vehicle record with the new values, 
        # passing None for any fields that the user chose to keep unchanged.
        res         = self.db.update_vehicle(
            vid,                # Vehicle_id     (required to identify which record to update)
            engine or None,     # Engine_number  (E.g.: ENG####X)
            plate or None,      # Plate_number   (E.g.: ABC####)
            chassis or None,    # Chassis_number (E.g.: CHS####XYZ)
            vtype or None,      # Vehicle_type   (E.g.: 'motorcycle', 'private car', 'public utility vehicle', 'truck', 'others')
            make or None,       # Make           (E.g.: 'Toyota',  'Honda', 'Ford',  'Mitsubishi', 'Nissan', 'Isuzu',  'Hyundai', 'Kia',      'Subaru',   'Mazda', etc.)
            model or None,      # Model          (E.g.: 'Corolla', 'Civic', 'F-150', 'L300',       'Accord', 'Triton', 'Elantra', 'Sportage', 'Forester', 'CX-5', etc.)
            year_i,             # Year           (E.g.: 1995, 2020, etc.)
            body or None,       # Body_type      (E.g.: 'sedan', 'hatchback', 'SUV', 'pickup', 'van', etc.)
            cap_i,              # Capacity       (E.g.: 4, 5, 15, etc.)
            color or None,      # Color          (E.g.: 'white', 'black', 'silver', 'blue', 'red', etc.)
            owner_id)           # Driver_id      (Must be an existing Driver ID in the database to link the vehicle to a driver record)
        # Present the result of the update operation to the user, 
        # indicating whether the update was successful or if any errors occurred.
        self._present_proc_result(res, 'update vehicle')

    # Allows the user to delete an existing vehicle record by first searching for the vehicle using its ID,
    # displaying the current details, and then asking for confirmation before proceeding with the deletion.
    def delete_vehicle_flow(self):
        vid_raw = self.get_user_input('    Enter Vehicle ID to delete:', True)
        if vid_raw is None:
            return
        try:
            vid = int(vid_raw) # Validate that the input is an integer.
        except Exception:
            print('    Invalid Vehicle ID')
            return
        # Try to find vehicle
        try:
            # Attempt to find the vehicle record in the database using the provided Vehicle ID. 
            # If not found, handle the exception and set found to None.
            found = self.db.call_proc('FindVehicle', [vid])
        except Exception:
            found = None
        if not found:
            print('    Vehicle not found')
            return
        rec = found[0]
        # Display the current details of the vehicle record to the user before confirming deletion, 
        # allowing them to review the information and cancel if they change their mind.
        self._display_record(rec, title='    Record to delete:')
        # Ask for confirmation before proceeding with the deletion of the vehicle record from the database.
        if not self._confirm('    Proceed to delete this vehicle?'):
            print('    Aborted')
            return
        # Call the database controller to delete the vehicle record with the specified Vehicle ID, 
        # and then present the result of the deletion operation to the user.
        res = self.db.delete_vehicle(vid)
        # Present the result of the delete operation to the user, 
        # indicating whether the deletion was successful or if any errors occurred.
        self._present_proc_result(res, 'delete vehicle')

    # Registration and Violation placeholders (update/delete)
    # This function allows the user to update an existing vehicle registration record 
    # by first searching for the registration using its number,
    # displaying the current details, and then prompting for new values for each field.
    def update_vehicle_registration_flow(self):
        # Prompt the user to enter the registration number of the vehicle registration record they wish to update.
        reg = self.get_user_input('    Registration number to update (Format: REG#####):', True)
        if reg is None:
            return
        else:
            if not self.validate_pattern(reg, 'REG#####'):
                print('    Registration number must match format "REG#####"!')
                return
        # Attempt to find the vehicle registration record in the database using the provided registration number.
        # If not found, handle the exception and set found to None.
        found = self.db.find_vehicle_registration(reg)
        if not found:
            print('    Registration not found!')
            return
        rec = found[0]
        # Display the current details of the vehicle registration record to the user before confirming the update,
        # allowing them to review the information and cancel if they change their mind.
        self._display_record(rec, title='    Current registration:')
        # Ask for confirmation before proceeding with the update of the vehicle registration record in the database.
        if not self._confirm('    Proceed to update this registration?'):
            print('    Aborted')
            return
        # Prompt the user for new values for each field of the vehicle registration record, 
        # allow to keep existing values by entering 'n/a'.
        reg_date = self.get_user_input('    Registration date (YYYY-MM-DD) (Enter to keep):', False)
        # Validate the registration date input to ensure it is in the correct format. 
        # If the input is invalid, inform the user and exit the update flow.
        if reg_date and validate_date(reg_date) is None:
            print('    Invalid date')
            return
        # Prompt for the expiration date and validate it in the same way as the registration date, 
        # ensuring that any new expiration date entered by the user is in the correct format before proceeding with the update.
        exp_date = self.get_user_input('    Expiration date (YYYY-MM-DD) (Enter to keep):', False)
        if exp_date and validate_date(exp_date) is None:
            print('    Invalid date')
            return
        effective_reg_date = reg_date or rec.get('Registration_date')
        effective_exp_date = exp_date or rec.get('Expiration_date')
        if effective_reg_date is not None and effective_exp_date is not None:
            if validate_dates(effective_reg_date, effective_exp_date) is None:
                print('    Expiration date must not be earlier than the registration date')
                return
        # Prompt for the status and validate it.
        status = self.get_user_input('    Status (Enter to keep):', False)
        # Prompt for the OR number.
        or_number = self.get_user_input('    OR number (Enter to keep):', False)
        # Prompt for the OR date and validate it.
        or_date = self.get_user_input('    OR date (YYYY-MM-DD) (Enter to keep):', False)
        if or_date and validate_date(or_date) is None:
            print('    Invalid OR date')
            return
        # Prompt for the document reference and ownership type, transfer reason, ownership start and end dates, and vehicle ID, 
        # allowing the user to keep existing values by entering 'n/a' for each field.
        doc_ref             = self.get_user_input('    Doc ref (Enter to keep):', False)
        ownership           = self.get_user_input('    Ownership type (Enter to keep):', False)
        transfer_reason     = self.get_user_input('    Transfer reason (Enter to keep):', False)
        start_date          = self.get_user_input('    Ownership start date (YYYY-MM-DD) (Enter to keep):', False)
        end_date            = self.get_user_input('    Ownership end date (YYYY-MM-DD) (Enter to keep):', False)
        vehicle_id          = self.get_user_input('    Vehicle ID (Enter to keep):', False)
        vehicle_id_int      = int(vehicle_id) if vehicle_id else None
        effective_start_date = start_date or rec.get('Ownership_start_date')
        effective_end_date = end_date or rec.get('Ownership_end_date')
        if effective_start_date is not None and effective_end_date is not None:
            if validate_dates(effective_start_date, effective_end_date) is None:
                print('    Ownership end date must not be earlier than the ownership start date')
                return
        # Call the database controller to update the vehicle registration record with the new values,
        # passing None for any fields that the user chose to keep unchanged, and then present the
        res = self.db.update_vehicle_registration(
            reg,                        # Registration_number (primary key, cannot be changed)
            reg_date or None,           # Registration_date
            exp_date or None,           # Expiration_date
            status or None,             # Registration_status
            or_number or None,          # OR_number
            or_date or None,            # OR_date
            doc_ref or None,            # Document_reference
            ownership or None,          # Ownership_type
            transfer_reason or None,    # Transfer_reason
            start_date or None,         # Ownership_start_date
            end_date or None,           # Ownership_end_date
            vehicle_id_int)             # Vehicle_id (foreign key to Vehicle)
        # Present the result of the update operation to the user, 
        # indicating whether the update was successful or if any errors occurred.
        self._present_proc_result(res, 'update registration')

    # Allows the user to delete an existing vehicle registration record by first searching for the registration using its number,
    # displaying the current details, and then asking for confirmation before proceeding with the deletion.
    def delete_vehicle_registration_flow(self):
        # Prompt the user to enter the registration number of the vehicle registration record they wish to delete.
        reg = self.get_user_input('    Registration number to delete:', True)
        if reg is None:
            return
        # Attempt to find the vehicle registration record in the database using the provided registration number.
        # If not found, handle the exception and set found to None.
        found = self.db.find_vehicle_registration(reg)
        if not found:
            print('    Registration not found!')
            return
        # Display the current details of the vehicle registration record to the user before confirming the deletion,
        # allowing them to review the information and cancel if they change their mind.
        self._display_record(found[0], title='    Registration to delete:')
        if not self._confirm('Proceed to delete this registration?'):
            print('    Aborted')
            return
        # Call the database controller to delete the vehicle registration record with the specified registration number,
        # and then present the result of the deletion operation to the user.
        res = self.db.delete_vehicle_registration(reg)
        # Present the result of the delete operation to the user, indicating whether the deletion was successful or if any errors occurred.
        self._present_proc_result(res, 'delete registration')

    # This function allows the user to add a new traffic violation record by prompting for all necessary details,
    # validating the inputs, and then calling the database controller to add the violation record if the user confirms.
    def add_violation_flow(self):
        # AddTrafficViolation/AddViolation expects: 
        #       datetime, status, fine, payment_date, driver_id, vehicle_id, violation_type_id, officer_id, location_id
        vdatetime   = self.get_user_input('    Violation datetime (YYYY-MM-DD HH:MM:SS):', True)
        try:
            # Validate that the violation datetime is in the correct format.
            vdatetime_obj = datetime.strptime(vdatetime, '%Y-%m-%d %H:%M:%S')
        except Exception:
            print('    Invalid datetime format')
            return
        # Prompt for the violation status and validate that it is one of the allowed values ('unpaid', 'paid', 'contested').
        status          = self.get_user_input("    Status ('unpaid'|'paid'|'contested'):", True)
        if validate_enum(status, ['unpaid', 'paid', 'contested']) is None:
            print('    Invalid status')
            return
        # Prompt for the fine amount and validate that it can be converted to a float, which is necessary for ensuring that the fine is a valid numeric value before adding the violation record to the database.
        fine            = self.get_user_input('    Fine amount (e.g., 500.00):', True)
        try:
            fine_f      = float(fine)
        except Exception:
            print('    Invalid fine amount')
            return
        # Prompt for the payment date and validate that it is in the correct format if provided, 
        # allowing the user to leave it blank if there is no payment date.
        payment_date    = self.get_user_input('    Payment date (YYYY-MM-DD) (n/a if none):', False)
        if payment_date and validate_date(payment_date) is None:
            print('    Invalid payment date')
            return
        if validate_dates(vdatetime_obj.date(), payment_date) is None:
            print('    Payment date must not be earlier than violation datetime')
            return
        # Prompt for the driver ID, vehicle ID, violation type ID, officer ID, and location ID, 
        # validating that each can be converted to an integer (for ensuring that the IDs are valid).
        driver_id       = self.get_user_input('    Driver ID:', True)
        try:
            did = int(driver_id)
        except Exception:
            print('    Invalid Driver ID')
            return
        if not self.db.find_driver(did):
            print('    Driver not found')
            return
        # Prompt for the vehicle ID and validate that it can be converted to an integer, 
        # which is necessary for linking the violation record to a specific vehicle in the database.
        vehicle_id      = self.get_user_input('    Vehicle ID:', True)
        try:
            vid = int(vehicle_id)
        except Exception:
            print('    Invalid Vehicle ID')
            return
        if not self.db.find_vehicle(vid):
            print('    Vehicle not found')
            return
        # Prompt for the violation type ID and validate that it can be converted to an integer,
        # which is necessary for linking the violation record to a specific violation type in the database.
        violation_type_id = self.get_user_input('    Violation type ID:', True)
        try:
            vtid = int(violation_type_id)
        except Exception:
            print('    Invalid violation type ID')
            return
        if not self.db.find_violation_type(vtid):
            print('    Violation type not found')
            return
        # Prompt for the officer ID and validate that it can be converted to an integer,
        # which is necessary for linking the violation record to a specific officer in the database.
        officer_id      = self.get_user_input('    Officer ID:', True)
        try:
            oid = int(officer_id)
        except Exception:
            print('    Invalid officer ID')
            return
        if not self.db.find_officer(oid):
            print('    Officer not found')
            return
        # Prompt for the location ID and validate that it can be converted to an integer,
        # which is necessary for linking the violation record to a specific location in the database.
        location_id     = self.get_user_input('    Location ID:', True)
        try:
            lid = int(location_id)
        except Exception:
            print('    Invalid location ID')
            return
        if not self.db.find_location(lid):
            print('    Location not found')
            return
        # Call the database controller to add the new traffic violation record with the provided details,
        res = self.db.add_traffic_violation(
            vdatetime,              # Violation_date    (E.g.: '2023-01-31')
            status,                 # Violation_status  (E.g.: 'unpaid', 'paid', 'contested')
            fine_f,                 # Fine_amount       (must be a valid float)
            payment_date or None,   # Payment_date      (E.g.: '2023-02-15', can be None if not provided)
            did,                    # Driver_id         (must be a valid integer)
            vid,                    # Vehicle_id        (Must be a valid integer)
            vtid,                   # Violation_type_id (must be a valid integer)
            oid,                    # Officer_id        (must be a valid integer)
            lid)                    # Location_id       (must be a valid integer)
        # Present the result of the add operation to the user, indicating whether the addition was successful or if any errors occurred.
        self._present_proc_result(res, 'add violation')

    # Function to update an existing traffic violation record by first searching for the violation using its ID,
    # displaying the current details, and then prompting for new values for each field, with validation
    def update_violation_flow(self):
        # Prompt the user to enter the violation ID of the traffic violation record they wish to update.
        vid         = self.get_user_input('    Violation ID to update:', True)
        try:
            vid_i = int(vid)
        except Exception:
            print('    Invalid Violation ID')
            return
        # Attempt to find the traffic violation record in the database using the provided violation ID.
        found       = self.db.call_proc('FindTrafficViolation', [vid_i])
        if not found:
            print('    Violation not found')
            return
        # Display the current details of the traffic violation record to the user before confirming the update,
        # allowing them to review the information and cancel if they change their mind.
        self._display_record(found[0], title='    Current violation:')
        if not self._confirm('    Proceed to update this violation?'):
            print('    Aborted')
            return
        # Prompt full signature matching UpdateTrafficViolation
        vdatetime   = self.get_user_input('    Violation datetime (YYYY-MM-DD HH:MM:SS) (n/a to keep):', False)
        if vdatetime and len(vdatetime) > 0:
            try:
                datetime.strptime(vdatetime, '%Y-%m-%d %H:%M:%S')
            except Exception:
                print('    Invalid datetime')
                return
        # Prompt for the violation status and validate that it is one of the allowed values ('unpaid', 'paid', 'contested'),
        # allowing the user to keep the existing status by entering 'n/a'.
        status      = self.get_user_input("    Violation status ('unpaid'|'paid'|'contested') (n/a to keep):", False)
        if status and validate_enum(status, ['unpaid', 'paid', 'contested']) is None:
            print('    Invalid status')
            return
        # Prompt for the fine amount and validate that it can be converted to a float.
        fine        = self.get_user_input('    Fine amount (n/a to keep):', False)
        fine_f = float(fine) if fine else None
        # Prompt for the payment date and validate that it is in the correct format if provided.
        payment_date = self.get_user_input('    Payment date (YYYY-MM-DD) (n/a to keep):', False)
        if payment_date and validate_date(payment_date) is None:
            print('    Invalid payment date')
            return
        effective_vdatetime = vdatetime or found[0].get('Violation_date')
        effective_payment_date = payment_date or found[0].get('Payment_date')
        if effective_vdatetime is not None and effective_payment_date is not None:
            if validate_dates(effective_vdatetime, effective_payment_date) is None:
                print('    Payment date must not be earlier than violation datetime')
                return
        # Prompt for the driver ID, vehicle ID, violation type ID, officer ID, and location ID, 
        # validating that each can be converted to an integer if provided.
        driver      = self.get_user_input('    Driver ID (n/a to keep):', False)
        try:
            driver_i = int(driver) if driver else None
        except Exception:
            print('    Invalid Driver ID')
            return
        if driver_i is not None and not self.db.find_driver(driver_i):
            print('    Driver not found')
            return
        # Prompt for the vehicle ID and validate that it can be converted to an integer if provided.
        vehicle     = self.get_user_input('    Vehicle ID (n/a to keep):', False)
        try:
            vehicle_i = int(vehicle) if vehicle else None
        except Exception:
            print('    Invalid Vehicle ID')
            return
        if vehicle_i is not None and not self.db.find_vehicle(vehicle_i):
            print('    Vehicle not found')
            return
        # Prompt for the violation type ID and validate that it can be converted to an integer if provided.
        vtype_id    = self.get_user_input('    Violation type ID (n/a to keep):', False)
        try:
            vtype_i = int(vtype_id) if vtype_id else None
        except Exception:
            print('    Invalid violation type ID')
            return
        if vtype_i is not None and not self.db.find_violation_type(vtype_i):
            print('    Violation type not found')
            return
        # Prompt for the officer ID and validate that it can be converted to an integer if provided.
        officer     = self.get_user_input('    Officer ID (n/a to keep):', False)
        try:
            officer_i = int(officer) if officer else None
        except Exception:
            print('    Invalid officer ID')
            return
        if officer_i is not None and not self.db.find_officer(officer_i):
            print('    Officer not found')
            return
        # Prompt for the location ID and validate that it can be converted to an integer if provided.
        location    = self.get_user_input('    Location ID (n/a to keep):', False)
        try:
            location_i = int(location) if location else None
        except Exception:
            print('    Invalid location ID')
            return
        if location_i is not None and not self.db.find_location(location_i):
            print('    Location not found')
            return
        # Call the database controller to update the traffic violation record with the new values, 
        # passing None for any fields that the user chose to keep unchanged, and then present the result of the update operation to the user.
        res = self.db.update_traffic_violation(vid_i, vdatetime or None, status or None, fine_f, payment_date or None, driver_i, vehicle_i, vtype_i, officer_i, location_i)
        # Present the result of the update operation to the user. 
        # Indicates whether the update was successful or if any errors occurred.
        self._present_proc_result(res, 'update violation')

    # This function allows the user to delete an existing traffic violation record by first searching for the violation using its ID,
    # displaying the current details, and then asking for confirmation before proceeding with the deletion.
    def delete_violation_flow(self):
        # Prompt the user to enter the violation ID of the traffic violation record they wish to delete.
        vid = self.get_user_input('    Violation ID to delete:', True)
        try:
            vid_i = int(vid)
        except Exception:
            print('    Invalid Violation ID')
            return
        # Attempt to find the traffic violation record in the database using the provided violation ID.
        found = self.db.call_proc('    FindTrafficViolation', [vid_i])
        if not found:
            print('    Violation not found')
            return
        # Display the current details of the traffic violation record to the user before confirming the deletion.
        self._display_record(found[0], title='    Violation to delete:')
        if not self._confirm('    Proceed to delete this violation?'):
            print('    Aborted')
            return
        # Call the database controller to delete the traffic violation record with the specified violation ID.
        res = self.db.delete_traffic_violation(vid_i)
        # Present the result of the delete operation to the user.
        # Indicates whether the deletion was successful or if any errors occurred.
        self._present_proc_result(res, 'delete violation')

    # Driver CRUD implementations (adding, searching, updating driver records in the system).
    # This function prompts the user for details about a new driver, displays a preview of the entered information,
    # and then calls the database controller to add the driver record if the user confirms.
    def add_driver(self):
        # Prompt for driver first name (Required)
        first           = self.get_user_input('    First name:', True)
        if first is None:
            print('    Canceled')
            return
        # Prompts for the middle name (Optional)
        middle          = self.get_user_input('    Middle name (n/a if none):', False)
        # Prompt for the last name (Required)
        last            = self.get_user_input('    Last name:', True)
        if last is None:
            print('    Canceled')
            return
        # Prompt for the suffix (Optional)
        suffix          = self.get_user_input('    Suffix (n/a if none):', False)
        # Prompt for the date of birth and validate that it is in the correct format (YYYY-MM-DD). 
        # Necessary for ensuring that the driver record has a valid date of birth before adding it to the database.
        dob = self.get_user_input('    Date of birth (YYYY-MM-DD):', True)
        if validate_date(dob) is None:
            print('    Invalid date')
            return
        # Prompt for the weight and validate that it can be converted to a float before adding it to the database.
        weight          = self.get_user_input('    Weight (kg):', True)
        try:
            weight = float(weight)
        except Exception:
            print('    Invalid weight')
            return
        # Prompt for the height and validate that it can be converted to a float before adding it to the database.
        height          = self.get_user_input('    Height (cm):', True)
        try:
            height = float(height)
        except Exception:
            print('    Invalid height')
            return
        # Prompt for the sex assigned at birth and validate that it is one of the allowed values ('Male', 'Female', 'Other').
        sex = self.get_user_input("    Sex ('Male'|'Female'|'Other'):", True)
        if validate_enum(sex, ['Male', 'Female', 'Other']) is None:
            print('    Invalid sex')
            return
        # Prompt for the nationality (Optional)
        nationality     = self.get_user_input('    Nationality:', False)
        # Prompt for the civil status and validate that it is one of the allowed values ('Single', 'Married', 'Divorced', 'Widowed').
        civil           = self.get_user_input("    Civil status ('Single'|'Married'|'Divorced'|'Widowed'):", True)
        if validate_enum(civil, ['Single', 'Married', 'Divorced', 'Widowed']) is None:
            print('    Invalid civil status')
            return
        # Prompt for the contact number and validate that it is not longer than 11 characters before adding the driver record to the database.
        contact         = self.get_user_input('    Contact number (Format: 09#########):', True)
        if not self.validate_pattern(contact, '09#########'):
            print('    Contact number must match format "09#########"!')
            return
        if len(contact) > 11:
            print('    Invalid contact length. Must be an 11-digit number starting with "09"')
            return
        # Prompt for the blood type
        blood           = self.get_user_input('    Blood type (E.g.: A+, A-, B+, B-, AB+, AB-, O+, or O-):', True)
        # Validate blood type: accept only standard types (case-insensitive)
        if blood:
            b = blood.strip().upper()
            allowed = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            if validate_enum(b, allowed) is None:
                print('    Invalid blood type. Allowed: A+, A-, B+, B-, AB+, AB-, O+, O-')
                return
        # Prompt for the house number and validate that it is not empty.
        house           = self.get_user_input('    House number:', True)
        # Prompt for the street / village and validate that it is not empty.
        street          = self.get_user_input('    Street / village:', True)
        # Prompt for the barangay and validate that it is not empty.
        barangay        = self.get_user_input('    Barangay:', True)
        # Prompt for the city / municipality and validate that it is not empty.
        city            = self.get_user_input('    City / municipality:', True)
        # Prompt for the province and validate that it is not empty.
        province        = self.get_user_input('    Province:', True)
        # Prompt for the region and validate that it is not empty.
        region          = self.get_user_input('    Region:', True)
        # Prompt for the zip code and validate that it is exactly 4 digits before adding the driver record to the database.
        zipc            = self.get_user_input('    Zip code:', True)
        if not zipc.isdigit() or len(zipc) != 4:
            print('    Zip code must be 4 digits')
            return
        # Shows a preview of the entered driver information before confirming the addition of the driver record to the database.
        preview = {
            'First_name': first,
            'Middle_name': middle,
            'Last_name': last,
            'Suffix': suffix,
            'Date_of_birth': dob,
            'Sex_assigned_at_birth': sex,
            'Contact_number': contact
        }
        # Display the preview of the entered driver information to the user
        # Allows user to review the details before confirming the addition of the driver record to the database.
        self._display_record(preview, title='New driver preview:')
        if not self._confirm('Proceed to add this driver?'):
            print('Aborted')
            return
        # Call the database controller to add the new driver record with the provided details, 
        # and then present the result of the add operation to the user.
        res = self.db.add_driver(
            first,                  # First_name            (Required) 
            middle,                 # Middle_name           (Optional)
            last,                   # Last_name             (Required)
            suffix,                 # Suffix                (Optional)
            dob,                    # Date_of_birth         (Required, format: YYYY-MM-DD)
            weight,                 # Weight                (Required, must be a valid float)
            height,                 # Height                (Required, must be a valid float)
            sex,                    # Sex_assigned_at_birth (Required, must be 'Male', 'Female', or 'Other')
            nationality or None,    # Nationality           ('Filipino' if left blank, otherwise use provided value)
            civil,                  # Civil_status          (Required, must be 'Single', 'Married', 'Divorced', or 'Widowed')
            contact,                # Contact_number        (Required, must not be longer than 11 characters)
            blood,                  # Blood_type            (Required)
            house,                  # House_number          (Required)
            street,                 # Street_village        (Required)
            barangay,               # Barangay              (Required)
            city,                   # City_municipality     (Required)
            province,               # Province              (Required)
            region,                 # Region                (Required)
            zipc)                   # Zip_code              (Required, must be exactly 4 digits)
        # Present the result of the add operation to the user. 
        # Indicates whether the addition was successful or if any errors occurred.
        self._present_proc_result(res, 'add driver')

    # Allows the user to search for a driver record by entering the Driver ID,
    # and then displays the details of the matching driver record(s) if found, 
    # or informs the user if no matching records are found.
    def search_driver_flow(self):
        # Require Driver ID for precise lookup
        did_raw = self.get_user_input('    Driver ID (required):', True)
        if did_raw is None:
            return
        try:
            did = int(did_raw)
        except ValueError:
            print('    Invalid Driver ID')
            return
        rows = self.db.find_driver(did)
        if not rows:
            print('    No matching drivers')
            return
        for r in rows:
            self._display_record(r, title="    Driver Record:")

    # Allows user to update the information of an existing driver record by entering the Driver ID,
    # and then prompts the user to enter the updated details for the driver.
    def update_driver_flow(self):
        # Require Driver ID for precise lookup
        did_raw = self.get_user_input('    Enter Driver ID to update:', True)
        if did_raw is None:
            return
        try:
            did = int(did_raw)
        except ValueError:
            print('    Invalid Driver ID')
            return
        # Attempt to find the driver record in the database using the provided Driver ID.
        found = self.db.find_driver(did)
        if not found:
            print('    Driver not found')
            return
        rec = found[0]
        # Display the current details of the driver record to the user before confirming the update,
        # allowing them to review the information and cancel if they change their mind.
        self._display_record(rec, title='    Current record:')
        if not self._confirm('    Proceed to update this driver?'):
            print('    Aborted')
            return
        # Prompt fields; blank or 'n/a' keeps existing values from rec
        def pick(field_name, prompt, required=False, validator=None, cast=None):
            val = self.get_user_input(prompt, False)
            if val is None or val == '':
                return rec.get(field_name)
            if validator and validator(val) is None:
                raise ValueError(f'    Invalid value for {field_name}')
            if cast:
                return cast(val)
            return val
        # Prompt for new values for each field of the driver record, allowing the user to keep existing values by entering 'n/a' or leaving it blank.
        try:
            first           = pick('First_name',            '    First name (Enter to keep):')
            middle          = pick('Middle_name',           '    Middle name (Enter to keep):')
            last            = pick('Last_name',             '    Last name (Enter to keep):')
            suffix          = pick('Suffix',                '    Suffix (Enter to keep):')
            dob             = pick('Date_of_birth',         '    Date of birth (YYYY-MM-DD) (Enter to keep):', validator=validate_date)
            weight          = pick('Weight',                '    Weight (kg) (Enter to keep):', cast=float)
            height          = pick('Height',                '    Height (cm) (Enter to keep):', cast=float)
            sex             = pick('Sex_assigned_at_birth', "    Sex ('Male'|'Female'|'Other') (Enter to keep):", validator=lambda v: validate_enum(v, ['Male', 'Female', 'Other']))
            nationality     = pick('Nationality',           '    Nationality (Enter to keep):')
            civil           = pick('Civil_status',          "    Civil status (Enter to keep):", validator=lambda v: validate_enum(v, ['Single', 'Married', 'Divorced', 'Widowed']))
            contact         = pick('Contact_number',        '    Contact number (Enter to keep):')
            if not self.validate_pattern(contact, '09#########'):
                print('    Contact number must match format "09#########"!')
                return
            blood           = pick('Blood_type',            '    Blood type (E.g.: A+, A-, B+, B-, AB+, AB-, O+, or O-):')
            if blood:
                b = blood.strip().upper()
                allowed = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
                if validate_enum(b, allowed) is None:
                    print('    Invalid blood type. Allowed: A+, A-, B+, B-, AB+, AB-, O+, O-')
                    return
            house           = pick('House_number',          '    House number (Enter to keep):')
            street          = pick('Street_village',        '    Street / village (Enter to keep):')
            barangay        = pick('Barangay',              '    Barangay (Enter to keep):')
            city            = pick('City_municipality',     '    City / municipality (Enter to keep):')
            province        = pick('Province',              '    Province (Enter to keep):')
            region          = pick('Region',                '    Region (Enter to keep):')
            zipc            = pick('Zip_code',              '    Zip code (Enter to keep):')
            if not zipc.isdigit() or len(zipc) != 4:
                print('    Zip code must be 4 digits')
                return
        except ValueError as e:
            print(str(e))
            return
        # Call the database controller to update the driver record with the new values, 
        # passing None for any fields that the user chose to keep unchanged, and then present the result of the update operation to the user.
        res = self.db.update_driver(
            did,            # Driver_id             
            first,          # First_name            
            middle,         # Middle_name           
            last,           # Last_name             
            suffix,         # Suffix                
            dob,            # Date_of_birth         
            weight,         # Weight                
            height,         # Height                
            sex,            # Sex_assigned_at_birth 
            nationality,    # Nationality           
            civil,          # Civil_status          
            contact,        # Contact_number        
            blood,          # Blood_type            
            house,          # House_number          
            street,         # Street_village        
            barangay,       # Barangay              
            city,           # City_municipality     
            province,       # Province              
            region,         # Region                
            zipc)           # Zip_code              
        # Present the result of the update operation to the user.
        # Indicates whether the update was successful or if any errors occurred.
        self._present_proc_result(res, 'update driver')

    # This function allows the user to delete an existing driver record by entering the Driver ID,
    # and then asks for confirmation before proceeding with the deletion of the driver record from the database.
    def delete_driver_flow(self):
        # Prompt the user to enter the Driver ID of the driver record they wish to delete.
        did_raw = self.get_user_input('Enter Driver ID to delete:', True)
        if did_raw is None:
            return
        try:
            did = int(did_raw)
        except ValueError:
            print('Invalid Driver ID')
            return
        # Attempt to find the driver record in the database using the provided Driver ID. 
        # If not found, inform the user and exit the deletion flow.
        found = self.db.find_driver(did)
        if not found:
            print('Driver not found')
            return
        rec = found[0]
        # Display the current details of the driver record to the user before confirming the deletion,
        # allowing them to review the information and cancel if they change their mind.
        self._display_record(rec, title='Record to delete:')
        # Ask the user for confirmation before proceeding with the deletion of the driver record from the database,
        # ensuring that they have a chance to cancel if they change their mind after reviewing the details of the driver record.
        if not self._confirm('Proceed to delete this driver?'):
            print('Aborted')
            return
        # Call the database controller to delete the driver record with the specified Driver ID, 
        # and then present the result of the deletion operation to the user.
        res = self.db.delete_driver(did)
        # Present the result of the delete operation to the user, indicating whether the deletion was successful or if any errors occurred.
        self._present_proc_result(res, 'delete driver')

    # This function allows the user to add a new driver's license record by prompting for all necessary details, validating the inputs,
    # and then calling the database controller to add the license record if the user confirms.
    def add_license_flow(self):
        # Require Driver ID for precise lookup of associated driver record
        # This ensures that the license is linked to an existing driver in the database and prevents adding a license for a non-existent driver.
        did_raw = self.get_user_input('    Driver ID:', True)
        if did_raw is None:
            return
        try:
            did = int(did_raw)
        except Exception:
            print('    Driver ID must be integer')
            return
        # Attempt to find the driver record in the database using the provided Driver ID.
        drv = self.db.find_driver(did)
        if not drv:
            print('    Driver not found')
            return
        # check driver has no existing license yet.
        existing = self.db.find_license_by_driver(did)
        if existing:
            print('    Driver already has a license on file')
            return
        # Prompt for the license number, type, status, issue date, expiry date, DL codes, and conditions, 
        # with validation for each input to ensure that the license record has valid and complete information before adding it to the database.
        license_number = self.get_user_input('    License number:', True)
        if license_number is None:
            return
        # Prompt for the license type and validate that it is one of the allowed values ('Student Permit', 'Non-Professional', 'Professional').
        license_type = self.get_user_input("    License type ('Student Permit'|'Non-Professional'|'Professional'):", True)
        if validate_enum(license_type, ['Student Permit', 'Non-Professional', 'Professional']) is None:
            print('    Invalid license type')
            return
        # Prompt for the license status and validate that it is one of the allowed values ('valid', 'expired', 'suspended', 'revoked').
        license_status = self.get_user_input("    License status ('valid'|'expired'|'suspended'|'revoked'):", True)
        if validate_enum(license_status, ['valid', 'expired', 'suspended', 'revoked']) is None:
            print('    Invalid license status')
            return
        # Prompt for the issue date and validate that it is in the correct format (YYYY-MM-DD).
        issue_date = self.get_user_input('    Issue date (YYYY-MM-DD):', True)
        if validate_date(issue_date) is None:
            print('    Invalid date')
            return
        # Prompt for the expiry date and validate that it is in the correct format (YYYY-MM-DD).
        expiry_date = self.get_user_input('    Expiry date (YYYY-MM-DD):', True)
        if validate_date(expiry_date) is None:
            print('    Invalid date')
            return
        if validate_dates(issue_date, expiry_date) is None:
            print('    Expiry date must not be earlier than the issue date')
            return
        # Prompt for DL codes (at least one required) and allow the user to enter multiple DL codes 
        # until they indicate they are finished by entering 'n/a' or leaving it blank.
        dl_codes = []
        print('    Enter DL codes (enter blank or n/a to finish). At least one required.')
        while True:
            code = self.get_user_input('    DL code (or n/a to finish):', False)
            if code is None or code == '':
                break
            dl_codes.append(code)
        if not dl_codes:
            print('    At least one DL code is required')
            return
        # Prompt for license conditions (optional) and allow the user to enter multiple conditions 
        # until they indicate they are finished by entering 'n/a' or leaving it blank.
        conditions = []
        print('    Enter license conditions (optional). Enter blank or n/a to finish.')
        while True:
            cond = self.get_user_input('    Condition (or n/a to finish):', False)
            if cond is None or cond == '':
                break
            conditions.append(cond)
        # Shows a preview of the entered license information before confirming the addition of the license record to the database,
        # allowing the user to review the details before confirming the addition of the license record to the
        preview = {
            '    License_number': license_number,
            '    License_type': license_type,
            '    License_status': license_status,
            '    License_issue_date': issue_date,
            '    License_expiry_date': expiry_date,
            '    Driver_id': did,
            '    DL_codes': ', '.join(dl_codes),
            '    Conditions': ', '.join(conditions) if conditions else None
        }
        # Display the preview of the entered license information to the user, 
        # allowing them to review the details before confirming the addition of the license record to the database.
        self._display_record(preview, title='    New license preview:')
        if not self._confirm('    Proceed to add this license?'):
            print('    Aborted')
            return
        # Call the database controller to add the new license record with the provided details, 
        # and then present the result of the add operation to the user.
        try:
            res = self.db.add_license(license_number, license_type, license_status, issue_date, expiry_date, did)
            self._present_proc_result(res, 'add license')
        except Exception as e:
            print('    Failed to add license:', str(e))
            return
        # Add DL codes
        for code in dl_codes:
            try:
                res = self.db.add_license_dlcode(license_number, code)
                self._present_proc_result(res, 'add license dlcode')
            except Exception as e:
                print(f'    Failed to add DL code {code}:', str(e))
        # Add conditions
        for cond in conditions:
            try:
                res = self.db.add_license_condition(license_number, cond)
                self._present_proc_result(res, 'add license condition')
            except Exception as e:
                print(f'    Failed to add condition {cond}:', str(e))

    # This function allows the user to update the details of an existing driver's license record 
    # by first searching for the license using either the Driver ID or License number,
    # displaying the current details, and then prompting for new values for each field, with validation
    def update_license_flow(self):
        # Ask for Driver ID or License number (either required)
        did_raw = self.get_user_input('    Driver ID (n/a if none):', False)
        lic_raw = self.get_user_input('    License number (n/a if none):', False)
        if (did_raw is None or did_raw == '') and (lic_raw is None or lic_raw == ''):
            print('    Provide at least a Driver ID or a License number')
            return

        rows = None
        license_row = None
        # Normalize the inputs
        did = None
        if did_raw and did_raw != '':
            try:
                did = int(did_raw)
            except Exception:
                print('    Driver ID must be integer')
                return
        # If license number provided, search by license number (more specific). Otherwise, search by driver id.
        if lic_raw and lic_raw != '':
            lic = lic_raw
            rows = self.db.get_license_by_number(lic)
            if not rows:
                print('    No license found with that number')
                return
            license_row = rows[0]
            if did is not None and int(license_row.get('Driver_id')) != did:
                print('    Provided Driver ID and License number do not match')
                return
        else:
            # search by driver id
            if did is None:
                print('    No input provided')
                return
            rows = self.db.call_proc('ShowDriverLicense', [did])
            if not rows:
                print('    No license found for that driver')
                return
            # Assume single/current license
            license_row = rows[0]
        # Display the current details of the license record to the user before confirming the update, 
        # allowing them to review the information and cancel if they change their mind.
        title = f"    License {license_row.get('License_number')}"
        self._display_record(license_row, title=title)
        if not self._confirm('    Proceed to edit this license?'):
            print('    Aborted')
            return
        # Prompt for new values for each field of the license record, allowing the user to keep existing values by entering 'n/a' or leaving it blank.
        new_type = self.get_user_input("    License type ('Student Permit'|'Non-Professional'|'Professional') (n/a to keep):", False)
        if new_type and validate_enum(new_type, ['Student Permit', 'Non-Professional', 'Professional']) is None:
            print('    Invalid license type')
            return
        # Note: status change may have implications (e.g. if changing to suspended or revoked, may want to remove DL codes and add conditions - but for simplicity we won't enforce that here)
        new_status = self.get_user_input("    License status ('valid'|'expired'|'suspended'|'revoked') (n/a to keep):", False)
        if new_status and validate_enum(new_status, ['valid', 'expired', 'suspended', 'revoked']) is None:
            print('    Invalid license status')
            return
        # For simplicity, we won't enforce that issue date cannot be in the future or expiry date cannot be in the past, but we will validate the format if provided.
        new_issue = self.get_user_input('    Issue date (YYYY-MM-DD) (n/a to keep):', False)
        if new_issue and validate_date(new_issue) is None:
            print('    Invalid issue date')
            return
        # Prompt for the expiry date and validate that it is in the correct format (YYYY-MM-DD).
        new_expiry = self.get_user_input('    Expiry date (YYYY-MM-DD) (n/a to keep):', False)
        if new_expiry and validate_date(new_expiry) is None:
            print('    Invalid expiry date')
            return
        effective_issue_date = new_issue or license_row.get('License_issue_date')
        effective_expiry_date = new_expiry or license_row.get('License_expiry_date')
        if effective_issue_date is not None and effective_expiry_date is not None:
            if validate_dates(effective_issue_date, effective_expiry_date) is None:
                print('    Expiry date must not be earlier than the issue date')
                return
        # Get the license number for further operations (DL codes, conditions, main update) 
        # This is the stable identifier for the license record that won't change even if other details are updated.
        license_number = license_row.get('License_number')
        # Manage DL codes 
        print('    Current DL codes:')
        dl_rows = self.db.get_license_dlcodes(license_number)
        existing_dl = [r.get('Dl_codes') if isinstance(r, dict) else list(r.values())[0] for r in (dl_rows or [])]
        print(', '.join(existing_dl) if existing_dl else 'None')
        # Remove DL codes
        while True:
            rem = self.get_user_input('    DL code to remove (blank to stop):', False)
            if rem is None or rem == '':
                break
            if rem not in existing_dl:
                print('    Not in existing DL codes')
                continue
            try:
                res = self.db.remove_license_dlcode(license_number, rem)
                self._present_proc_result(res, 'remove dlcode')
                existing_dl.remove(rem)
            except Exception as e:
                print('    Failed to remove DL code:', str(e))
        # Add DL codes
        while True:
            add = self.get_user_input('    Add DL code (blank to stop):', False)
            if add is None or add == '':
                break
            try:
                res = self.db.add_license_dlcode(license_number, add)
                self._present_proc_result(res, 'add dlcode')
            except Exception as e:
                print('    Failed to add DL code:', str(e))
        # Manage Conditions
        print('Current Conditions:')
        cond_rows = self.db.get_license_conditions(license_number)
        existing_cond = [r.get('Condition') if isinstance(r, dict) and 'Condition' in r else list(r.values())[0] for r in (cond_rows or [])]
        print(', '.join(existing_cond) if existing_cond else 'None')
        # Remove conditions
        while True:
            remc = self.get_user_input('Condition to remove (blank to stop):', False)
            if remc is None or remc == '':
                break
            if remc not in existing_cond:
                print('Not in existing conditions')
                continue
            try:
                res = self.db.remove_license_condition(license_number, remc)
                self._present_proc_result(res, 'remove condition')
                existing_cond.remove(remc)
            except Exception as e:
                print('Failed to remove condition:', str(e))
        # Add conditions
        while True:
            addc = self.get_user_input('Add condition (blank to stop):', False)
            if addc is None or addc == '':
                break
            try:
                res = self.db.add_license_condition(license_number, addc)
                self._present_proc_result(res, 'add condition')
            except Exception as e:
                print('Failed to add condition:', str(e))
        # Update main license row
        try:
            res = self.db.update_license(license_number, new_type or None, new_status or None, new_expiry or None)
            self._present_proc_result(res, 'update license')
        except Exception as e:
            print('Failed to update license:', str(e))
            return
        # show updated record
        updated = self.db.get_license_by_number(license_number)
        if updated:
            self._display_record(updated[0], title='Updated license:')

    # Example implementations for a few actions 
    # (showing driver vehicles, showing vehicle registrations, adding a vehicle registration, renewing a vehicle registration).
    def show_driver_vehicles(self):
        # Require Driver ID for precise lookup
        driver_id = self.get_user_input('    Enter Driver ID:', True)
        if driver_id is None:
            print('    Canceled')
            return
        try:
            did = int(driver_id)
        except ValueError:
            print('    Driver ID must be an integer')
            return
        # Call the database controller to retrieve and display the vehicles associated with the specified Driver ID,
        # allowing the user to see the details of the vehicles registered to that driver.
        rows = self.db.show_driver_vehicles(did)
        if not rows:
            print('    No vehicles found or error')
            return
        for r in rows:
            print(r)

    # This function allows the user to view the registration details of a specific vehicle by entering the Vehicle ID,
    # and then retrieves and displays the registration information associated with that vehicle from the database.
    def show_vehicle_registrations(self):
        # Require Vehicle ID for precise lookup
        vehicle_id = self.get_user_input('    Enter Vehicle ID:', True)
        if vehicle_id is None:
            print('    Canceled')
            return
        try:
            vid = int(vehicle_id)
        except ValueError:
            print('    Vehicle ID must be an integer')
            return
        # Call the database controller to retrieve and display the registration details associated with the specified Vehicle ID,
        # allowing the user to see the registration information for that vehicle.
        rows = self.db.show_vehicle_registrations(vid)
        if not rows:
            print('    No registrations found or error')
            return
        for r in rows:
            self._display_record(r, title=f"    Registration {r.get('Registration_number')}")

    # This function allows the user to add a new vehicle registration record by prompting for all necessary details, validating the inputs,
    # and then calling the database controller to add the registration record if the user confirms.
    def add_vehicle_registration(self):
        # Prompt for the registration number.
        reg_number = self.get_user_input('    Registration number (Form: REG#####):', True)
        if reg_number is None:
            print('    Canceled')
            return
        else:
            if not self.validate_pattern(reg_number, 'REG#####'):
                print('    Registration number must match format "REG#####"!')
                return
        # Prompt for the registration date and validate that it is in the correct format (YYYY-MM-DD).
        reg_date = self.get_user_input('    Registration date (YYYY-MM-DD):', True)
        if validate_date(reg_date) is None:
            print('    Invalid date format')
            return
        # Prompt for the expiration date and validate that it is in the correct format (YYYY-MM-DD).
        exp_date = self.get_user_input('    Expiration date (YYYY-MM-DD):', True)
        if validate_date(exp_date) is None:
            print('    Invalid date format')
            return
        if validate_dates(reg_date, exp_date) is None:
            print('    Expiration date must not be earlier than the registration date')
            return
        # Prompt for the registration status and validate that it is one of the allowed values ('active', 'expired', 'suspended').
        status = self.get_user_input("    Status ('active'|'expired'|'suspended'):", True)
        if validate_enum(status, ['active', 'expired', 'suspended']) is None:
            print('    Invalid status')
            return
        # Prompt for the official receipt number.
        or_number = self.get_user_input('    Official receipt number (Format: OR#####):', True)
        if or_number is None:
            print('    Official receipt number is required')
            return
        else:
            if not self.validate_pattern(or_number, 'OR#####'):
                print('    Official receipt number must match format "OR#####"!')
                return
        # Prompt for the official receipt date and validate that it is in the correct format (YYYY-MM-DD).
        or_date = self.get_user_input('    Official receipt date (YYYY-MM-DD):', True)
        if validate_date(or_date) is None:
            print('    Invalid OR date format')
            return
        # Prompt for the document reference number (Optional)
        doc_ref = self.get_user_input('    Document ref no (Format: DR-### | enter if none):', False)
        if doc_ref not in (None, '') and not self.validate_pattern(doc_ref, 'DR-###'):
            print('    Document ref no must match format "DR-###"')
            return
        # Prompt for the ownership type and validate that it is one of the allowed values ('owned', 'financed', 'leased').
        ownership = self.get_user_input("    Ownership type ('owned'|'financed'|'leased') (n/a if none):", False)
        if ownership and validate_enum(ownership, ['owned', 'financed', 'leased']) is None:
            print('    Invalid ownership type')
            return
        # Prompt for the transfer reason (Optional)
        transfer_reason = self.get_user_input('    Transfer reason (n/a if none):', False)
        # Prompt for the ownership start date and validate that it is in the correct format (YYYY-MM-DD).
        start_date = self.get_user_input('    Ownership start date (YYYY-MM-DD):', True)
        if validate_date(start_date) is None:
            print('    Invalid date format')
            return
        # Prompt for the ownership end date and validate that it is in the correct format (YYYY-MM-DD).
        end_date = self.get_user_input('    Ownership end date (YYYY-MM-DD) (n/a if none):', False)
        if end_date and validate_date(end_date) is None:
            print('    Invalid date format')
            return
        if validate_dates(start_date, end_date) is None:
            print('    Ownership end date must not be earlier than the ownership start date')
            return
        # Require Vehicle ID for precise lookup of associated vehicle record
        vehicle_id = self.get_user_input('    Vehicle ID:', True)
        try:
            vid = int(vehicle_id)
        except ValueError:
            print('    Vehicle ID must be integer')
            return
        # Attempt to find the vehicle record in the database using the provided Vehicle ID.
        res = self.db.add_vehicle_registration(
            reg_number,         # Registration_number       (E.g.: REG#####)
            reg_date,           # Registration_date         (YYYY-MM-DD)
            exp_date,           # Expiration_date           (YYYY-MM-DD)
            status,             # Registration_status       ('active', 'expired', 'suspended')
            or_number,          # Official_receipt_number   (E.g. OR#####)
            or_date,            # Official_receipt_date     (YYYY-MM-DD)
            doc_ref,            # Document_reference_number (E.g.: DR-###)
            ownership,          # Ownership_type            ('owned', 'financed', 'leased')
            transfer_reason,    # Transfer_reason           (Optional free text)
            start_date,         # Ownership_start_date      (YYYY-MM-DD)
            end_date,           # Ownership_end_date        (YYYY-MM-DD)
            vid)                # Vehicle_id                (Foreign key to Vehicles table)
        # Present the result of the add operation to the user, indicating whether the addition was successful or if any errors occurred.
        self._present_proc_result(res, 'add registration')

    # This function allows the user to renew an existing vehicle registration by entering the old registration number, 
    # new registration number, registration date, and expiration date,
    # and then calls the database controller to update the registration record with the new details if the
    def renew_vehicle_registration(self):
        # Prompt for the old registration number to identify which registration record to renew.
        old_reg = self.get_user_input('    Old registration number:', True)
        if old_reg is None:
            print('    Canceled')
            return
        else: 
            if not self.validate_pattern(old_reg, 'REG####'):
                print('    Registration number must match format "REG####"!')
                return
        # Prompt for the new registration number, which will replace the old registration number in the database record.
        new_reg = self.get_user_input('    New registration number:', True)
        if new_reg is None:
            print('    Canceled')
            return
        else: 
            if not self.validate_pattern(new_reg, 'REG####'):
                print('    Registration number must match format "REG####"!')
                return
        # Prompt for the registration date and validate that it is in the correct format (YYYY-MM-DD).
        reg_date = self.get_user_input('    Registration date (YYYY-MM-DD):', True)
        if validate_date(reg_date) is None:
            print('    Invalid date format')
            return
        # Prompt for the expiration date and validate that it is in the correct format (YYYY-MM-DD).
        exp_date = self.get_user_input('    Expiration date (YYYY-MM-DD):', True)
        if validate_date(exp_date) is None:
            print('    Invalid date format')
            return
        if validate_dates(reg_date, exp_date) is None:
            print('    Expiration date must not be earlier than the registration date')
            return
        # Call the database controller to update the existing vehicle registration record with the 
        # new registration number, registration date, and expiration date,
        # effectively renewing the vehicle registration with the updated details, and then present the result of the
        res = self.db.renew_vehicle_registration(
            old_reg,        # (Old) Registration_number (E.g.: REG#####)
            new_reg,        # (New) Registration_number (E.g.: REG#####)
            reg_date,       # Registration_date         (YYYY-MM-DD)
            exp_date)       # Expiration_date           (YYYY-MM-DD)
        # Present the result of the renew operation to the user, indicating whether the renewal was successful or if any errors occurred.
        self._present_proc_result(res, 'renew registration')

    # This function allows the user to run various reports related to registered drivers, 
    # such as filtering by license type, license status, age range, and sex, 
    # by presenting a menu of report options, prompting for the necessary inputs, 
    # and then retrieving and displaying the report results from the database.
    def _run_driver_reports(self):
        # For each report type, the function prompts for the necessary inputs 
        # (e.g., license type, status, age range, sex) and validates them, 
        # then calls the appropriate database controller method to retrieve the report data, 
        # and finally displays the results to the user in a readable format.
        while True:
            # Present a menu of report options related to registered drivers, 
            # allowing the user to choose which report they want to run based on 
            # different criteria such as license type, license status, age range, and sex.
            self.print_registered_drivers_menu()
            # Prompt the user to select a report option from the menu and validate the input 
            # to ensure it corresponds to a valid report choice.
            registered_choice_num = self.get_menu_choice(4)
            if registered_choice_num is None or registered_choice_num == 0:
                return
            # Based on the user's choice, the function executes the corresponding report logic,
            # which may involve additional prompts for specific criteria (e.g., license type, status,
            # age range, sex) and then retrieves the relevant data from the database to display 
            # the report results to the user.
            if registered_choice_num == 1:
                while True:
                    # If the user selects the option to filter registered drivers by license type, 
                    # the function presents a sub-menu of license types, prompts the user to select 
                    # a license type, validates the input, and then retrieves and displays the drivers 
                    # that match the selected license type from the database.
                    self.print_license_type_menu()
                    # Prompt the user to select a license type from the sub-menu 
                    # and validate the input to ensure it corresponds to a valid license type choice.
                    license_choice = self.get_menu_choice(3)
                    if license_choice is None:
                        return
                    if license_choice == 0:
                        break
                    # Map the user's license type choice to the corresponding database view name for filtering drivers by license type.
                    license_map = {
                        1: 'ViewDriverLicenseStudentPermit',
                        2: 'ViewDriverLicenseProfessional',
                        3: 'ViewDriverLicenseNonProfessional',
                    }
                    # Retrieve the view name based on the user's license type choice and validate that it is a valid option.
                    view_name = license_map.get(license_choice)
                    if view_name is None:
                        print('    Invalid option')
                        continue
                    # Call the database controller to retrieve the registered drivers that match the selected license type 
                    # using the corresponding database view, and then display the results to the user in a readable format, 
                    # allowing them to see the details of the drivers that have the specified license type. 
                    # If no matching drivers are found, inform the user accordingly.
                    rows = self.db.show_registered_drivers_by_license_type(view_name)
                    if not rows:
                        print('    No matching drivers found')
                    else:
                        # Display each matching driver record to the user, showing the details of each driver that has the specified license type.
                        for r in self._sort_rows_by_pk(rows):
                            self._display_record(r, title=f"    Driver {r.get('Driver_id')}")
                    break
                continue
            # If the user selects the option to filter registered drivers by license status,
            # the function presents a sub-menu of license statuses, prompts the user to select a status, validates the input,
            # and then retrieves and displays the drivers that match the selected license status from the database.
            if registered_choice_num == 2:
                while True:
                    # Present a sub-menu of license statuses (e.g., valid, expired, suspended, revoked) 
                    # for the user to choose from when filtering registered drivers by license status.
                    self.print_license_status_menu()
                    # Prompt the user to select a license status from the sub-menu and validate the input
                    # to ensure it corresponds to a valid license status choice.
                    status_choice = self.get_menu_choice(4)
                    if status_choice is None:
                        return
                    if status_choice == 0:
                        break
                    # Map the user's license status choice to the corresponding database view name for filtering drivers by license status.
                    status_map = {
                        1: 'ViewDriverLicenseValid',
                        2: 'ViewDriverLicenseExpired',
                        3: 'ViewDriverLicenseSuspended',
                        4: 'ViewDriverLicenseRevoked',
                    }
                    # Retrieve the view name based on the user's license status choice and validate that it is a valid option.
                    view_name = status_map.get(status_choice)
                    if view_name is None:
                        print('    Invalid option')
                        continue
                    # Call the database controller to retrieve the registered drivers that match the selected license status 
                    # using the corresponding database view, and then display the results to the user in a readable format, allowing them to see
                    rows = self.db.show_registered_drivers_by_status(view_name)
                    if not rows:
                        print('    No matching drivers found')
                    else:
                        # Display each matching driver record to the user, showing the details of each driver that has the specified license status.
                        for r in self._sort_rows_by_pk(rows):
                            self._display_record(r, title=f"    Driver {r.get('Driver_id')}")
                    break
                continue
            # If the user selects the option to filter registered drivers by age range, the function prompts the user 
            # to enter a minimum and maximum age, validates that the inputs are integers, and then retrieves and 
            # displays the drivers that fall within the specified age range from the database, allowing the user to see 
            # the details of the drivers that match the age criteria. If no matching drivers are found, inform the user accordingly.
            if registered_choice_num == 3:
                min_age_raw = self.get_user_input('    Minimum age:', True)
                max_age_raw = self.get_user_input('    Maximum age:', True)
                try:
                    min_age = int(min_age_raw)
                    max_age = int(max_age_raw)
                except Exception:
                    print('    Age values must be integers')
                    continue
                # Validate that the maximum age is greater than or equal to the minimum age to ensure a valid age range is provided by the user.
                if max_age < min_age:
                    print('    Maximum age must be greater than or equal to minimum age')
                    continue
                # Call the database controller to retrieve the registered drivers that fall within the specified age range, 
                # and then display the results to the user in a readable format, allowing them to see the details of the drivers 
                # that match the age criteria. If no matching drivers are found, inform the user accordingly.
                rows = self.db.show_driver_age_range(min_age, max_age)
                if not rows:
                    print('    No matching drivers found')
                else:
                    # Display each matching driver record to the user, showing the details of each driver that falls within the specified age range.
                    for r in self._sort_rows_by_pk(rows):
                        self._display_record(r, title=f"    Driver {r.get('Driver_id')}")
                continue
            # If the user selects the option to filter registered drivers by sex, the function presents a sub-menu of sex options (e.g., male, female),
            # prompts the user to select a sex, validates the input, and then retrieves and displays the drivers that match the selected sex from the database, 
            # allowing the user to see the details of the drivers that match the sex criteria. 
            # If no matching drivers are found, inform the user accordingly.
            if registered_choice_num == 4:
                while True:
                    # Present a sub-menu of sex options (e.g., male, female)
                    self.print_sex_menu()
                    # Prompt the user to select a sex from the sub-menu and validate the input to ensure it corresponds to a valid sex choice.
                    sex_choice = self.get_menu_choice(2)
                    if sex_choice is None:
                        return
                    if sex_choice == 0:
                        break
                    # Map the user's sex choice to the corresponding database view name for filtering drivers by sex.
                    sex_map = {
                        1: 'ShowMaleDrivers', 
                        2: 'ShowFemaleDrivers'}
                    # Retrieve the view name based on the user's choice.
                    view_name = sex_map.get(sex_choice)
                    if view_name is None:
                        print('    Invalid option')
                        continue
                    # Call the database controller to retrieve the registered drivers that match the selected sex using the 
                    # corresponding database view, and then display the results to the user in a readable format, 
                    # allowing them to see the details of the drivers that match the sex criteria. 
                    # If no matching drivers are found, inform the user accordingly.
                    rows = self.db.show_registered_drivers_by_sex(view_name)
                    if not rows:
                        print('    No matching drivers found')
                    else:
                        # Display each matching driver record to the user, showing the details of each driver that matches the selected sex.
                        for r in self._sort_rows_by_pk(rows):
                            self._display_record(r, title=f"    Driver {r.get('Driver_id')}")
                    break
                continue

    # This function serves as the main loop for the reports menu, 
    # allowing the user to select from various report options related to drivers and vehicles,
    # and then calls the corresponding functions to execute the selected reports, 
    # displaying the results to the user in a readable format. 
    # The menu continues to loop until the user chooses to exit back to the main menu.
    def _run_reports_menu(self):
        while True:
            # Present a menu of report options
            self.print_reports_menu()
            # Prompt the user to select a report option from the menu and validate the input to ensure it corresponds to a valid report choice.
            report_choice_num = self.get_menu_choice(7)
            if report_choice_num is None or report_choice_num == 0:
                return
            if report_choice_num == 1:
                # This will call the function that handles the sub-menu and logic for driver-related reports based on 
                # license type, status, age range, and sex, allowing the user to further filter and view registered drivers based on those criteria.
                self._run_driver_reports()  
            elif report_choice_num == 2:
                # This will call the function that retrieves and displays the vehicles associated 
                # with a specific driver based on the Driver ID, allowing the user to see the 
                # details of the vehicles registered to that driver.
                self._run_vehicle_by_driver_report()
            elif report_choice_num == 3:
                # This will call the function that retrieves and displays the vehicle registrations 
                # that are expired as of a specified date, allowing the user to see which 
                # vehicle registrations have expired based on the provided date criteria.
                self._run_expired_registrations_report()
            elif report_choice_num == 4:
                # This will call the function that retrieves and displays the licenses that are 
                # either expired or suspended as of a specified date, allowing the user to see 
                # which licenses are not currently valid based on their expiration or suspension 
                # status as of the provided date.
                self._run_expired_or_suspended_licenses_report()
            elif report_choice_num == 5:
                # This will call the function that retrieves and displays the traffic violations 
                # that occurred within a specified date range, allowing the user to see the details 
                # of the violations that took place during that time period based on the provided start and end dates.
                self._run_driver_violations_within_dates_report()
            elif report_choice_num == 6:
                # This will call the function that retrieves and displays the total number of 
                # traffic violations for a specified year, allowing the user to see the violation statistics for that year.
                self._run_total_violations_for_year_report()
            elif report_choice_num == 7:
                # This will call the function that retrieves and displays the traffic violations that 
                # occurred in a specific area, allowing the user to see the details of the violations that took place in that location.
                self._run_vehicle_violation_area_report()

    # Helper functions for displaying report results in a readable format, including sorting rows by primary key, 
    # inferring a title from the primary key, and formatting values for display.
    def _show_report_rows(self, rows, empty_message: str):
        if not rows:
            print(empty_message)
            return
        # Sort the rows by primary key to ensure a consistent and logical order when displaying the report results to the user.
        for row in self._sort_rows_by_pk(rows):
            title = None
            # Attempt to infer a title for the record based on the primary key value, 
            # allowing the user to easily identify the record being displayed in the report results.
            pk = self._infer_pk_key(row)
            if pk:
                title = f"{pk.replace('_', ' ').title()} {row.get(pk)}"
            # Display the record details to the user in a readable format, showing the information 
            # for each record in the report results along with the inferred title if available.
            self._display_record(row, title=title)

    # This function is responsible for displaying a report in a tabular format, 
    # allowing the user to see the results of the report in a structured and organized way.
    def _display_report_table(self, rows, columns=None, headers=None, empty_message: str = '    No records found'):
        if not rows:
            print(empty_message)
            return
        rows = self._sort_rows_by_pk(rows)
        if columns is None:
            columns = list(rows[0].keys())
        if headers is None:
            headers = [col.replace('_', ' ').title() for col in columns]
        # Determine the maximum width for each column based on the header and the longest value in that column across all rows,
        # while also considering the overall terminal width to ensure the table fits within the display area,
        # and if necessary, reduce the column widths proportionally to fit the table within the terminal width, 
        # ensuring that the displayed report is readable and well-formatted for the user.
        term_width = shutil.get_terminal_size(fallback=(100, 30)).columns
        widths = {}
        for col in columns:
            max_width = len(str(col))
            for row in rows:
                value = row.get(col)
                if value is None:
                    value = ''
                else:
                    value = str(self._fmt_date(value) if 'date' in col.lower() or 'birth' in col.lower()
                                else self._fmt_currency(value) if 'fine' in col.lower() or 'amount' in col.lower()
                                else self._fmt_enum(value) if col.lower() in ('registration_status', 'license_status', 'license_type', 'ownership_type', 'vehicle_type', 'sex_assigned_at_birth', 'civil_status') or col.lower().endswith('_type')
                                else value)
                max_width = max(max_width, len(value))
            widths[col] = min(max_width, 28)
        # Calculate the total width of the table based on the column widths and the spacing between columns,
        # and if the total width exceeds the terminal width, reduce the column widths proportionally until the table 
        # fits within the terminal width, ensuring that the displayed report is readable and well-formatted for the user.
        total_width = sum(widths.values()) + (3 * (len(columns) - 1))
        if total_width > term_width:
            overflow = total_width - term_width
            reduce_cols = [c for c in columns if widths[c] > 10]
            while overflow > 0 and reduce_cols:
                changed = False
                for c in list(reduce_cols):
                    if widths[c] > 10 and overflow > 0:
                        widths[c] -= 1
                        overflow -= 1
                        changed = True
                reduce_cols = [c for c in columns if widths[c] > 10]
                if not changed:
                    break

        # Helper function to format values for display based on the column type, such as formatting dates, currency, 
        # and enumerated types for better readability in the report output.
        def format_value(col, value):
            if value is None:
                value = ''
            if 'date' in col.lower() or 'birth' in col.lower():
                value = self._fmt_date(value)
            elif 'fine' in col.lower() or 'amount' in col.lower():
                value = self._fmt_currency(value)
            elif col.lower() in ('registration_status', 'license_status', 'license_type', 'ownership_type', 'vehicle_type', 'sex_assigned_at_birth', 'civil_status') or col.lower().endswith('_type'):
                value = self._fmt_enum(value)
            return '' if value is None else str(value)

        # Helper function to truncate text that exceeds the specified width, adding an ellipsis to indicate truncation.
        def clip_value(text: str, width: int) -> str:
            if len(text) <= width:
                return text
            if width <= 3:
                return text[:width]
            return text[:width - 3] + '...'
        
        # Print the report table with headers and rows formatted according to the calculated column widths, 
        # ensuring that the output is organized and easy to read for the user, and includes separators for better visual clarity.
        print('\n' + '-' * min(term_width, max(60, total_width)))
        header = ' | '.join(f"{headers[idx]:<{widths[col]}}" for idx, col in enumerate(columns))
        print(header)
        print('-' * min(term_width, max(60, total_width)))
        for row in rows:
            parts = []
            for col in columns:
                text = clip_value(format_value(col, row.get(col)), widths[col])
                parts.append(f"{text:<{widths[col]}}")
            print(' | '.join(parts))
        print('-' * min(term_width, max(60, total_width)))

    # This function retrieves and displays the vehicles associated with a specific driver based on the Driver ID,
    # allowing the user to see the details of the vehicles registered to that driver.
    def _run_vehicle_by_driver_report(self):
        # Require Driver ID for precise lookup of associated vehicle records.
        driver_id_raw = self.get_user_input('    Driver ID:', True)
        if driver_id_raw is None:
            return
        try:
            driver_id = int(driver_id_raw)
        except Exception:
            print('    Driver ID must be integer')
            return
        # Call the database controller to retrieve and display the vehicles associated with the specified Driver ID,
        # allowing the user to see the details of the vehicles registered to that driver.
        rows = self.db.show_driver_vehicles(driver_id)
        if not rows:
            print('    No vehicles found')
            return
        # Sort the retrieved vehicle records by their primary key to ensure a consistent and logical order 
        # when displaying the report results to the user, and then display each vehicle record with a 
        # title that includes the Vehicle ID for easy identification of each vehicle in the report output.
        for row in self._sort_rows_by_pk(rows):
            vehicle_id = row.get('Vehicle_id')
            self._display_record(row, title=f"    Vehicle {vehicle_id}")

    # This function retrieves and displays the vehicle registrations that are expired as of a specified date, 
    # allowing the user to see which vehicle registrations have expired based on the provided date criteria.
    def _run_expired_registrations_report(self):
        # Prompt the user to enter an "as of" date in the format YYYY-MM-DD, which will be used as the 
        # reference date to determine which vehicle registrations are considered expired.
        as_of_date = self.get_user_input('    As of date (YYYY-MM-DD):', True)
        if validate_date(as_of_date) is None:
            print('    Invalid date format')
            return
        rows = self.db.get_expired_registrations(as_of_date)
        # Display the expired vehicle registrations in a tabular format with specific columns and headers, 
        # allowing the user to see the details of each expired registration, and if no expired registrations 
        # are found, inform the user accordingly.
        self._display_report_table(
            rows,
            columns=['Vehicle_id', 'Plate_number', 'Make', 'Model', 'Registration_number', 'Expiration_date', 'Registration_status'],
            headers=['Vehicle ID', 'Plate Number', 'Make', 'Model', 'Registration Number', 'Expiration Date', 'Registration Status'],
            empty_message='    No expired registrations found'
        )

    # This function retrieves and displays the licenses that are expired or suspended,
    # allowing the user to see the details of such licenses.
    def _run_expired_or_suspended_licenses_report(self):
        # Call the database controller to retrieve and display the licenses that are either expired or suspended,
        # allowing the user to see the details of such licenses, and if no expired or suspended licenses are found, inform the user accordingly.
        rows = self.db.show_expired_or_suspended_licenses()
        # Display the expired or suspended licenses in a tabular format with specific columns and headers,
        # allowing the user to see the details of each license, and if no expired or suspended licenses are found, inform the user accordingly.
        self._show_report_rows(rows, '    No expired or suspended licenses found')

    # This function retrieves and displays traffic violations for a specific driver within a date range,
    # allowing the user to analyze the driver's violation history.
    def _run_driver_violations_within_dates_report(self):
        # Require Driver ID for precise lookup of associated violation records.
        driver_id_raw = self.get_user_input('    Driver ID:', True)
        if driver_id_raw is None:
            return
        try:
            driver_id = int(driver_id_raw)
        except Exception:
            print('    Driver ID must be integer')
            return
        # Prompt the user to enter a start date and an end date in the format YYYY-MM-DD, 
        # which will be used to filter the traffic violations for the specified driver within that date range, 
        # and validate that the entered dates are in the correct format.
        start_date = self.get_user_input('    Start date (YYYY-MM-DD):', True)
        if validate_date(start_date) is None:
            print('    Invalid date format')
            return
        # Prompt the user to enter an end date in the format YYYY-MM-DD, 
        # which will be used as the upper bound of the date range for filtering traffic violations,
        # and validate that the entered end date is in the correct format to ensure accurate filtering 
        # of violations based on the specified date range.
        end_date = self.get_user_input('    End date (YYYY-MM-DD):', True)
        if validate_date(end_date) is None:
            print('    Invalid date format')
            return
        # Call the database controller to retrieve and display the traffic violations for the 
        # specified driver that occurred within the provided date range, allowing the user to 
        # analyze the driver's violation history based on the specified criteria, 
        # and if no violations are found for that driver within the date range, inform the user accordingly.
        rows = self.db.show_driver_traffic_violations_within_dates(
            driver_id,  # Driver_id     (Foreign key to Drivers table)
            start_date, # Start date    (YYYY-MM-DD)
            end_date)   # End date      (YYYY-MM-DD)
        # Display the traffic violations in a readable format, showing the details of each violation 
        # for the specified driver within the date range, and if no violations are found, inform the user accordingly.
        self._show_report_rows(rows, '    No violations found')

    # This function retrieves and displays the total number of traffic violations for a specified year,
    # allowing the user to see the violation statistics for that year.
    def _run_total_violations_for_year_report(self):
        # Prompt the user to enter a year in the format YYYY, which will be used to filter and retrieve the 
        # total number of traffic violations that occurred during that year, and validate that the entered year is an integer.
        year_raw = self.get_user_input('    Year (YYYY):', True)
        try:
            year = int(year_raw)
        except Exception:
            print('    Year must be integer')
            return
        # Call the database controller to retrieve and display the total number of traffic violations 
        # for the specified year, allowing the user to see the violation statistics for that year, 
        # and if no violation counts are found for that year, inform the user accordingly.
        rows = self.db.view_total_violations_for_given_year(year)
        if not rows:
            print('    No violation counts found for that year')
            return
        # Display the total violation counts in a tabular format with specific columns and headers, 
        # allowing the user to see the details of the violation statistics for that year, 
        # and if no violation counts are found for that year, inform the user accordingly.
        self._display_report_table(
            rows,
            columns=['Violation_Type', 'Total_Count', 'Total_Fines_Collected'],
            headers=['Violation Type', 'Total Count', 'Total Fines Collected'],
            empty_message='    No violation counts found for that year'
        )

    # This function retrieves and displays the traffic violations that occurred in a specific area,
    # allowing the user to see the details of the violations that took place in that location.
    def _run_vehicle_violation_area_report(self):
        while True:
            # Present a sub-menu of area options (e.g., city, region) for the user to choose from when filtering traffic violations by area.
            self.print_vehicle_violation_area_menu()
            # Prompt the user to select an area type from the sub-menu and validate the input to ensure it corresponds to a valid area choice.
            area_choice = self.get_menu_choice(2)
            if area_choice is None or area_choice == 0:
                return
            if area_choice == 1:
                # Prompt the user to enter a city name, which will be used to filter and retrieve the traffic 
                # violations that occurred in that specific city, and validate that the input is not empty.
                city = self.get_user_input('    City:', True)
                if not city:
                    continue
                # Call the database controller to retrieve and display the traffic violations that occurred in the specified city,
                # allowing the user to see the details of the violations that took place in that location, 
                # and if no violations are found for that city, inform the user accordingly.
                rows = self.db.show_vehicle_violation_city(city)
                # Display the traffic violations in a readable format, showing the details of each violation for the specified city,
                # and if no violations are found for that city, inform the user accordingly.
                self._show_report_rows(rows, '    No vehicle violations found for that city')
                return
            if area_choice == 2:
                # Prompt the user to enter a region name, which will be used to filter 
                # and retrieve the traffic violations that occurred in that specific region,
                # and validate that the input is not empty.
                region = self.get_user_input('    Region:', True)
                if not region:
                    continue
                # Call the database controller to retrieve and display the traffic violations that occurred in the specified region,
                # allowing the user to see the details of the violations that took place in that location,
                # and if no violations are found for that region, inform the user accordingly.
                rows = self.db.show_vehicle_violation_region(region)
                # Display the traffic violations in a readable format, showing the details of each violation for the specified region,
                # and if no violations are found for that region, inform the user accordingly.
                self._show_report_rows(rows, '    No vehicle violations found for that region')
                return

    # This function serves as the main entry point for the console application, 
    # presenting the main menu to the user and handling their menu choices 
    # to navigate through different management and reporting functionalities 
    # related to drivers, vehicles, registrations, and traffic violations.
    def start(self):
        while True:
            # Display the main menu to the user, allowing them to choose from various management 
            # and reporting options related to drivers, vehicles, registrations, and traffic violations.
            self.print_main_menu()
            c = self.get_menu_choice(5)
            if c is None:
                print('Canceled')
                continue

            # ==========================================================================================================================================
            # DRIVER MANAGEMENT 
            if c == 1:
                self.print_driver_menu()
                s = self.get_menu_choice(6)
                if s is None:
                    continue
                if s == 1:
                    # This calls the function that handles the flow for adding a new driver, 
                    # allowing the user to input the necessary details and save the new driver record to the database.
                    self.add_driver()
                elif s == 2:
                    # This calls the function that handles the flow for updating an existing driver's information,
                    # allowing the user to modify the details of a driver record in the database based on their input.
                    self.update_driver_flow()
                elif s == 3:
                    # This calls the function that handles the flow for deleting a driver record from the database,
                    # allowing the user to remove a driver from the system based on their input.
                    self.delete_driver_flow()
                elif s == 5:
                    # This calls the function that handles the flow for adding a new license for a driver, allowing the 
                    # user to input the necessary details and save the new license record to the database for a specific driver.
                    self.add_license_flow()
                elif s == 6:
                    # This calls the function that handles the flow for updating an existing driver's license information, 
                    # allowing the user to modify the details of a license record in the database based on their input.
                    self.update_license_flow()
                elif s == 4:
                    # SEARCH DRIVER RECORDS: Shows a search sub-menu then require Driver ID
                    # This option allows the user to search for driver records based on a specific Driver ID, 
                    # and then choose to view either the associated vehicles, license information, or traffic violations for that driver, 
                    # providing a way to access detailed information about the driver based on their unique identifier.
                    self.print_driver_search_menu()
                    # Prompt the user to select a search option from the sub-menu 
                    # and validate the input to ensure it corresponds to a valid search choice.
                    sub = self.get_menu_choice(3)
                    if sub is None:
                        continue
                    if sub == 0:
                        continue
                    # Prompt the user to enter a Driver ID, which will be used to search for the corresponding 
                    # driver record in the database, and validate that the input is an integer to ensure accurate retrieval 
                    # of the driver information based on the provided Driver ID, allowing the user to access the details 
                    # of the driver and their associated records such as vehicles, license information, or traffic violations.
                    did_raw = self.get_user_input('    Driver ID (required):', True)
                    if did_raw is None:
                        continue
                    try:
                        did = int(did_raw)
                    except ValueError:
                        print('    Invalid Driver ID')
                        continue
                    # Based on the user's search choice, retrieve and display the relevant information for the specified Driver ID,
                    # allowing the user to see either the associated vehicles, license information, or traffic violations for that driver,
                    # and if no records are found for the selected category, inform the user accordingly.
                    if sub == 1:
                        rows = self.db.show_driver_vehicles(did)
                        if not rows:
                            print('    No vehicles found')
                        else:
                            # Define the set of vehicle fields to display for better readability, and then display each 
                            # associated vehicle record for the specified Driver ID, showing the details of each vehicle 
                            # in a readable format, and if no vehicles are found for that driver, inform the user accordingly.
                            vehicle_fields = {
                                'Vehicle_id', 
                                'Engine_number', 
                                'Plate_number', 
                                'Chassis_number',
                                'Vehicle_type', 
                                'Make', 
                                'Model', 
                                'Year', 
                                'Body_type', 
                                'Capacity', 
                                'Color'
                            }
                            for r in rows:
                                vehicle_only = {k: v for k, v in r.items() if k in vehicle_fields}
                                self._display_record(vehicle_only, title=f"    Vehicle {r.get('Vehicle_id')}")
                    # If the user selects the option to show only license information for the specified Driver ID, 
                    # the function retrieves and displays the license details for that driver from the database, 
                    # allowing the user to see the relevant license information in a readable format, 
                    # and if no license information is found for that driver, inform the user accordingly.
                    elif sub == 2:
                        # Calls the ShowDriverLicense stored procedure to retrieve the license information for the specified Driver ID,
                        # and then displays the license details in a readable format, allowing the user to see the
                        # relevant license information for that driver, and if no license information is found, inform the user accordingly.
                        rows = self.db.call_proc('ShowDriverLicense', [did])
                        if not rows:
                            print('    No license information found')
                        else:
                            for r in rows:
                                self._display_record(r, title='    Driver License Info')
                    # If the user selects the option to show only traffic violations for the specified Driver ID,
                    # the function retrieves and displays the traffic violation records associated with that driver from the database,
                    # allowing the user to see the details of the violations in a readable format, 
                    # and if no violations are found for that driver, inform the user accordingly.
                    elif sub == 3:
                        try:
                            # Calls the ShowTrafficViolations stored procedure to retrieve the traffic violation records 
                            # for the specified Driver ID, and then displays the violation details in a readable format, 
                            # allowing the user to see the details of the violations associated with that driver, 
                            # and if no violations are found, inform the user accordingly.
                            rows = self.db.call_proc('ShowTrafficViolations', [did])
                        except Exception:
                            rows = None
                        if not rows:
                            print('    No violations found or feature not available')
                        else:
                            # Sort the retrieved violation records by their primary key to ensure a consistent and logical order 
                            # when displaying the report results to the user, and then display each violation record with a title 
                            # that includes the inferred primary key value for easy identification of each violation in the report output.
                            for r in rows:
                                self._display_record(r, title=f"    Violation {r.get(self._infer_pk_key(r))}")

            # ==========================================================================================================================================
            # VEHICLE MANAGEMENT
            elif c == 2:
                # Display the vehicle management menu to the user.
                self.print_vehicle_menu()
                # Prompt the user to select an option from the vehicle management menu 
                # and validate the input to ensure it corresponds to a valid choice.
                s = self.get_menu_choice(4)
                if s is None:
                    continue
                if s == 1:
                    # This calls the function that handles the flow for adding a new vehicle, 
                    # allowing the user to input the necessary details and save the new vehicle record to the database.
                    self.add_vehicle()
                elif s == 2:
                    # This calls the function that handles the flow for updating an existing vehicle's information,
                    # allowing the user to modify the details of a vehicle record in the database based on their input.
                    self.update_vehicle_flow()
                elif s == 3:
                    # This calls the function that handles the flow for deleting a vehicle record from the database,
                    # allowing the user to remove a vehicle from the system based on their input.
                    self.delete_vehicle_flow()
                elif s == 4:
                    # Search Vehicle Records: show search sub-menu then require Vehicle ID
                    self.print_vehicle_search_menu()
                    # Prompt the user to select a search option from the sub-menu.
                    sub = self.get_menu_choice(3)
                    if sub is None:
                        continue
                    if sub == 0:
                        continue
                    # Prompt the user to enter a Vehicle ID, which will be used to search for the corresponding vehicle record in the database, 
                    # and validate that the input is an integer to ensure accurate retrieval of the vehicle information based on the provided 
                    # Vehicle ID, allowing the user to access the details of the vehicle and its associated records such as owner information, 
                    # registration details, or traffic violations.
                    vid_raw = self.get_user_input('Vehicle ID (required):', True)
                    if vid_raw is None:
                        continue
                    try:
                        vid = int(vid_raw)
                    except ValueError:
                        print('Invalid Vehicle ID')
                        continue
                    # Based on the user's search choice, retrieve and display the relevant information for the specified Vehicle ID, 
                    # allowing the user to see either the associated owner information, registration details, or traffic violations for that vehicle, 
                    # and if no records are found for the selected category, inform the user accordingly.
                    if sub == 1:
                        rows = self.db.call_proc('ShowVehicleOwner', [vid])
                        if not rows:
                            print('No vehicle owner found')
                        else:
                            for r in rows:
                                self._display_record(r, title='Vehicle owner')
                    elif sub == 2:
                        rows = self.db.show_vehicle_registrations(vid)
                        if not rows:
                            print('No registrations found')
                        else:
                            for r in rows:
                                self._display_record(r, title=f"Registration {r.get('Registration_number')}")
                    elif sub == 3:
                        rows = self.db.call_proc('ShowVehicleTrafficViolations', [vid])
                        if not rows:
                            print('No associated traffic violations found')
                        else:
                            for r in rows:
                                self._display_record(r, title=f"Violation {r.get('Violation_id')}")

            # ==========================================================================================================================================
            # VEHICLE REGISTRATION MANAGEMNET
            elif c == 3:
                # Display the vehicle registration management menu to the user.
                self.print_registration_menu()
                # Prompt the user to select an option from the vehicle registration management menu.
                s = self.get_menu_choice(4)
                if s is None:
                    continue
                if s == 1:
                    # This calls the function that handles the flow for adding a new vehicle registration, 
                    # allowing the user to input the necessary details and save the new registration record 
                    # to the database for a specific vehicle.
                    self.add_vehicle_registration()
                elif s == 2:
                    # This calls the function that handles the flow for renewing an existing vehicle registration, 
                    # allowing the user to update the registration details and extend the registration period for a specific vehicle.
                    self.renew_vehicle_registration()
                elif s == 3:
                    # This calls the function that handles the flow for updating an existing vehicle registration's information,
                    # allowing the user to modify the details of a registration record in the database based on their input.
                    self.update_vehicle_registration_flow()
                elif s == 4:
                    # This calls the function that handles the flow for deleting a vehicle registration record from the database,
                    # allowing the user to remove a vehicle registration from the system based on their input.
                    self.delete_vehicle_registration_flow()

            # ==========================================================================================================================================
            # TRAFFIC VIOLATION MANAGEMENT
            elif c == 4:
                # Display the traffic violation management menu to the user.
                self.print_violation_menu()
                # Prompt the user to select an option from the traffic violation management menu.
                s = self.get_menu_choice(3)
                if s is None:
                    continue
                if s == 1:
                    # This calls the function that handles the flow for adding a new traffic violation,
                    # allowing the user to input the necessary details and save the new violation record to the database.
                    self.add_violation_flow()
                elif s == 2:
                    # This calls the function that handles the flow for updating an existing traffic violation's information,
                    # allowing the user to modify the details of a violation record in the database based on their input.
                    self.update_violation_flow()
                elif s == 3:
                    # This calls the function that handles the flow for deleting a traffic violation record from the database,
                    # allowing the user to remove a traffic violation from the system based on their input.
                    self.delete_violation_flow()

            # ==========================================================================================================================================
            # GENERATE REPORTS
            elif c == 5:
                # This calls the function that handles the flow for generating various reports based on user-selected criteria,
                # allowing the user to access different types of reports related to drivers, vehicles, registrations, 
                # and traffic violations, and if the user selects the option to generate reports, they will be presented 
                # with a sub-menu of report options to choose from, and based on their selection, the corresponding report 
                # generation function will be called to retrieve and display the report results to the user.
                self._run_reports_menu()

            # ==========================================================================================================================================
            # EXIT
            elif c == 0:
                print('    Goodbye')
                return

            # ==========================================================================================================================================            
            else:
                print('    Invalid option')
