# -*- coding: utf-8 -*-
"""CAM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Oy_I4KYnjKPDAsYnwadztCSGp7WCVdi1
"""

import tensorflow as tf
from keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from keras.models import Sequential, Model
from keras.layers import Input
import keras.utils as image
import numpy as np
import matplotlib.pyplot as plt
import glob as glob

resnet = ResNet50(include_top=True, weights='imagenet', input_shape=(224, 224, 3))

resnet.summary()

activation_layer = resnet.get_layer('conv5_block3_out')

model = Model(inputs=resnet.input, outputs=activation_layer.output)

model.summary()

fc_layer = resnet.get_layer('predictions')

W = fc_layer.get_weights()[0]

img = image.load_img('toucan.jpg', target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

res = resnet.predict(x)

dec_pred = decode_predictions(res)[0]

pred_classname = dec_pred[0][1]
pred_prob = np.argmax(res[0])

print(pred_classname)
print(pred_prob)

w = W[:,pred_prob]

feature_map = model.predict(x)[0]

cam = feature_map.dot(w)

import scipy as sp

cam = sp.ndimage.zoom(cam, (32, 32), order=1)

plt.subplot(1,2,1)
plt.imshow(img, alpha=0.8)
plt.imshow(cam, cmap='jet', alpha=0.5)
plt.subplot(1,2,2)
plt.imshow(img)
plt.title(pred_classname)
plt.show()