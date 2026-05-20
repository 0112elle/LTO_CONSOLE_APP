from sql.sql_connector import MariaDBInstance
from controller.db_controller import DBController
from view.ui import UserInterface

def main():
    print('Starting LTO Console App')
    # Adjust credentials as needed
    db = MariaDBInstance(user='ltodirector', password='lto', database='lto', host='127.0.0.1', port=3306)
    ctrl = DBController(db)
    ui = UserInterface(ctrl)
    try:
        ui.start()
    finally:
        ctrl.close()

if __name__ == '__main__':
    main()
