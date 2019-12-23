import face_recognition, cv2
import numpy as np
import os, time, requests
from threading import Thread
import gui_messages as window
import routine_backup as bkp

already = []
already_time = []
out_time = []
left_for_today = []
already,already_time,out_time,left_for_today = bkp.restore_lists(already,already_time,out_time,left_for_today)
def printstatus(a):
    if(a.startswith('2')):
        print("Data Sent Successfully")
    else:
        if(a.startswith('4')):
            print("Client Error")
        if(a.startswith('5')):
            print("Server Error")
        print('couldnt send data, error code:',r.status_code)

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
            mi = int('0{}'.format(mi))
        hr = hr + 1
        strtime = str(hr)+'.'+str(mi)
        return(float(strtime))
    t = float(t)+0.15
    return(float(t))

video_capture = cv2.VideoCapture(0)

video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1376)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
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

known_face_encodings = encoded_images
known_face_names = []
for file in face_images:
	known_face_names.append(file.split("/")[1].split(".")[0])

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                if('_' in name):
                    name=name.split("_")[0]
                t=time.time()           
                already=timecheckcall(t,already)                     
                if name not in already:
                    bkp.backup_lists(already,already_time,out_time,left_for_today)
                    Thread(target=window.greet_user, args=(name,0,)).start()
                    t=time.time()
                    r=requests.post("http://833a3270.ngrok.io/updateattend/{}/{}".format(name,t))
                    r.status_code
                    a=str(r.status_code)
                    printstatus(a)
                    already.append(name)
                    time_in = float(time.strftime("%H.%M", time.localtime(t)))
                    already_time.append(time_in)
                    out_time.append(resolvetime(time_in))
                    bkp.backup_lists(already,already_time,out_time,left_for_today)
                    print(already)
                else:

                    index_out=already.index(name)
                    if(out_time[index_out]<float(time.strftime("%H.%M", time.localtime(time.time())))):
                        if(name not in left_for_today):
                            Thread(target=window.greet_user, args=(name,1,)).start()
                            r=requests.post("http://833a3270.ngrok.io/updateattend/{}/{}".format(name,t))
                            left_for_today.append(name)
                            r.status_code
                            a=str(r.status_code)
                            printstatus(a)
                        else:
                            pass
                    else:
                        pass
            break

    process_this_frame = not process_this_frame
    
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1 ) & 0xFF == ord('q'):
        bkp.backup_lists([],[],[],[])
        break
video_capture.release()
cv2.destroyAllWindows()
