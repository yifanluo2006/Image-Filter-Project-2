from flask import Flask, request, jsonify, Response, send_file
import jwt
from pymongo import MongoClient
from gridfs import GridFS
from dotenv import load_dotenv
import os
import base64
import bcrypt

from auth_middleware import token_required

from bson.objectid import ObjectId

from flask_cors import CORS

from bson.objectid import ObjectId

from auth_middleware import token_required

import tensorflow as tf
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
import numpy as np
import cv2
from skimage.graph import route_through_array
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

CORS(app)

SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
#print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY


# Initialize GridFS for file storage
fs = GridFS(db)

@app.route('/image', methods=['POST'])
def insert_img():
    try:
        if 'image' in request.files:
            image = request.files['image']
            name = request.form.get("name", "")  
            description = request.form.get("description", "")  
            user_id = request.form.get("user_id", "")  
            fileName = request.form.get("fileName", "") 

           
            if not ObjectId.is_valid(user_id):
                return jsonify({"error": "Invalid user ID format"})

            
            image_path = 'img.jpg'
            image.save(image_path)

            # GridFS file and insert to MongoDB 
            with open(image_path, 'rb') as image_file:
                image_id = fs.put(image_file, filename=image.filename, name=name, description=description)

            
            result = collection.insert_one({
                'image_file_id': image_id,
                'ifImage': 'Yes',
                'name': name,
                'description': description,
                'user_id': user_id,
                'fileName':fileName  
            })

            
            return jsonify({"message": "Image uploaded successfully", "imageID": str(result.inserted_id)})
        else:
            return jsonify({"error": "No image file provided in the request"})
    except Exception as e:
        return jsonify({"error": str(e)})




if __name__ == '__main__':
    app.run(debug=True)




