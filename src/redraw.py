import numpy as np
import matplotlib.pyplot as plt
import pickle

with open('test_2d.pkl', 'rb') as f:
    M = pickle.load(f)

images = []

dim_ = None

try:
    for im,dims in M:
        dim_ = dims
        images.append(im)
except:
    for im in M:
        images.append(im)

M = images

M = np.array(M)
print(M.shape)
for i in range(0, len(M)):
    im = M[i]
    print(im.shape)
    plt.imshow(M[i], cmap='jet', interpolation='none')
    plt.xlim(0, 10)
    plt.draw()
    plt.pause(0.1)
    plt.cla()
