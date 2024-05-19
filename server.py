import firebase_admin
from firebase_admin import credentials, initialize_app, firestore, storage

# cred = credentials.Certificate("info.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

import firebase_admin
from firebase_admin import credentials, storage
from flask import Flask, jsonify, request

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
filename = "DSC01906.JPG"
localpath = "DSC01906.JPG"

# url = storage_manager.exists_on_cloud(filename)
# if url:
#     print(f'The file exists on the cloud. URL: {url}')
# else:
#     print('The file does not exist on the cloud.')

source = 'DSC00673.JPG'
destination = 'new_image.JPG'
storage_manager.download_file(source,destination)

# uploaded_url = storage_manager.upload_file(filename, localpath)
# print(f'File uploaded. Public URL: {uploaded_url}')

# word = input("Give me a word: ")
# newDoc = db.collection("Words").document(word)
# newDoc.set({
#   "word": word
# })

# word = input("Give me a word: ")
# doc = db.collection("Words").document(word)
# doc_info = doc.get().to_dict()
#
# if doc_info:
#     print(doc_info['word'])
# else:
#     print("word not found")

# col = db.collection("Words")
# for doc in col.stream():
#     print(doc.to_dict())

# old_word = input("Give me a word: ")
# new_word = input("Give me a new word: ")
#
# doc = db.collection("Words").document(old_word)
# doc_info = doc.get().to_dict() #verify that the document exists
# # print(doc_info)
#
# if doc_info:
#     doc.update({
#         "word": new_word
#     })
# else:
#     print("word not found")

# word = input("Give me a word: ")
# doc = db.collection("Words").document(word)
# doc.delete()

# big_word = input("Give me a big word: ")
# little_word = input("Give me a little word: ")
# new_doc = db.collection("Words").document(big_word).collection("Little Words").document(little_word)
# new_doc.set({
#   "word": little_word
# })

# big_word = input("Give me a big word: ")
# little_word = input("Give me a little word: ")
# new_word = input("Give me a new word: ")
#
# doc = db.collection("Words").document(big_word).collection("Little Words").document(little_word)
# doc_info = doc.get().to_dict() #verify that the document exists
# # print(doc_info)
#
# if doc_info:
#     doc.update({
#         "word": new_word
#     })
# else:
#     print("word not found")