import psycopg2

"""
run this command before connection:
ssh -NfL 3306:b07-dancedashboard.cx4zc3f2utdt.ap-southeast-1.rds.amazonaws.com:5432 -i ~/Downloads/ssh_tunnel.pem ec2-user@ec2-54-169-67-0.ap-southeast-1.compute.amazonaws.com
"""

def connect(date, dance_move, left_time, left_dancer, center_time, center_dancer, right_time, right_dancer, diff_in_timing, sync):
# def connect():
    """ Connect to the PostgreSQL database server """
    RDS_HOSTNAME = "localhost"
    # RDS_HOSTNAME = "b07-dancedashboard.cx4zc3f2utdt.ap-southeast-1.rds.amazonaws.com"
    RDS_USERNAME = "b07admin"
    RDS_PASSWORD = "password"
    RDS_DATABASE = "justdance"
    RDS_PORT = 3306

    try:
        connection = psycopg2.connect(user = RDS_USERNAME, 
                                    password = RDS_PASSWORD, 
                                    host = RDS_HOSTNAME, 
                                    port = RDS_PORT, 
                                    database = RDS_DATABASE)
        connection.autocommit = True
        cursor = connection.cursor()
        print ( connection.get_dsn_parameters(),"\n")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ dance_move +"'"+ "," +"'"+left_time +"'"+ "," + left_dancer + "," +"'"+ center_time +"'"+ "," + center_dancer + "," +"'"+ right_time +"'"+ "," + right_dancer + "," + diff_in_timing + "," + "'" + sync + "')"
        # record_to_insert = ()
        print(insertDanceDataQuery)
        cursor.execute(insertDanceDataQuery)
        print("inserted")
        
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == '__main__':
    connect("2020-10-27", "rocket", "21:03:30.204", "1", "21:03:45.304", "2", "21:02:30.998", "3" , "15.100", "No")
    # connect("2020-10-27", "rocket", "NULL", "1", "NULL", "2", "NULL", "3" , "15.100", "No")
    # connect()