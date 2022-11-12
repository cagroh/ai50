import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4

# CG: nice progress bar:
#from tqdm import tqdm


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    # CG: initiate resulting lists:
    images = list()
    labels = list()
    filenames = list()
    badreads  = list()
    
    # CG: let's signal we're working:
    print (f"Searching for image files in {data_dir}...")

    #CG: assume that data_dir will contain one directory named after each category, numbered 0 through NUM_CATEGORIES - 1:
    # CG: nice progress bar:
    #for cat in tqdm(range(NUM_CATEGORIES)):
    for cat in range(NUM_CATEGORIES):

        # CG: build search_dir by adding the category number to the starting dir:
        search_dir = data_dir + os.sep + str(cat) + os.sep

        # CG: walk down the directory tree:
        for root, dirs, files in os.walk(search_dir):

            # CG: get a list of all files in the directory:
            names = [(os.path.join(root,f)) for f in files]

            # CG: ignore empty entries:
            if len(names) == 0:
                continue

            # CG: add an entry in the arrays for each file found:
            for f in names:

                # CG: load the image file:
                img = cv2.imread (f, cv2.IMREAD_UNCHANGED)

                # CG: if failed, add to badreads list: 
                if img is None:
                    badreads.append (f)
                    continue

                # CG: add filename to list of valid files:
                filenames.append(f)

                # CG: resize the image to the desired sizes:
                img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))

                # CG: convert the image to RGB color scheme:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # CG: add the image to the list:
                images.append(img)

                # CG: add the corresponding categorie to the list:
                labels.append(cat)

    # CG: return the lists:
    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    
    # CG: create the model as Sequential:
    model = tf.keras.models.Sequential()

    # CG: add a convolutional layer. Learn 32 filters using a 4x4 kernel, shaping input according to given image parameters:
    model.add (tf.keras.layers.Conv2D(32, (4, 4), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)))

    # CG: add a convolutional layer. Learn 32 filters using a 2x2 kernel:
    model.add (tf.keras.layers.Conv2D(32, (2, 2), activation="relu"))

    # CG: max-pooling layer, using 2x2 pool size:
    model.add (tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))

    # CG: flatten units:
    model.add (tf.keras.layers.Flatten())

    # CG: add a hidden layer with 32X32X3 (3072) neurons and 1/3% dropout:
    model.add (tf.keras.layers.Dense(3072, activation="relu"))
    model.add (tf.keras.layers.Dropout(1/2))

    # CG: add a hidden layer with 1024 neurons:
    model.add (tf.keras.layers.Dense(1024, activation="relu"))

    # CG: add a hidden layer with 512 neurons:
    model.add (tf.keras.layers.Dense(512, activation="relu"))

    # CG: add a hidden layer with 256:
    model.add (tf.keras.layers.Dense(256, activation="relu"))

    # CG: add a hidden layer with 128:
    model.add (tf.keras.layers.Dense(128, activation="relu"))
    #model.add (tf.keras.layers.Dropout(1/3))

    # CG: add a hidden layer with 64:
    model.add (tf.keras.layers.Dense(64, activation="relu"))
    #model.add (tf.keras.layers.Dropout(1/3))

    # CG: add an output layer with output units for all NUM_CATEGORIES categories:
    model.add (tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax"))

    # CG: compile the model
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # CG: return the compiled model:
    return model


if __name__ == "__main__":
    main()
