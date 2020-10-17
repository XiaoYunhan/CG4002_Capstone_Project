from comm_external.multiple_server import Server
# from comm_external.DB_Client import connect

def main():

    #""" decleration and initialization """
    socket_server= Server("127.0.0.1", 8080, 7)
    socket_server.start()
    # connect()
    #while True:
     #   print(socket_server.raw_data)
      #  print(socket_server.RTT)

     #   """ raw data processing """

      #  """ machine learning """

       # """ send data to aws database """

if __name__ == '__main__':
    main()
