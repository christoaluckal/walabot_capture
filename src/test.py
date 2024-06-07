#!/usr/bin/env python3
'''
    Name:           walabot_recording
    Parameters:     duration
    Info:           Logs raw sliced image and current unix time in nanosec.
                    Rate of measurement is currently not specified. Hence it depends on local processing power.
                    
    Based on:       'RawSliceImage.py' of Walabot github project. 

    @author: Lennart Aigner <lennart.aigner@tum.de>
'''

import WalabotAPI as wb
import time
import sys
import rospy
import numpy as np
from std_msgs.msg import Bool,Int16
import pickle
import os

curr_dir = os.path.dirname(os.path.realpath(__file__))


# Select scan arena
    #             R             Phi          Theta
ARENA = [(480, 1000, 1.2), (-10, 10, 2), (-20, 20, 2)]
# ARENA = [(480, 1000, 3), (-10, 10, 1), (-20, 20, 1)]

# ARENA CONFIG
# R:
    # Min: [1-1000]
    # Max: [1-1000]
    # Res: [0.1-10]
# Phi:
    # Min: [-90,90]
    # Max: [-90,90]
    # Res: [0.1-10]
# Theta:
    # Min: [-90,90]
    # Max: [-90,90]
    # Res: [0.1-10]
# Threshold:
    # Min: [0.1-100]
    # Max: [0.1-100]
    # Default: 15

class WBTROSNode:
    def __init__(self,arena=ARENA,base_name="",record_type="continuous") -> None:
        self.arena = arena
        self.record_listener = rospy.Subscriber("/wala_record",Int16,self.record)
        self.record_type = record_type
        if base_name == "":
            self.basename = "experiment_"+time.strftime("%Y%m%d-%H%M%S")
        else:
            self.basename = base_name

        self.antenna_pair = None

        self.rate = rospy.Rate(100)

        self.images_2d = []
        self.images_3d = []
        self.raw_signals = []

        rospy.on_shutdown(self.onShutdown)

        
    def record(self,msg: Int16):
        duration = str(msg.data)+"s"
        
        try:
            if duration == "0s":

                self.continuousStream()
            elif duration[-1] == "s":
                self.durationRecord(duration=duration)
            else:
                print("Invalid record type. Please use 'continuous' or 'duration'")
                sys.exit(1)
        except (rospy.ROSInterruptException, KeyboardInterrupt):
            rospy.signal_shutdown("Shutting down")

        

    def continuousStream(self,):
        print("Recording continuously")
        while True:
            wb.Trigger()
            self.images_2d.append(wb.GetRawImageSlice()[0])
            self.images_3d.append(wb.GetRawImage())
            self.raw_signals.append(wb.GetSignal(self.antenna_pair))
            self.rate.sleep()

    def durationRecord(self,duration="10s"):
        print(f"Recording for {duration}")
        dur_type = duration[-1]
        dur_val = int(duration[:-1])
        
        if dur_type == "m":
            dur_val*= 60
        elif dur_type == "h":
            dur_val*= 60
            dur_val*= 60
        else:
            pass

        start = time.time()
        while time.time()-start < dur_val:
            wb.Trigger()
            self.images_2d.append(wb.GetRawImageSlice()[0])
            self.images_3d.append(wb.GetRawImage())
            self.raw_signals.append(wb.GetSignal(self.antenna_pair))
            self.rate.sleep()
            print(f"Remaining time: {dur_val-(time.time()-start)}s")

    def initializeWLBT(self,):
        wb.Init()
        wb.Initialize()
        try:
            wb.ConnectAny()
        except wb.WalabotError as err:
            print("Failed to connect to Walabot.\nerror code: " + str(err.code))
            sys.exit(1)

        ver = wb.GetVersion()
        print("Walabot API version: {}".format(ver))

        print("Connected to Walabot")

        

    def setProfile(self,profile=wb.PROF_SENSOR):
        wb.SetProfile(profile)

    def setArenaParams(self,arena=ARENA):
        assert len(arena) == 3 and all([len(a) == 3 for a in arena])

        wb.SetArenaR(*arena[0])
        wb.SetArenaPhi(*arena[1])
        wb.SetArenaTheta(*arena[2])
        print("Arena set")

    def setFilter(self,filter=wb.FILTER_TYPE_NONE):
        assert filter in [wb.FILTER_TYPE_NONE, wb.FILTER_TYPE_DERIVATIVE, wb.FILTER_TYPE_MTI]

        wb.SetDynamicImageFilter(filter)

    def getDimensions(self,):
        return wb.GetRawImageSlice()[1:3]
    
    def start(self):
        wb.Start()
        wb.StartCalibration()

        stat, prog = wb.GetStatus()
        while stat == wb.STATUS_CALIBRATING and prog < 100:
            print("Calibrating " + str(prog) + "%")
            wb.Trigger()
            stat, prog = wb.GetStatus()
            # time.sleep(0.1)

        antennas = wb.GetAntennaPairs()
        print(f"{len(antennas)} antenna pairs found. Using {antennas[0]}")
        self.antenna_pair = antennas[0]

    def onShutdown(self,):
        wb.Stop()
        wb.Disconnect()
        print("Done!")

        # with open(f"{self.basename}_2d.pkl","wb") as f:
        #     pickle.dump(self.images_2d,f)

        # with open(f"{self.basename}_3d.pkl","wb") as f:
        #     pickle.dump(self.images_3d,f)

        # with open(f"{self.basename}_signals.pkl","wb") as f:
        #     pickle.dump(self.raw_signals,f)

        with open(f"{curr_dir}/{self.basename}_2d.pkl","wb") as f:
            pickle.dump(self.images_2d,f)

        with open(f"{curr_dir}/{self.basename}_3d.pkl","wb") as f:
            pickle.dump(self.images_3d,f)

        with open(f"{curr_dir}/{self.basename}_signals.pkl","wb") as f:
            pickle.dump(self.raw_signals,f)

        sys.exit(0)

    def run(self):
        while not rospy.is_shutdown():
            self.rate.sleep()


if __name__ == '__main__':
    rospy.init_node("walabot_recording")
    wbt = WBTROSNode(base_name="test")
    wbt.initializeWLBT()
    wbt.setProfile()
    wbt.setArenaParams()
    wbt.setFilter()
    wbt.start()
    rospy.spin()
