from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, storage

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
fb_cred_path = 'info2.json'

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
    filename = "DSC01906.JPG"

    url = storage_manager.exists_on_cloud(filename)
    if url:
        print(f'The file exists on the cloud. URL: {url}')
    else:
        print('The file does not exist on the cloud.')

    source = 'DSC00673.JPG'
    destination = 'new_image.JPG'
    storage_manager.download_file(source, destination)

    print("download successful")
  except Exception as e:
    return jsonify({"error": e})


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000)