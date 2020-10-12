# import pg
import psycopg2

def connect():
    """ Connect to the PostgreSQL database server """
    RDS_HOSTNAME = "localhost"
    # RDS_HOSTNAME = "b07-dancedashboard.cx4zc3f2utdt.ap-southeast-1.rds.amazonaws.com"
    RDS_USERNAME = "b07admin"
    RDS_PASSWORD = "password"
    RDS_DATABASE = "justdance"
    RDS_PORT = 5432
    try:
        connection = psycopg2.connect(user = RDS_USERNAME, 
                                    password = RDS_PASSWORD, 
                                    host = RDS_HOSTNAME, 
                                    port = RDS_PORT, 
                                    database = RDS_DATABASE)
        cursor = connection.cursor()
        print ( connection.get_dsn_parameters(),"\n")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
        
        # conn = pg.DB(host = RDS_HOSTNAME, user = RDS_USERNAME, passwd = RDS_PASSWORD, dbname = RDS_DATABASE, port = RDS_PORT)
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == '__main__':
    connect()