import fingerpi as fp
from picamera import PiCamera
import time
import datetime
from types import *
import RPi.GPIO as GPIO

camera = PiCamera()
f = fp.FingerPi()
print ('Opening connection...')

f.Open()
f.CmosLed(False)

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
LOCK = 4



def printMenu():
    print("\nMenu")
    print("0. Unlock")
    print("1. Enroll Count")
    print("2. Check Enrolled ID")
    print("3. Enroll new finger")
    print("4. Remove enrolled ID")
    print("5. Remove all IDs")
    print("6. Verify ID (1:1)")
    print("7. Identify ID (1:N)")
    print("8. Exit \n")
    return

def enroll_count():
    count = f.GetEnrollCount()[0]['Parameter']
    print ("{} fingerprints has been enrolled\n".format(count))
    del count
    return

def enroll():
    enroll_failed = False
    enroll_success = False
    try:
        print("Totally {} fingerprints has been enrolled\n".format(f.GetEnrollCount()[0]['Parameter']))
        while ((not enroll_failed) and (not enroll_success)):
            id = input("Enter enrolled ID: 0-199 (200 to exit): ")
            if (id == 200):
                enroll_failed = True
                break
            if type(id) is not IntType or id < 0 or id > 200:
                print("ID is not valid\n")
                continue
            else:
                res = f.CheckEnrolled(id)
                if res[0]['ACK']:
                    print("ID is already used\n")
                    continue
                # print(res[0]['Parameter'])
                f.CmosLed(True)
                status = f.EnrollStart(id)
                if (not status[0]['ACK']):
                    print (status[0]['Parameter'])
                    enroll_failed = True
                    break
                # print(status[0]['Parameter'])
                
                print("1.Place your finger on the scanner\n")
                f.WaitForFinger(False)
                cap1 = f.CaptureFinger(best_image = True)
                if (cap1[0]['ACK'] == False):
                    print("1. No Image captured")
                    enroll_failed = True
                    break
                status1 = f.Enroll1()
                if not status1[0]['ACK']:
                    print(status1[0]['Parameter'])
                    enroll_failed = True
                    break
                # print(status1[0]['Parameter'])
                print ("1. Remove your finger\n")
                f.WaitForFinger(True)

                print("2.Place same finger on the scanner\n")
                f.WaitForFinger(False)
                cap2 = f.CaptureFinger(best_image = True)
                if (cap2[0]['ACK'] == False):
                    print("2. No Image captured")
                    enroll_failed = True
                    break
                status2 = f.Enroll2()
                if not status2[0]['ACK']:
                    print(status2[0]['Parameter'])
                    enroll_failed = True
                    break
                # print(status2[0]['Parameter'])
                print ("2. Remove your finger\n")
                f.WaitForFinger(True)

                print("3.Place same finger on the scanner\n")
                f.WaitForFinger(False)
                cap3 = f.CaptureFinger(best_image = True)
                if (cap3[0]['ACK'] == False):
                    print("2. No Image captured")
                    enroll_failed = True
                    break
                status3 = f.Enroll3()
                if not status3[0]['ACK']:
                    if (status3[0]['Parameter'] == 0):
                        print("Finger is already registered")
                    else:
                        print(status3[0]['Parameter'])
                    enroll_failed = True
                    break
                # print(status3[0]['Parameter'])
                enroll_success = True
                print ("3. Remove your finger\n")
                f.WaitForFinger(True)            
                
        if enroll_failed :
            time.sleep(2)
            f.CmosLed(False)
            print "Enroll failed\n\n"
        if enroll_success :
            time.sleep(2)
            f.CmosLed(False)
            print "Enroll success\n"
            print("Totally {} fingerprints has been enrolled.\n".format(f.GetEnrollCount()[0]['Parameter']))
        
    except RuntimeError as e:
        print(e)
    return
    

def check_enrolled_ID():
    while (True):
        id = input("Enter enrolled ID: 0-199 (200 to eixt): ")
        if (id == 200):
            break
        if type(id) is not IntType or id < 0 or id > 199:
            print("ID is not valid\n")
            continue
        else:
            status = f.CheckEnrolled(id)[0]['ACK']
            if (status):
                print ("ID: {} is already used.".format(id))
            else:
                print ("ID: {} is good to use.".format(id))
            del status
            break
    return

