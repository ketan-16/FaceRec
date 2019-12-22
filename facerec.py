import face_recognition, cv2
import numpy as np
import os, time, requests
from gtts import gTTS
from playsound import playsound
from threading import Thread
import tkinter as tk
from tkinter import ttk

already = []
already_time = []
out_time = []
left_for_today = []
LARGE_FONT= ("Verdana", 12)
NORM_FONT = ("Helvetica", 16)

def popupmsg(msg): 
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=35,padx=192)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    windowWidth = popup.winfo_reqwidth()
    windowHeight = popup.winfo_reqheight()
    positionRight = int(popup.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(popup.winfo_screenheight()/2 - windowHeight/2)
    popup.geometry("450x250+{}+{}".format(positionRight, positionDown))
    popup.mainloop()

#Function gets greet audio file, plays it and then deletes it
def plays(name):
    tts = gTTS('Welcome,'+name)
    tts.save('greet.mp3')
    playsound('greet.mp3')
    os.remove('greet.mp3')

#Prints httpsreponse status
def printstatus(a):
    if(a.startswith('2')):
        print("Data Sent Successfully")
    else:
        if(a.startswith('4')):
            print("Client Error")
        if(a.startswith('5')):
            print("Server Error")
        print('couldnt send data, error code:',r.status_code)

#maintain a list of already checked-in users
def timecheckcall(t1,already):
    t2=float(time.strftime("%H.%M", time.localtime(t1)))
    return already

def resolvetime(t):
    
    t = str(t)
    hr,mi = t.split('.')
    mi=int(mi)
    hr=int(hr)
    if(mi>=45):
        mi=mi-45
        if mi <10:
            mi = int('0'+mi)
        hr = hr + 1
        strtime = str(hr)+'.'+str(mi)
        return(float(strtime))
    t = t+0.15
    return(float(t))
    
    

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1376)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
# Load a sample picture and learn how to recognize it.
path = 'face_images'

files = os.listdir(path)
face_images = []
for file in files:
	if file.endswith('.jpg'):
		face_images.append(path+"/"+file)
print(face_images)

loaded_images = []
encoded_images = []
for img in face_images:
	tmp = face_recognition.load_image_file(img)
	enctmp = face_recognition.face_encodings(tmp)[0]

	loaded_images.append(tmp)
	encoded_images.append(enctmp)

# Create arrays of known face encodings and their names
known_face_encodings = encoded_images
known_face_names = []
for file in face_images:
	known_face_names.append(file.split("/")[1].split(".")[0])

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]
    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]
            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                if('_' in name):
                    name=name.split("_")[0]
                t=time.time()           
                already=timecheckcall(t,already)                     
                if name not in already:
                    msg='Welcome, '+name
                    Thread(target=popupmsg, args=(msg,)).start()
                    # Thread(target=plays, args=(name,)).start()
                    t=time.time()
                    r=requests.post("http://833a3270.ngrok.io/updateattend/{}/{}".format(name,t))
                    r.status_code
                    a=str(r.status_code)
                    printstatus(a)
                    already.append(name)
                    time_in = float(time.strftime("%H.%M", time.localtime(t)))
                    already_time.append(time_in)
                    out_time.append(resolvetime(time_in))
                    print(already)
                else:

                    index_out=already.index(name)
                    print(out_time[index_out],float(time.strftime("%H.%M", time.localtime(time.time()))))
                    if(out_time[index_out]<float(time.strftime("%H.%M", time.localtime(time.time())))):
                        print('bahar wala if')
                        if(name not in left_for_today):
                            print('andar wala if')
                            r=requests.post("http://833a3270.ngrok.io/updateattend/{}/{}".format(name,t))
                            left_for_today.append(name)
                            r.status_code
                            a=str(r.status_code)
                            printstatus(a)
                        else:
                            print("Dear, you've already checked out")
                    else:
                        print('Outside else')
            break

    process_this_frame = not process_this_frame
    
    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcams
video_capture.release()
cv2.destroyAllWindows()
