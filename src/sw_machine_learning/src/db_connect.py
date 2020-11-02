import psycopg2

from comm_external.multiple_server import ACTIONS

RDS_HOSTNAME = "localhost"
RDS_USERNAME = "b07admin"
RDS_PASSWORD = "password"
RDS_DATABASE = "justdance"
RDS_PORT = 3306
flag = False
date = "2020-10-27"
dance_move = "0"
left_time = "21:03:30.204"
left_dancer = "0"
center_time = "21:03:45.304"
center_dancer = "0"
right_time = "21:03:45.304"
right_dancer = "0"
diff_in_timing = "0"
sync = "Yes"

def db_connect(self, queue):
    

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

    while True:
        if not queue.empty():
            cmd = queue.get()
            if cmd == "Start":
                insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ cmd +"'"+ "," +"'"+left_time +"'"+ "," + "1" + "," +"'"+ center_time +"'"+ "," + "2" + "," +"'"+ right_time +"'"+ "," + "3" + "," + diff_in_timing + "," + "'" + sync + "')"
            else:
                for i in range(3):
                    if cmd[i][0] != -1:
                        if cmd[i][0] == 8:
                            insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ "End" +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
                        else:
                            insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ ACTIONS[cmd[i][0]] +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
                        flag = True
                        break
                if not flag:
                    insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ str(cmd[0][0]) +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
                    flag = False
            cursor.execute(insertDanceDataQuery)

    