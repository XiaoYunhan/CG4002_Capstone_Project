import psycopg2
import logging

from comm_external.multiple_server import ACTIONS

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

def db_connect(queue):

    RDS_HOSTNAME = "localhost"
    RDS_USERNAME = "b07admin"
    RDS_PASSWORD = "password"
    RDS_DATABASE = "justdance"
    RDS_PORT = 3306
    is_pos = False
    to_commit = False
    date = "2020-11-03"
    dance_move = "0"
    left_time = "21:03:30.204"
    left_dancer = "0"
    center_time = "21:03:45.304"
    center_dancer = "0"
    right_time = "21:03:45.304"
    right_dancer = "0"
    diff_in_timing = "0"
    sync = "Yes"
    insertDanceDataQuery = "NAN"

#def db_connect(queue):
#    is_pos = False   

    connection = psycopg2.connect(user = RDS_USERNAME,
                                password = RDS_PASSWORD,
                                host = RDS_HOSTNAME,
                                port = RDS_PORT,
                                database = RDS_DATABASE)
    connection.autocommit = True
    cursor = connection.cursor()
    logging.info ( connection.get_dsn_parameters())
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    #conn_msg = "You are connected to - " + record + "\n"
    #logging.info(conn_msg)

    while True:
        if not queue.empty():
            cmd = queue.get()
            logging.info(cmd)
            if cmd == "Start":
                insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ cmd +"'"+ "," +"'"+left_time +"'"+ "," + "1" + "," +"'"+ center_time +"'"+ "," + "2" + "," +"'"+ right_time +"'"+ "," + "3" + "," + diff_in_timing + "," + "'" + sync + "')"
                to_commit = True
            else:
                for i in range(3):
                    if cmd[i][0] != -1:
                        #if cmd[i][0] == 8:
                         #   insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ "End" +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
                         #   to_commit = True
                        #else:
                        insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ ACTIONS[cmd[i][0]] +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
                        is_pos = True
                        to_commit = True
                        break
                if is_pos:
                    insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ str(cmd[0][0]) +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
                    is_pos = False
                    to_commit = True
            if to_commit:
                cursor.execute(insertDanceDataQuery)
                to_commit = False

    
