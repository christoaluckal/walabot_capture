'''
    Name:           walabot_recording
    Parameters:     duration
    Info:           Logs raw sliced image and current unix time in nanosec.
                    Rate of measurement is currently not specified. Hence it depends on local processing power.
                    
    Based on:       'RawSliceImage.py' of Walabot github project. 

    @author: Lennart Aigner <lennart.aigner@tum.de>
'''

import WalabotAPI as wb
import matplotlib
import matplotlib.pyplot as plt
import time
import sys
import os
import pandas as pd

if os.name == 'nt':
    from msvcrt import getch, kbhit
else:
    import curses

matplotlib.use('tkagg')


# Select scan arena
#             R             Phi          Theta
ARENA = [(480, 1000, 1.2), (-10, 10, 2), (-20, 20, 2)]


if __name__ == '__main__':

    if len(sys.argv[1:]) > 0:
        print("Desired recording time in minutes:", str(sys.argv[1]))
        t_end = time.time() + 60*int(sys.argv[1])
    else:
        print("No time specified. Recording time in minutes: 30")
        t_end = time.time() + 60*1
    # print "x: " + str(sys.argv[1])

    # Starting Time string
    namevar = time.strftime("%Y_%m_%w_%H_%M_%S")
    # Init of Dataframe
    dataset = pd.DataFrame()
    # Star Walabot capture process
    print("Initialize API")
    wb.Init()
    wb.Initialize()

    # Check if a Walabot is connected
    try:
        wb.ConnectAny()

    except wb.WalabotError as err:
        print("Failed to connect to Walabot.\nerror code: " + str(err.code))
        sys.exit(1)

    ver = wb.GetVersion()
    print("Walabot API version: {}".format(ver))

    print("Connected to Walabot")
    wb.SetProfile(wb.PROF_TRACKER)

    # Set scan arena
    wb.SetArenaR(*ARENA[0])
    wb.SetArenaPhi(*ARENA[1])
    wb.SetArenaTheta(*ARENA[2])
    print("Arena set")

    # Set image filter
    wb.SetDynamicImageFilter(wb.FILTER_TYPE_MTI)

    # Start scan
    wb.Start()
    wb.StartCalibration()

    stat, prog = wb.GetStatus()

    while stat == wb.STATUS_CALIBRATING and prog < 100:
        print("Calibrating " + str(prog) + "%")
        stat, prog = wb.GetStatus()

    dim1, dim2 = wb.GetRawImageSlice()[1:3]
    counter = 1
    try:
        while (t_end-time.time() > 0):
            # One iteration takes around 0.1 seconds
            wb.Trigger()
            # TODO: Signals cannot be used in Tracker mode. Which signal is best for us?
            # raw_signals = []
            # for antenna_pair in wb.GetAntennaPairs():
            # print(antenna_pair)
            # raw_signals.append(wb.GetSignal(antenna_pair))
            wb_rawimage2D = wb.GetRawImageSlice()[0]
            # plt.imshow(wb_rawimage2D, cmap='jet', interpolation='none')
            # plt.draw()
            # plt.pause(0.05)
            plt.imsave(f"images/im_{counter}.png", wb_rawimage2D)
            counter += 1
            sample_dict = dict(wb_rawimage2D=wb.GetRawImageSlice()[
                               0], timestamp=time.time_ns())
            # dataset = dataset.append(sample_dict, ignore_index=True)
            # time.sleep(20)
            # time.sleep(0.1)
    except KeyboardInterrupt:
        print('interrupted!')

    # dataset.to_pickle("dataset_walabot_{}.pkl".format(namevar))

    wb.Stop()
    wb.Disconnect()

    print("Done!")

    sys.exit(0)
