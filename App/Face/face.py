import socket, cv2 as cv 
import numpy as np
#import time
import psutil

# Read Haar Cascade file
haar_file = "face.xml"
haar_cascade = cv.CascadeClassifier(haar_file)

port_recive = 8889         # Port to listen on (non-privileged ports are > 1023)
recive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP


recive.bind( ('', port_recive) )
recive.listen()
recive_socket, recive_address = recive.accept()  
print("Connect - %s" %str(recive_address))

connection_lost = False

# Get resource usage before
process = psutil.Process()
memory_before = process.memory_info().rss / 1024 / 1024  # memory usage in MB
cpu_before = process.cpu_percent()

total_time = cv.getTickCount()
with open('FaceOut.txt', 'w') as file:  # Open the file for writing
    try:
        #file.write(f"Memory usage before: {memory_before:.2f} MB - CPU usage before: {cpu_before:.2f} %\n")
        while not connection_lost: 
            # Receive image bytes
            image_bytes = b''
            st_time = cv.getTickCount()
            data = recive_socket.recv(1024)
            #Calculating waiting time
            waiting_time = (cv.getTickCount() - st_time) / cv.getTickFrequency()
            st_time = cv.getTickCount()
            image_bytes = image_bytes + data
            while True:
                data = b''
                data = recive_socket.recv(1024)
                image_bytes = image_bytes + data
                # Calculating Rec image
                if b'.jpg' in image_bytes:
                    break
                if not data:
                    connection_lost = True
                    break
                
            rec_time = (cv.getTickCount() - st_time) / cv.getTickFrequency()
            recive_socket.sendall(b'DONE')
            
            # Check if image bytes are empty
            if not image_bytes:
                #print("Connection lost")
                break
            
            # Start Timer
            st_time = cv.getTickCount()
            
            #image_parts = image_bytes.decode('utf-8')
            image_parts = image_bytes.split(b'##END##')
            image_name = image_parts[1].decode()
            image_bytes = image_parts[0]
            
            img = cv.imdecode(np.frombuffer(image_bytes, np.uint8), cv.IMREAD_COLOR)
            output = img
            output = cv.resize(output, (600,400) )
            # Convert image to GRAY scale
            gray = cv.cvtColor(output, cv.COLOR_BGR2GRAY)
            # Call Haar Cascade recognition
            obj_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2)
            num_detect = 0
            if len(obj_rect) > 0:
                # Drow rectangle on object
                for (x,y,w,h) in obj_rect:
                    cv.rectangle(output, (x,y), (x+w,y+h), (0,255,0), thickness=2)
                    num_detect = num_detect + 1
                # Save output image 
                cv.imwrite( ('out'+image_name) , output)

            start_time = ((cv.getTickCount() - st_time) / cv.getTickFrequency())
            # Get resource usage after
            memory_after = process.memory_info().rss / 1024 / 1024  # memory usage in MB
            cpu_after = process.cpu_percent()
            # Print the excution time
            #print(f"{image_name} - Wait {waiting_time:.4f} - Rec {rec_time:.4f} - Process {start_time:.4f} - {len(obj_rect)}")
            file.write(f"{image_name} - Wait {waiting_time:.4f} - Rec {rec_time:.4f} - Process {start_time:.4f} - {num_detect} - Memory: {memory_after:.2f} MB - CPU: {cpu_after:.2f} % \n")

            
    except ConnectionResetError:
        print("Connection lost")

# Write the total time to the file
total_time_t = (cv.getTickCount() - total_time) / cv.getTickFrequency()
print(f"Total time taken to receive all images: {total_time_t:.4f} seconds\n")
with open('FaceOut.txt', 'a') as file:  # Append to the file
    file.write(f"Total time taken to receive all images: {total_time_t:.4f} seconds\n")

    
recive_socket.close()
recive.close()
