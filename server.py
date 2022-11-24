import rsa
from socket import * # to manage connection
import threading # to manage sequence

# generate encryption keys
publicKey, privateKey = rsa.newkeys(1024)
clientPublicKey = None

serverHost = "127.0.0.1" #listening at
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((serverHost,serverPort))
serverSocket.listen(5) # max queue for connection


clientSockets = [] # stores all client connections
users = [] # stores all usernames of clients
clientsPublicKeys = []



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
          index = 0
          for clientSocket in clientSockets:
               if source != clientSocket:
                    clientSocket.send(rsa.encrypt(msg, clientsPublicKeys[index]))
               index+=1
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
          index = 0
          for clientSocket in clientSockets:
               if source != clientSocket:
                    clientSocket.send(rsa.encrypt(msg, clientsPublicKeys[index]))
               index+=1


# handles mentions or one-to-one messages
def unicast(msg, source, destination):
     try:
          i = users.index(destination)
          clientSockets[i].send(rsa.encrypt((source+': '+msg).encode('ascii'), clientsPublicKeys[i]))
     except:
          i = users.index(source)
          clientSockets[i].send(rsa.encrypt( ('client has left').encode('ascii'), clientsPublicKeys[i]))
          return
          

# handle when receiving message from client
def handleMessage(client):
     while True:
          try:
               # send message to all clients
              msg = rsa.decrypt(client.recv(1024), privateKey)
              broadcast(msg, client)
          except:
               # when connection is lost, remove client
               i = clientSockets.index(client)
               clientSockets.remove(client)
               client.close()

               # remove public key
               keyToBeRemoved = clientsPublicKeys[i]
               clientsPublicKeys.remove(keyToBeRemoved)

               # remove username 
               username = users[i]
               broadcast('\n{} left!'.format(username).encode('ascii'), None)
               users.remove(username)
               break



# handle when new client connects to the server
def receiveClientConnection():
     print("encrypted message")
     print ('The server is ready to receive...')
     while True:
          connectionSocket, addr = serverSocket.accept()

          # exchange public keys with the client
          connectionSocket.send(publicKey.save_pkcs1("PEM"))
          clientPublicKey = rsa.PublicKey.load_pkcs1(connectionSocket.recv(1024))
          clientsPublicKeys.append(clientPublicKey)

          print("{} has connected!".format(str(addr)))

          connectionSocket.send(rsa.encrypt("username".encode(), clientPublicKey))
          username = connectionSocket.recv(1024).decode("ascii")
          users.append(username)
          clientSockets.append(connectionSocket)
          broadcast(f"{username} has joined!\n".encode("ascii"), connectionSocket)

          # handle client individually at the same time
          thread = threading.Thread(target=handleMessage, args=(connectionSocket,))
          thread.start()



receiveClientConnection()