def verify():
    while (True):
        id = input("Enter the ID: 0-199 (200 to exit): ")
        if (id == 200):
            break
        if type(id) is not IntType or id < 0 or id > 199:
            print("ID is not valid\n")
            continue
        else:
            status = f.CheckEnrolled(id)[0]['ACK']
            if (not status):
                print ("ID: {} is not registered.".format(id))
            else:
                f.CmosLed(True)
                print("Place your finger on the scanner\n")
                f.WaitForFinger(False)                
                cap1 = f.CaptureFinger(best_image = False)
                if (cap1[0]['ACK'] == False):
                    print("1. No Image captured")
                    break                
                rp = f.Verify(id)
                print("Remove your finger \n")
                f.WaitForFinger(True)
                if (rp[0]['ACK']):
                    print (rp[0]['Parameter'])
                    print ("Verified \n")
                else:
                    print ("Finger is not verified \n")
                
                f.CmosLed(False)
            break
    return

def identify():
    f.CmosLed(True)
    print("Place your finger on the scanner\n")
    f.WaitForFinger(False)
    cap1 = f.CaptureFinger(best_image = False)
    if (cap1[0]['ACK'] == False):
        print("1. No Image captured \n")
        return
    rp = f.Identify()
    print("Remove your finger \n")
    f.WaitForFinger(True)
    if (rp[0]['ACK']):
        print ("The finger ID is {}.\n".format(rp[0]['Parameter']))
    else:
        print ("Finger is not registered \n")
    f.CmosLed(False)
    return

def removeID():
    while (True):
        id = input("Enter the ID: 0-199 (200 to exit): ")
        if (id == 200):
            break
        if type(id) is not IntType or id < 0 or id > 199:
            print("ID is not valid\n")
            continue
        else:
            status = f.CheckEnrolled(id)[0]['ACK']
            if (not status):
                print ("ID: {} is not registered.".format(id))
                continue
            else:
                rp = f.DeleteId(id)
                if(rp[0]['ACK']):
                    print ("ID: {} is deleted.".format(id))
                    break
                else:
                    print ("{} error!".format(rp[0]['Parameter']))
                    break
    return

def removeAll():
    status = f.DeleteAll()
    if (status):
        print ("All the fingerprints are deleted")
    else:
        print ("{} error!".format(rp[0]['Parameter']))
    return

def unlock():
    #takePic()
    f.CmosLed(True)
    print("Place your finger on the scanner\n")
    f.WaitForFinger(False)
    cap1 = f.CaptureFinger(best_image = False)
    if (cap1[0]['ACK'] == False):
        print("1. No Image captured \n")
        return
    rp = f.Identify()
    print("Remove your finger \n")
    f.WaitForFinger(True)
    f.CmosLed(False)
    if (rp[0]['ACK']):
        print ("The finger ID is {}.\n".format(rp[0]['Parameter']))
        GPIO.setup(LOCK, GPIO.OUT)
        GPIO.output(LOCK, True)
        print("Unlock")
        i = 5
        while i > 0:
            print(i)
            i = i -1
            time.sleep(1)
        GPIO.output(LOCK, False)
        print("lock")
    else:
        print ("Finger is not registered \n")
    #f.CmosLed(False)
    return

def takePic():
    
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    camera.resolution = (400,300)
    camera.framerate = (15)
    #camera.start_preview()
    time.sleep(1)
    camera.capture("/home/pi/SF_DeviceSecuritySystem/Fingerprint/resources/SF_DSS/image/%s.jpg" % date)
    #camera.stop_preview()    



    

try:
    while True:
        f.CmosLed(False)
        printMenu()
        option = input("Select an option: ")
        if (option == 0 ):
            print("0. Unlock")
            unlock()
            continue
        if (option == 1):
            print("1. Enroll Count: \n")
            enroll_count()
            continue
        elif (option == 2):
            print("2. Check Enrolled ID: \n")
            check_enrolled_ID()
            continue
        elif (option == 3):
            print("3. Enroll new finger: \n")
            enroll()
            continue
        elif (option == 4):
            print("4. Remove enrolled ID")
            removeID()
            continue
        elif (option == 5):
            print("5. Remove all IDs")
            removeAll()
            continue
        elif (option == 6):
            print("6. Verify ID (1:1)")
            verify()
            continue
        elif (option == 7):
            print("7. Identify ID (1:N)")
            identify()
            continue
        elif (option == 8):
            print("8. Exit")
            f.Close()
            GPIO.cleanup()
            break
        else:
            print("Invalid input")
            continue
except RuntimeError as e:
    print(e)
except SyntaxError as e:
    print (e)
except NameError as e:
    print (e)

    
