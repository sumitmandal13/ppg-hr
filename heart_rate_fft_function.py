import os
import numpy as np
from matplotlib import pyplot as plt
import imageio
# import cv2
from datetime import datetime
from flask import Flask 
import json

app = Flask(__name__)


def perform_all():
    videofile = 'sumit_89.mp4'
    filename,extension = videofile.split(".")
    
    fps = 30 
    PLOT = True
    SAVE = True

    # Setting up plotting
    # plt.style.use('fivethirtyeight')

    # pull the video in the array

    video = imageio.get_reader(videofile,'ffmpeg')



    # print(type(video))
    # print(type(cap))



    # print(len(video))



    colors = {'red':[], 'green':[], 'blue':[]}

    for frame in video:
        # Average all pixels
        lumped_pixel = np.mean(frame,axis=(0,1))
        colors['red'].append(lumped_pixel[0])
        colors['green'].append(lumped_pixel[1])
        colors['blue'].append(lumped_pixel[2])





#     import seaborn as sns
#     sns.lineplot(colors['red'],palette=['r'],linewidth='1',color='red')




#     sns.lineplot(colors['green'],color='green',linewidth=1)




    # Normalize red/green/blue channels to 255
    for key in colors:
        colors[key] = np.divide(colors[key],255)

    # sns.lineplot(colors['red'],palette=['r'],linewidth='1',color='red')


    # Convert frame to times
    x = np.arange(len(colors['red'])) / fps

    # Perform simple high-pass filter on the data
    colors['red_filtered'] = list()
    colors['red_filtered'] = np.append(colors['red_filtered'],colors['red'][0])
    tau = 0.25 # HPF high passnfilter time constant in secoonds
    fsample = fps # sample rate

    alpha = tau / (tau + 2/fsample)
    # print('alpha',alpha)

    # Doing for only red, since red is dominant
    for index,frame in enumerate(colors['red']):
        if index>0:
            # print(index,frame)
            y_prev = colors['red_filtered'][index-1]
            x_curr = colors['red'][index]
            x_prev = colors['red'][index-1]
            colors['red_filtered'] = np.append(colors['red_filtered'],alpha * (y_prev + x_curr - x_prev))


            # print('y_prev',y_prev)
            # print('x_curr',x_curr)
            # print('x_prev',x_prev)
            # print("colors['red_filtered']",colors['red_filtered'])

    # Truncating starting data since beginning of series will be wonky

    x_filt = x[50:-1]
    colors['red_filtered'] = colors['red_filtered'][50:-1]

    # Take FFt to get frequency information
    red_fft = np.absolute(np.fft.fft(colors['red_filtered']))
    N = len(colors['red_filtered'])
    freqs = np.arange(0,fsample/2,fsample/N)



    # Truncate to fs/2
    red_fft = red_fft[0:len(freqs)]

    # Get heart rate from FFT
    max_val = 0
    max_index = 0

    for index,fft_val in enumerate(red_fft):
        if fft_val > max_val:
            max_val = fft_val
            max_index = index


    heartrate = freqs[max_index] * 60
    print('Estimated Heartrate: {} bpm'.format(heartrate))
    
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    
    return heartrate,dt_string    

# perform_all()

def create_json():
    try:
        with open('Accounts.json',encoding='utf8') as fp:
            data = json.load(fp)
            heartrate,dt_string = perform_all()
            data['heart_rate'].append(heartrate)
            data['Experiment_time'].append(dt_string)

    except FileNotFoundError:
        print('File not found.  Creating initial data...')
        # data = {'heart_rate': [], 'Experiment_time': []}

    with open('Accounts.json', 'w', encoding='utf8') as fp:
        json.dump(data, fp, indent=2)
        
create_json()

def calculate_diff():
    heartrate,dt_string = perform_all()
    act_value = int(input("Enter Actual Value"))
    deviation = (abs((act_value - heartrate)/act_value)*100)
    print(f"deviation is {deviation} percentage")
    return deviation

calculate_diff()


