import fingerpi as fp
# from fingerpi import base
import time
from types import *    


f = fp.FingerPi()
print ('Opening connection...')
#f.Open(extra_info = True, check_baudrate = True)
f.Open()
f.CmosLed(False)

enroll_failed = False
enroll_success = False
try:
    print("{} fingerprints has been enrolled\n\n".format(f.GetEnrollCount()[0]['Parameter']))
    while ((not enroll_failed) and (not enroll_success)):
        id = input("Enter enrolled ID: 0-199: ")
        if type(id) is not IntType or id < 0 or id > 199:
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
        f.Close()
        print "Enroll failed\n\n"
        print("{} fingerprints has been enrolled.".format(f.GetEnrollCount()[0]['Parameter']))

    if enroll_success :
        time.sleep(2)
        f.CmosLed(False)
        print "Enroll success\n"
        print("{} fingerprints has been enrolled.".format(f.GetEnrollCount()[0]['Parameter']))
        f.Close()
        
except RuntimeError as e:
    print(e)

