from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage
import numpy as np
import tensorflow as tf
from PIL import Image

interpreter1 = tf.lite.Interpreter(model_path="model_unquant1.tflite")
interpreter1.allocate_tensors()

input_details1 = interpreter1.get_input_details()
output_details1 = interpreter1.get_output_details()

# Load labels
def load_labels(label_path):
    with open(label_path, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    return labels

label_path1 = "labels1.txt"  # Path to your labels file
labels1 = load_labels(label_path1)

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


@app.route('/test/<message>')
def test_method(message):
  print(message)
  return jsonify(message)


@app.route('/name/<name>')
def say_hi(name):
  print("hello, my name is " + name)
  return jsonify("success")


# {"num1": int, "num2": int}
@app.route('/addnums', methods=['POST'])
def add_two():
  try:
    data = request.json
    if data is not None:
      answer = data['num1'] + data['num2']
      return jsonify({"answer": answer})
    else:
      return jsonify({"msg": "invalid json"})
  except Exception as e:
    return jsonify({"error": e})


@app.route('/nameage', methods=['POST'])
def retrun_nameage():
  try:
    data = request.json
    if data is not None:
      name = str(data['name'])
      age = int(data['age'])
      return jsonify("Hello, my name is " + name + ", and I am " + str(age) +
                     " years old.")
    else:
      return jsonify({"msg": "invalid json"})
  except Exception as e:
    return jsonify({"error": e})


@app.route('/test', methods=['POST'])
def test():
  return jsonify({"name": "Yifan"})


@app.route('/downloadImage', methods=['POST'])
def download():
  try:
    data = request.json
    if data is not None:
      filename = str(data['file'])

      url = storage_manager.exists_on_cloud(filename)
      if url:
        print(f'The file exists on the cloud. URL: {url}')
      else:
        print('The file does not exist on the cloud.')

      source = filename
      destination = 'new_image.JPG'
      storage_manager.download_file(source, destination)

      return jsonify({"Message": "Download Successful!"})

  except Exception as e:
    return jsonify({"error": e})

@app.route('/analyzeImage1',methods=['POST'])
def analyze1():
  try:
    data = request.json
    if data is not None:
      file = str(data['file'])
      input_shape = input_details1[0]['shape']
      input_image = np.array(Image.open(file).resize((input_shape[1], input_shape[2])))
      input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension if needed
      input_image = input_image.astype(np.float32)  # Convert to float32 if needed

      # Set input tensor
      interpreter1.set_tensor(input_details1[0]['index'], input_image)

      # Run inference
      interpreter1.invoke()

      # Get output tensor
      output_data = interpreter1.get_tensor(output_details1[0]['index'])

      # Interpret results with labels
      top_prediction_index = np.argmax(output_data, axis=1)

      top_prediction_label = labels1[top_prediction_index[0]]

      return jsonify({"Top prediction label": top_prediction_label})
    else:
      return jsonify({"Message:": "Invalid Format"})
  except Exception as e:
    return jsonify({"error": e})

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000)
