'''
    Name:           walabot_recording
    Parameters:     duration
    Info:           Logs raw sliced image and current unix time in nanosec.
                    Rate of measurement is currently not specified. Hence it depends on local processing power.
                    
    Based on:       'RawSliceImage.py' of Walabot github project. 

    @author: Lennart Aigner <lennart.aigner@tum.de>
'''

import WalabotAPI as wb
import sys
import time


# Select scan arena
    #             R             Phi          Theta
ARENA = [(400, 1000, 2), (-60, 60, 5), (-15, 15, 5)]

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

        self.antenna_pair = None

        self.images_2d = []
        self.images_3d = []
        self.raw_signals = []


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

        wb.Start()
        wb.StartCalibration()

        stat, prog = wb.GetStatus()
        while stat == wb.STATUS_CALIBRATING and prog < 100:
            print("Calibrating " + str(prog) + "%")
            stat, prog = wb.GetStatus()

        antennas = wb.GetAntennaPairs()
        print(f"{len(antennas)} antenna pairs found. Using {antennas[0]}")
        self.antenna_pair = antennas[0]

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
    
    def onShutdown(self,):
        wb.Stop()
        wb.Disconnect()
        print("Done!")



if __name__ == '__main__':
    res_1 = [1,1.1,1.2,1.3,1.4,1.5]
    res_2 = [1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2]
    res_3 = [1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2]
    for r1 in res_1:
        for r2 in res_2:
            for r3 in res_3:
                try:
                    print("R:",r1,"Phi:",r2,"Theta:",r3)
                    wbt = WBTROSNode()

                    wbt.initializeWLBT()
                    wbt.setProfile()
                    arena = [(450, 1000, r1), (-12, 12, r2), (-24, 24, r3)]
                    
                    wbt.setArenaParams()
                    wbt.onShutdown()
                    print("Arena:",arena)
                except Exception as e:
                    wb.Clean()
                    
                    print(e)
                    pass
                
                time.sleep(5)

                


