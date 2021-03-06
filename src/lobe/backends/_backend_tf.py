import numpy as np

from PIL import Image
from .._results import PredictionResult

try:
    import tensorflow as tf
    from tensorflow.contrib import predictor
except ImportError:
    raise ImportError("ERROR: This is a TensorFlow model and requires tensorflow to be installed on this device. Please run\n\tpip install tensorflow\n")

class ImageClassificationModel():
    __input_key_image = 'Image'
    __output_key_confidences = 'Confidences'
    __output_key_prediction = 'Prediction'

    def __init__(self, signature):
        self.__model_path = signature.model_path
        self.__tf_predict_fn = None
        self.__labels = signature.classes

    def __load(self):
        self.__tf_predict_fn = predictor.from_saved_model(self.__model_path)

    def predict(self, image: Image.Image) -> PredictionResult:
        if self.__tf_predict_fn is None:
            self.__load()

        # Convert all values to range [0,1]
        np_image = np.asarray(image) / 255.

        # Add an extra axis onto the numpy array
        np_image = np_image[np.newaxis, ...]

        predictions = self.__tf_predict_fn({
                self.__input_key_image: np_image
                })

        confidences = predictions[self.__output_key_confidences][0]
        top_prediction = predictions[self.__output_key_prediction][0].decode('utf-8')

        return PredictionResult(labels=self.__labels, confidences=confidences, prediction=top_prediction)