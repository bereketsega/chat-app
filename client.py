import rsa
from socket import * # to manage connection
import threading # to manage multiple clients

# generate encryption keys
publicKey, privateKey = rsa.newkeys(1024)
# receiverPublicKey = None

username = input("Enter your username: ")

# define a client socket
serverName = "127.0.0.1" #ip of server
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)

# connect the client to the server
clientSocket.connect((serverName,serverPort))

# exchange public keys with the server
serverPublicKey = rsa.PublicKey.load_pkcs1(clientSocket.recv(1024))
clientSocket.send(publicKey.save_pkcs1("PEM"))


# handle when receiving message from the server
def receiveServerMessage():
    while True:
        try:
            msg = rsa.decrypt(clientSocket.recv(1024), privateKey).decode("ascii");
            if msg == "username":
                clientSocket.send(username.encode("ascii"))
            else:
                print(msg)
        except:
            print("Error")
            clientSocket.close()
            break



# handle when client sends message to the server
def sendServerMessage():
    while True:
        msg = '{}: {}'.format(username, input(''))
        clientSocket.send(rsa.encrypt(msg.encode("ascii"), serverPublicKey))



# a thread to handle when client receive message from the server
receiveMessageThread = threading.Thread(target=receiveServerMessage)
receiveMessageThread.start()



# a thread to handle when client send message to the server
sendMessageThread = threading.Thread(target=sendServerMessage)
sendMessageThread.start()
