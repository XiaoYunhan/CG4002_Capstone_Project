from comm_external.multiple_server import Server
from comm_external.DB_Client import connect

def main():
    socket_server= Server("127.0.0.1", 8080, 7)
    socket_server.start()
    connect()

if __name__ == '__main__':
    main()