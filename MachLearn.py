import tensorflow as tf
from data_base import DataBaseManager as dbm
import numpy as np


# TODO TE->Rushing and Receiving:->age->g->gs->TGT->Y/Rec->REC1D->RECLng->CtchPct->Y/Tch->Fmb ;;;; Training data
# TODO Fantasy:->FantPt ;;;; training predictioin

class MachineLearningClass():
    def __init__(self):
        pass

    mnist = tf.keras.datasets.mnist
    mnist.load_data()

    def StartML(self):
        database = dbm()
        database.keras_data()

        # rush_receive_list = database.df.values.tolist()
        # rush_receive_array = np.array(rush_receive_list)
        rush_receive_array = database.df.to_numpy()
        x_train = rush_receive_array[:400, 1:11]
        y_train = rush_receive_array[:400, 0]
        x_test = rush_receive_array[400:, 1:11]
        y_test = rush_receive_array[400:, 0]
        # model = tf.keras.models.Sequential()
        # model.add(tf.keras.layers.Dense(12, input_dim=12, activation='relu'))
        # model.add(tf.keras.layers.Dense(12, activation='relu'))
        # model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
        # model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        # model.fit(x_train, y_train, epochs=150, batch_size=10)
        #
        # _, accuracy = model.evaluate(x_train, y_train)
        # print('Accuracy: %.2f' % (accuracy * 100))

        model = tf.keras.models.Sequential([
            # tf.keras.layers.Dense(12, input_dim=10, activation='relu'),
            tf.keras.layers.Dense(12, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10)
        ])
        # predictions = model(y_train).numpy()
        # print(predictions)
        # print(tf.nn.softmax(predictions).numpy())
        #
        # loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        # print(loss_fn(y_train, predictions).numpy())
        #
        # model.compile(optimizer='adam',
        #               loss=loss_fn,
        #               metrics=['accuracy'])

        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        model.fit(x_train, y_train, epochs=5, batch_size=10)
        # model.evaluate(x_test, y_test, verbose=2)
        # probability_model = tf.keras.Sequential([
        #     model,
        #     tf.keras.layers.Softmax()
        # ])
        # print(probability_model(x_test[:5]))
        _, accuracy = model.evaluate(x_test, y_test)
        print('Accuracy: %.2f' % (accuracy * 100))

    def diabetes(self):
        # load the dataset
        dataset = np.loadtxt('data/pima-indians-diabetes.csv', delimiter=',')
        # split into input (X) and output (y) variables
        X = dataset[:, 0:8]
        y = dataset[:, 8]
        # define the keras model
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(12, input_dim=8, activation='relu'))
        model.add(tf.keras.layers.Dense(8, activation='relu'))
        model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
        # compile the keras model
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        # fit the keras model on the dataset
        model.fit(X, y, epochs=150, batch_size=10)
        # evaluate the keras model
        _, accuracy = model.evaluate(X, y)
        print('Accuracy: %.2f' % (accuracy * 100))


MLC = MachineLearningClass()
MLC.diabetes()
