import mysql.connector

conn = mysql.connector.connect(host="ky-3855.westus3.cloudapp.azure.com", user="conflict_user", password="conflict_password", database="conflict_db")


c = conn.cursor()
c.execute('''
          CREATE TABLE reported_conflicts
          (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
          node_id VARCHAR(250) NOT NULL,
          blu_numbers INT NOT NULL,
          op_numbers INT NOT NULL,
          planet_id VARCHAR(100) NOT NULL,
          system_id VARCHAR(100) NOT NULL,
          timestamp VARCHAR(100) NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          trace_id INTEGER NOT NULL)
          ''')

c.execute('''
          CREATE TABLE upload_operation
          (id INT PRIMARY KEY AUTO_INCREMENT,
          operation_id VARCHAR(250) NOT NULL,
          planet_id VARCHAR(100) NOT NULL,
          system_id VARCHAR(100) NOT NULL,
          op_type VARCHAR(100) NOT NULL,
          blu_ships INT NOT NULL,
          op_ships INT NOT NULL,
          timestamp VARCHAR(100) NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          trace_id INTEGER NOT NULL)
          ''')

conn.commit()
conn.close()