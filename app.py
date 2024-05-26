from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage
import numpy as np
import tensorflow as tf
from PIL import Image

import os
import cv2
from cv2filters import Filters

filters = Filters()



interpreter1 = tf.lite.Interpreter(model_path="model_unquant1.tflite")
interpreter1.allocate_tensors()

input_details1 = interpreter1.get_input_details()
output_details1 = interpreter1.get_output_details()

interpreter2 = tf.lite.Interpreter(model_path="model_unquant2.tflite")
interpreter2.allocate_tensors()

input_details2 = interpreter2.get_input_details()
output_details2 = interpreter2.get_output_details()

interpreter3 = tf.lite.Interpreter(model_path="model_unquant3.tflite")
interpreter3.allocate_tensors()

input_details3 = interpreter3.get_input_details()
output_details3 = interpreter3.get_output_details()

# Load labels
def load_labels(label_path):
    with open(label_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    return labels

label_path1 = "labels1.txt"  # Path to your labels file
labels1 = load_labels(label_path1)

label_path2 = "labels2.txt"  # Path to your labels file
labels2 = load_labels(label_path2)

label_path3 = "labels3.txt"  # Path to your labels file
labels3 = load_labels(label_path3)

class StorageManager:
  def __init__(self, bucket_name, fb_cred_path):
    self.bucket_name = bucket_name
    self.fb_cred_path = fb_cred_path

    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(self.fb_cred_path)
    firebase_admin.initialize_app(cred, {
      'storageBucket': self.bucket_name
    })

  def exists_on_cloud(self, file_name):
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    return blob.exists() and blob.public_url

  def upload_file(self, file_name, local_path):
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(local_path)
    print('This file is uploaded to cloud.')
    blob.make_public()
    return blob.public_url

  def download_file(self, source, destination):
    bucket = storage.bucket()
    blob = bucket.blob(source)
    blob.download_to_filename(destination)

project_id = 'filter-39761'
bucket_name = f'{project_id}.appspot.com'
fb_cred_path = 'info.json'

storage_manager = StorageManager(bucket_name, fb_cred_path)

app = Flask(__name__)

# ------------------------------------ API ------------------------------------------
@app.route('/')
def index():
  return 'Hello from Flask!'

# @app.route('/downloadImage', methods=['POST'])
# def download():
#   try:
#     data = request.json
#     if data is not None:
#       filename = str(data['file'])
#
#       url = storage_manager.exists_on_cloud(filename)
#       if url:
#         print(f'The file exists on the cloud. URL: {url}')
#       else:
#         print('The file does not exist on the cloud.')
#
#       source = filename
#       destination = 'new_image.JPG'
#       storage_manager.download_file(source, destination) # downloading to machine
#
#       return jsonify({"Message": "Download Successful!"})
#
#   except Exception as e:
#     return jsonify({"error": e})

@app.route('/analyze', methods=['POST'])
def analyze():
  # Grab Image
  try:
    data = request.json
    if data is not None:
      file = str(data['file'])
      input_shape = input_details1[0]['shape']
      input_image = np.array(Image.open(file).resize((input_shape[1], input_shape[2])))
      input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension if needed
      input_image = input_image.astype(np.float32)  # Convert to float32 if needed

      # Call model 1
      # Set input tensor
      interpreter1.set_tensor(input_details1[0]['index'], input_image)

      # Run inference
      interpreter1.invoke()

      # Get output tensor
      output_data1 = interpreter1.get_tensor(output_details1[0]['index'])

      # Interpret results with labels
      top_prediction_index1 = np.argmax(output_data1, axis=1)

      top_prediction_label1 = labels1[top_prediction_index1[0]]

      # Call model 2
      # Set input tensor
      interpreter2.set_tensor(input_details2[0]['index'], input_image)

      # Run inference
      interpreter2.invoke()

      # Get output tensor
      output_data2 = interpreter2.get_tensor(output_details2[0]['index'])

      # Interpret results with labels
      top_prediction_index2 = np.argmax(output_data2, axis=1)

      top_prediction_label2 = labels2[top_prediction_index2[0]]

      # Call model 3
      # Set input tensor
      interpreter3.set_tensor(input_details3[0]['index'], input_image)

      # Run inference
      interpreter3.invoke()

      # Get output tensor
      output_data3 = interpreter3.get_tensor(output_details3[0]['index'])

      # Interpret results with labels
      top_prediction_index3 = np.argmax(output_data3, axis=1)

      top_prediction_label3 = labels3[top_prediction_index3[0]]

      return jsonify({"Model 1": top_prediction_label1, "Model 2": top_prediction_label2, "Model 3": top_prediction_label3})
    else:
      return jsonify({"Message:": "Invalid Format"})
  except Exception as e:
    return jsonify({"error": e})

@app.route('/paintImage', methods=['POST'])
def paint():
    try:
      data = request.json
      if data is not None:
        img_path = str(data['file'])
        image = cv2.imread(img_path)

        painting_image = filters.painting(image)
        # cv2.imshow("Painted", painting_image)
        # cv2.waitKey(0)

        return jsonify({"Message": "Image Success"})
      else:
        return jsonify({"Message:": "Invalid Format"})
    except Exception as e:
      return jsonify({"error": e})

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000)