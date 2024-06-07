import numpy as np
import matplotlib.pyplot as plt
import pickle

with open('rawImage.pkl', 'rb') as f:
    M = pickle.load(f)

images = []

dim_ = None

for im,dims in M:
    dim_ = dims
    images.append(im)

M = images

M = np.array(M)

for i in range(0, len(M)):
    im = M[i]

    plt.imshow(M[i], cmap='jet', interpolation='none')
    plt.draw()
    plt.pause(0.1)
    plt.cla()
