import time
import cv2 as cv

import socket
HOST = '192.168.1.2'
PORT = 8886
send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
send.connect(( HOST , PORT ))
send.settimeout(1800)
print("Connect")


from os import path
path = path.dirname(__file__) + '\\Car\\'

image = None
total_time = 0
for i in range (1,5):
    for j in range (1, 1001) :

            start_time = cv.getTickCount()

            image = str(j) + ".jpg"
            img = cv.imread(path + image)
            
            img_bytes = cv.imencode('.jpg',img)[1].tobytes()
            data =  img_bytes
            send.sendall(data)
            end_marker = b'##END##' + image.encode()
            send.sendall(end_marker)
            
            rec = send.recv(512)
            
            end_time = (cv.getTickCount()-start_time)/cv.getTickFrequency()

            total_time = total_time + end_time 
            print(f"{i} - {j} - Sent: {image} - {end_time:.4f} \n" )

            time.sleep(2)


send.close()
