import socket
# Socket's Listeners
from taskcontrol.lib import SocketsBase


Socket = SocketsBase()


def server_handler(conn, addr, socket_server):
    print("SERVER", conn, addr)
    while True:
        data = conn.recv(1024).decode()
        if data:
            print("Data \n", data)
            if data == "close":
                conn.close()
            else:
                conn.send("close".encode())
        break
    conn.close()
    print("SERVER ", socket_server.get("host"), socket_server.get("port"))
    # print(socket_server.get("server").close())


config = {"name": "test", "protocol": socket.AF_INET, "streammode": socket.SOCK_STREAM,
          "host": "127.0.0.1", "port": 9001, "numbers": 1, "handler": server_handler, "close_server": True}

# METHOD ONE:
s = Socket.socket_create(config)
if s:
    print("Server started")
    sr = Socket.socket_listen(config.get("name"))

# @DCMysuru @CPMysuru @CPBlr 
# Gokulam, Mysore is sounding like a prostitution, mourning center w/ women shouting since last 15 years& no action has been taken.
# Any complaints have led to threats or coersive closure of complaints. Looks like environmental apart from legal lapse
