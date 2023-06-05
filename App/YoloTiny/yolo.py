import socket, cv2 as cv
import numpy as np
import psutil

# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# Initialize the parameters
conf = 0.5  #Confidence threshold
nmsThreshold = 0.4   #Non-maximum suppression threshold

# Load names of classes
classesFile = "coco.names";
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')
    
# Give the configuration and weight files for the model and load the network using them.
modelConfiguration = "yolov3-tiny.cfg";
modelWeights = "yolov3-tiny.weights";
net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)

net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)


port_recive = 8886         # Port to listen on (non-privileged ports are > 1023)
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
with open('YoloOut.txt', 'w') as file:  # Open the file for writing
    try:
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
                if b'.jpg' in image_bytes:
                    break
                if not data:
                    connection_lost = True
                    break
            
            # Calculating Rec image   
            rec_time = (cv.getTickCount() - st_time) / cv.getTickFrequency()
            
            recive_socket.sendall(b'DONE')
            
            # Check if image bytes are empty
            if not image_bytes:
                break
            
            # Start Timer
            st_time = cv.getTickCount()
            
            image_parts = image_bytes.split(b'##END##')
            image_name = image_parts[1].decode()
            image_bytes = image_parts[0]
            
            img = cv.imdecode(np.frombuffer(image_bytes, np.uint8), cv.IMREAD_COLOR)
            img_output = img

            # Create a 4D blob from a frame.
            blob = cv.dnn.blobFromImage(img_output, 1/255, (416, 416),[0,0,0], swapRB=True, crop=False)
            # Sets the input to the network
            net.setInput(blob)
            # Runs the forward pass to get output of the output layers
            outputs = net.forward(getOutputsNames(net))

            frameHeight = img_output.shape[0]
            frameWidth = img_output.shape[1]
            boxes = []
            confidences = []
            classIds = []
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    classId = np.argmax(scores)
                    confidence = scores[classId]
                    if confidence > conf:
                        center_x = int(detection[0] * frameWidth)
                        center_y = int(detection[1] * frameHeight)
                        width = int(detection[2] * frameWidth)
                        height = int(detection[3] * frameHeight)
                        left = int(center_x - width / 2)
                        top = int(center_y - height / 2)
                        classIds.append(classId)
                        confidences.append(float(confidence))
                        boxes.append([left, top, width, height])
            indices = cv.dnn.NMSBoxes(boxes, confidences, conf, nmsThreshold)

            if len(indices) > 0:
                for i in indices:
                    i = i[0]
                    box = boxes[i]
                    left = box[0]
                    top = box[1]
                    width = box[2]
                    height = box[3]
                    cv.rectangle(img_output, (left, top), ((left+width), (top+height)), (255,178,50), 2)
                # Save output image
                cv.imwrite( ("out"+image_name) , img_output)
        
            start_time = ((cv.getTickCount() - st_time) / cv.getTickFrequency())
            # Get resource usage after
            memory_after = process.memory_info().rss / 1024 / 1024  # memory usage in MB
            cpu_after = process.cpu_percent()
            # Print the excution time
            file.write(f"{image_name} - Wait {waiting_time:.4f} - Rec {rec_time:.4f} - Process {start_time:.4f} - {len(indices)} - Memory: {memory_after:.2f} MB - CPU: {cpu_after:.2f} % \n")

            
    except ConnectionResetError:
        print("Connection lost")

# Write the total time to the file
total_time_t = (cv.getTickCount() - total_time) / cv.getTickFrequency()
print(f"Total time taken to receive all images: {total_time_t:.4f} seconds\n")
with open('YoloOut.txt', 'a') as file:  # Append to the file
    file.write(f"Total time taken to receive all images: {total_time_t:.4f} seconds\n")

    
recive_socket.close()
recive.close()
