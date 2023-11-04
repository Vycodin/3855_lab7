import mysql.connector
db_conn = mysql.connector.connect(host="ky-3855.westus3.cloudapp.azure.com", user="conflict_user", password="conflict_password", database="conflict_db")

db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE reported_conflicts, upload_operation
''')
db_conn.commit()
db_conn.close()