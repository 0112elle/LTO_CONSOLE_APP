import sys      # For exiting on connection failure
import pymysql  # For MariaDB/MySQL connectivity

class MariaDBInstance:
    
    # For simplicity, we use a single cursor. In a more complex app, you might want to manage multiple cursors or use connection pooling.
    def __init__(self, user: str, password: str, database: str, host: str = "127.0.0.1", port: int = 3306):
        try:
            self.conn = pymysql.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.Error as e:
            print(f"Error connecting to MariaDB: {e}")
            sys.exit(1)
        self.cursor = self.conn.cursor()

    # Helper method to get the cursor, if needed for direct queries.
    def cur(self):
        return self.cursor

    # Helper method to execute a stored procedure and fetch results.
    def callproc(self, proc_name, params=None):
        if params is None:
            params = []
        try:
            self.cursor.callproc(proc_name, params)
            # Some procedures return result sets; fetch them
            result = self.cursor.fetchall()
            # advance to next result to clear
            try:
                while self.cursor.nextset():
                    pass
            except Exception:
                pass
            self.conn.commit()
            return result
        except pymysql.Error as e:
            print(f"Stored procedure error: {e}")
            return None

    # Helper method to execute a query with parameters and fetch results.
    def query(self, sql, params=None):
        if params is None:
            params = []
        try:
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
            self.conn.commit()
            return result
        except pymysql.Error as e:
            print(f"Query error: {e}")
            return None

    # Helper method to execute a query without fetching results (e.g., for INSERT/UPDATE).
    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass
