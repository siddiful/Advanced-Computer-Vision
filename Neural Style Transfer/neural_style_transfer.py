# -*- coding: utf-8 -*-
"""Neural Style Transfer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fZknBMAaVpmOJWeV2E9sszxsUQVPcZfg
"""

from keras.models import Model
from keras.layers import Input, Conv2D, MaxPooling2D, AveragePooling2D
from keras.applications.vgg16 import VGG16, preprocess_input
import keras.utils as image
import numpy as np
import matplotlib.pyplot as plt
import keras.backend as K
from scipy.optimize import fmin_l_bfgs_b
from content_transfer import AvgpoolVGG, unpreprocess, scale_img
from style_transfer import gram_matrix, style_loss, minimise

import tensorflow as tf
if tf.__version__.startswith('2'):
  tf.compat.v1.disable_eager_execution()

def load_preprocess(path, shape=None):
  img = image.load_img(path, target_size=shape)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  x = preprocess_input(x)

  return x

content_image = load_preprocess('content.jpg')
h, w = content_image.shape[1:3]

style_image = load_preprocess('style.jpg', (h,w))

batch_shape = content_image.shape
shape = batch_shape[1:]

vgg = AvgpoolVGG(shape)
content_model = Model(vgg.input, vgg.layers[13].get_output_at(1))
content_target = K.variable(content_model.predict(content_image))

sym_conv_output = [layer.get_output_at(1) for layer in vgg.layers if layer.name.endswith('conv1')]
style_model = Model(vgg.input, sym_conv_output)
target_conv_output = [K.variable(y) for y in style_model.predict(style_image)]

style_weights = [0.2,0.4,0.3,0.5,0.2]

loss = K.mean(K.square(content_target - content_model.output))
for w, symbol, target in zip(style_weights, sym_conv_output, target_conv_output):
  loss += w*style_loss(symbol[0], target[0])

gradient = K.gradients(loss, vgg.input)

get_loss_grads = K.function(inputs=[vgg.input], outputs=[loss]+gradient)

def get_loss_grads_wrap(xvec):
  l, g = get_loss_grads([xvec.reshape(*batch_shape)])
  return l.astype(np.float64), g.flatten().astype(np.float64)

final_img = minimise(get_loss_grads_wrap, 10, batch_shape)
plt.imshow(scale_img(final_img))
plt.show()