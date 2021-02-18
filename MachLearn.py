import tensorflow as tf
from data_base import DataBaseManager as dbm
import numpy as np
#TODO TE->Rushing and Receiving:->age->g->gs->TGT->Y/Rec->REC1D->RECLng->CtchPct->Y/Tch->Fmb ;;;; Training data
#TODO Fantasy:->FantPt ;;;; training predictioin

class MachineLearningClass():
    def __init__(self):
        pass

    def StartML(self):
        database = dbm()
        database.keras_data()

        # rush_receive_list = database.df.values.tolist()
        # rush_receive_array = np.array(rush_receive_list)
        rush_receive_array = database.df.to_numpy()
        x_train = rush_receive_array[:, 1: 11]
        y_train = rush_receive_array[:, 0]
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
        # predictions = model(x_train[:1]).numpy()
        # print(predictions)
        # print(tf.nn.softmax(predictions).numpy())
        #
        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        # print(loss_fn(y_train[:1], predictions).numpy())

        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        model.fit(x_train, y_train, epochs=80000, batch_size=10)
        # # model.evaluate(x_test, y_test, verbose=2)
        # probability_model = tf.keras.Sequential([
        #     model,
        #     tf.keras.layers.Softmax()
        # ])
        # # print(probability_model(x_test[:5]))
        _, accuracy = model.evaluate(x_train, y_train)
        print('Accuracy: %.2f' % (accuracy * 100))

MLC = MachineLearningClass()
MLC.StartML()