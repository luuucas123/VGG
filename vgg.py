# -*- coding: utf-8 -*-

"""
Author: Vic Chan
Date: 7/8/2017
Content: VGG Implementation
"""

import tensorflow as tf
import data as dataset

learning_rate = 0.0001

tf.app.flags.DEFINE_string('data_path', '', 'Enter data (CIFAR-100) path')
tf.app.flags.DEFINE_integer('epoch', 10, 'Enter the epoches to train the network')
tf.app.flags.DEFINE_integer('batch_size', 32, 'Enter the batch size')

image_size = 32 * 32 * 3
image_classes = 100
test_step = 1

image = tf.placeholder(tf.float32, [None, image_size], name='image')
label = tf.placeholder(tf.float32, [None, image_classes], name='label')


def init_weights(input_size, output_size):
    return tf.Variable(tf.truncated_normal([input_size, output_size], stddev=0.1))


def init_filter(filter_size, filter_nums, channels):
    return tf.Variable(tf.truncated_normal([filter_size, filter_size, channels, filter_nums], stddev=0.1))


def conv2d(name, x, conv_filter, b, stride=1):
    x = tf.nn.conv2d(input=x,
                     filter=conv_filter,
                     strides=[1, stride, stride, 1],
                     padding='SAME',
                     name=name)
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)


def maxpool(name, x, pool_size, stride):
    return tf.nn.max_pool(value=x,
                          ksize=[1, pool_size, pool_size, 1],
                          strides=[1, stride, stride, 1],
                          padding='SAME',
                          name=name)


def batch_norm(x):
    batch_mean, batch_var = tf.nn.moments(x, [0, 1, 2], keep_dims=True)
    scale = tf.Variable(tf.ones([x.get_shape()[-1]]))
    beta = tf.Variable(tf.zeros([x.get_shape()[-1]]))
    epsilon = 1e-3

    return tf.nn.batch_normalization(
        x,
        mean=batch_mean,
        variance=batch_var,
        scale=scale,
        variance_epsilon=epsilon,
        offset=beta
    )


def init_bias(dim):
    return tf.Variable(tf.truncated_normal([dim], stddev=1))


def fc(name, x, weights, bias):
    fc1 = tf.matmul(x, weights)
    return tf.nn.relu(tf.add(fc1, bias))


def softmax(name, x, weights, bias):
    fc1 = tf.matmul(x, weights)
    return tf.nn.softmax(tf.add(fc1, bias))


def dump_parameters(x):
    print("[Shape]%s" % (x.shape))


parameters = {
    # stage 1
    'conv_1_bias': init_bias(64),
    'conv_1_filter': init_filter(3, 64, 3),
    'conv_2_bias': init_bias(64),
    'conv_2_filter': init_filter(3, 64, 64),
    # stage 2
    'conv_3_bias': init_bias(128),
    'conv_3_filter': init_filter(3, 128, 64),
    'conv_4_bias': init_bias(128),
    'conv_4_filter': init_filter(3, 128, 128),
    # stage 3
    'conv_5_bias': init_bias(256),
    'conv_5_filter': init_filter(3, 256, 128),
    'conv_6_bias': init_bias(256),
    'conv_6_filter': init_filter(3, 256, 256),
    'conv_7_bias': init_bias(256),
    'conv_7_filter': init_filter(3, 256, 256),
    # stage 4
    'conv_8_bias': init_bias(512),
    'conv_8_filter': init_filter(3, 512, 256),
    'conv_9_bias':init_bias(512),
    'conv_9_filter': init_filter(3, 512, 512),
    'conv_10_bias': init_bias(512),
    'conv_10_filter': init_filter(3, 512, 512),
    # stage 5
    'conv_11_bias': init_bias(512),
    'conv_11_filter': init_filter(3, 512, 512),
    'conv_12_bias': init_bias(512),
    'conv_12_filter': init_filter(3, 512, 512),
    'conv_13_bias': init_bias(512),
    'conv_13_filter': init_filter(3, 512, 512),

    # fc weights and bias
    'fc_1_weights': init_weights(512, 4096),
    'fc_1_bias': init_bias(4096),

    'fc_2_weights': init_weights(4096, 4096),
    'fc_2_bias': init_bias(4096),

    'fc_3_weights': init_weights(4096, 1000),
    'fc_3_bias': init_bias(1000),

    'softmax_weights': init_weights(1000, 100),
    'softmax_bias': init_bias(100),

}


FLAGS = tf.app.flags.FLAGS


with tf.name_scope('reshape'):
    x = tf.reshape(image, shape=[-1, 32, 32, 3])

# 32

