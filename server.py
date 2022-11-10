from socket import * # to manage connection
import threading # to manage sequence


serverHost = "127.0.0.1" #listening at
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((serverHost,serverPort))
serverSocket.listen(5) # max queue for connection


clientSockets = [] # stores all client connections
users = [] # stores all usernames of clients



# broadcast message to all clients connected to the server
def broadcast(msg, source):
     # handle message source and destination
     msgString = msg.decode('ascii')
     msgBody = msgString.split(":")
     username = ''
     data = ''
     mention = ''
     if len(msgBody) > 1:
          username = msgBody[0]
          data = msgBody[1][1:]
     if len(data) < 1:
          return
     else:
          mention = data[0]
     if mention == '@':
          msgList = data.split(' ')
          destination = msgList[0][1:]
          msgList.pop(0)
          targetedMsg = ' '.join(msgList)
          unicast(targetedMsg, username, destination)
     else:
          for clientSocket in clientSockets:
               if source != clientSocket:
                    clientSocket.send(msg)


# handles mentions or one-to-one messages
def unicast(msg, source, destination):
     try:
          i = users.index(destination)
          # for clientSocket in clientSockets:
          #      if source != clientSocket:
          clientSockets[i].send((source+': '+msg).encode('ascii'))
     except:
          i = users.index(source)
          clientSockets[i].send(('Error: client has left').encode('ascii'))
          return
          

# handle when receiving message from client
def handleMessage(client):
     while True:
          try:
               # send message to all clients
              msg = client.recv(1024)
              broadcast(msg, client)
          except:
               # when connection is lost, remove client
               i = clientSockets.index(client)
               clientSockets.remove(client)
               client.close()
               # remove username also
               username = users[i]
               broadcast('\n{} left!'.format(username).encode('ascii'))
               users.remove(username)
               break



# handle when new client connects to the server
def receiveClientConnection():
     print ('The server is ready to receive...')
     while True:
          connectionSocket, addr = serverSocket.accept()
          print("{} has connected!".format(str(addr)))
          connectionSocket.send("username".encode())
          username = connectionSocket.recv(1024).decode("ascii")
          users.append(username)
          clientSockets.append(connectionSocket)
          broadcast(f"{username} has joined!\n".encode("ascii"), connectionSocket)

          # handle client individually at the same time
          thread = threading.Thread(target=handleMessage, args=(connectionSocket,))
          thread.start()



receiveClientConnection()
