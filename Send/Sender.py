import time
import cv2 as cv

import socket
HOST = '192.168.1.4'
PORT = 8886
send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
send.connect(( HOST , PORT ))
send.settimeout(1800)


from os import path
path = path.dirname(__file__) + '\\Yolo\\'

image = None
total_time = 0
print("start")
with open( (path+'CarSend.txt') ,'w')as file:
    for i in range (1,5):
        for j in range (5, 1005) :

                start_time = cv.getTickCount()

                image = str(j) + ".jpg"
                print(f"image name: {i} - {image}")
                img = cv.imread(path + image)
                
                img_bytes = cv.imencode('.jpg',img)[1].tobytes()
                data =  img_bytes
                send.sendall(data)
                end_marker = b'##END##' + image.encode()
                send.sendall(end_marker)
                
                rec = send.recv(512)
                
                end_time = (cv.getTickCount()-start_time)/cv.getTickFrequency()

                total_time = total_time + end_time 
                #file.write(f"{i} - {j} - Sent: {image} - {end_time:.4f} \n" )

                time.sleep(1)

#with open('FaceSend.txt','a')as file:
#    file.write(f"Total Time is {total_time:.4f}" )

send.close()