with tf.name_scope('conv_block_1'):
    conv_1 = conv2d('conv_1', x, parameters['conv_1_filter'], parameters['conv_1_bias'])
    conv_2 = conv2d('conv_2', conv_1, parameters['conv_2_filter'], parameters['conv_2_bias'])
    pool_1 = maxpool('pool_1', conv_2, 2, 2)

#   16 * 16 * 64
with tf.name_scope('conv_block_2'):
    conv_3 = conv2d('conv_3', pool_1, parameters['conv_3_filter'], parameters['conv_3_bias'])
    conv_4 = conv2d('conv_4', conv_3, parameters['conv_4_filter'], parameters['conv_4_bias'])
    pool_2 = maxpool('pool_2', conv_4, 2, 2)
    x = batch_norm(pool_2)


#   8 * 8 * 128
with tf.name_scope('conv_block_3'):
    conv_5 = conv2d('conv_5', x, parameters['conv_5_filter'], parameters['conv_5_bias'])
    conv_6 = conv2d('conv_6', conv_5, parameters['conv_6_filter'], parameters['conv_6_bias'])
    conv_7 = conv2d('conv_7', conv_6, parameters['conv_7_filter'], parameters['conv_7_bias'])
    pool_3 = maxpool('pool_3', conv_7, 2, 2)
    x = batch_norm(pool_3)

#   4 * 4 * 256
with tf.name_scope('conv_block_4'):
    conv_8 = conv2d('conv_8', x, parameters['conv_8_filter'], parameters['conv_8_bias'])
    conv_9 = conv2d('conv_9', conv_8, parameters['conv_9_filter'], parameters['conv_9_bias'])
    conv_10 = conv2d('conv_10', conv_9, parameters['conv_10_filter'], parameters['conv_10_bias'])
    pool_4 = maxpool('pool_4', conv_10, 2, 2)
    x = batch_norm(pool_4)

#   2 * 2 * 512
with tf.name_scope('conv_block_5'):
    conv_11 = conv2d('conv_11', x, parameters['conv_11_filter'], parameters['conv_11_bias'])
    conv_12 = conv2d('conv_12', conv_11, parameters['conv_12_filter'], parameters['conv_12_bias'])
    conv_13 = conv2d('conv_13', conv_12, parameters['conv_13_filter'], parameters['conv_13_bias'])
    pool_5 = maxpool('pool_5', conv_13, 2, 2)
    x = batch_norm(pool_5)

#   1 * 1 * 512
x = tf.reshape(x, [-1, 512])
#   512

with tf.name_scope('fc'):
    fc_1 = fc('fc_1', x, parameters['fc_1_weights'], parameters['fc_1_bias'])
    fc_2 = fc('fc_2', fc_1, parameters['fc_2_weights'], parameters['fc_2_bias'])
    fc_3 = fc('fc_3', fc_2, parameters['fc_3_weights'], parameters['fc_3_bias'])
    output = tf.matmul(fc_3, parameters['softmax_weights'])
    output = tf.add(output, parameters['softmax_bias'])


with tf.name_scope('loss'):
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=label, logits=output)
    cross_entropy = tf.reduce_mean(cross_entropy)
    tf.summary.scalar('loss',cross_entropy)

with tf.name_scope('accuracy'):
    correct_prediction = tf.equal(tf.argmax(output, 1), tf.argmax(label, 1))
    correct_prediction = tf.cast(correct_prediction, tf.float32)
    accuracy = tf.reduce_mean(correct_prediction)
    tf.summary.scalar('accuracy', accuracy)


with tf.name_scope('optimizer'):
    train_step = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(cross_entropy)

init = tf.global_variables_initializer()
# path = '/home/jurh/disk/temp/cifar100/cifar-100-python/'
# path = '/Users/vic/Dev/DeepLearning/Paddle/DeepLearningWithPaddle/GoogLeNet/data/'
path = FLAGS.data_path
cifar = dataset.CIFAR(path + 'train', path + 'test')


with tf.Session() as sess:
    sess.run(init)
    step = 1
    while step <= FLAGS.epoch:
        loss = 0
        for i in range(1+50000/FLAGS.batch_size):
            batch_images, batch_labels = cifar.next_batch(FLAGS.batch_size)
            train_step.run(feed_dict={image: batch_images, label: batch_labels})
            loss += sess.run(cross_entropy, feed_dict={image: batch_images, label: batch_labels})

            if i % 5 == 0:
                train_accuracy = accuracy.eval(feed_dict={image: batch_images, label: batch_labels})
                print("Epoch: %s Batch: %s Loss: %s Accuracy: %s" % (step, i, loss/(i+1), train_accuracy))

        batch_test_images, batch_test_labels = cifar.test_batch(FLAGS.batch_size)
        test_accuracy = accuracy.eval(feed_dict={image: batch_test_images, label: batch_test_labels})
        print("[Testing Accuracy]: %.3f" % test_accuracy)
        step += 1



