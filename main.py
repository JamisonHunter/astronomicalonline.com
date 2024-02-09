# Imports
from flask import Flask, render_template
from pymongo import MongoClient
from random import randint
from datetime import datetime, timedelta
from bson import ObjectId
import os

app = Flask(__name__, static_folder='static')

my_secret = os.environ['MONGO_URI']


# Routes
# Home
@app.route("/")
def index():
  # Connect to MongoDB
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Query MongoDB to find the document with the most recent date
  most_recent_image = collection.find_one(sort=[("Date", -1)])

  # Get the date of the most recent image
  date_current = most_recent_image["Date"]

  # Query MongoDB for the documents with the dates of the two previous days
  date_1 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=1)
  date_2 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=2)

  image_1 = collection.find_one({"Date": date_1.strftime("%Y-%m-%d")})
  image_2 = collection.find_one({"Date": date_2.strftime("%Y-%m-%d")})

  return render_template("index.html",
                         image=most_recent_image,
                         image_1=image_1,
                         image_2=image_2)


# About
@app.route("/about")
def about():
  # Connect to MongoDB
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Get the total number of documents in the collection
  total_images = collection.count_documents({})

  # Generate a random index within the range of total images
  random_index = randint(0, total_images - 1)

  # Query MongoDB to get a random document
  random_image = collection.find().limit(-1).skip(random_index).next()

  return render_template("about.html", image=random_image)


# Random Image
@app.route("/random")
def random():
  # Connect to MongoDB
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Get the total number of documents in the collection
  total_images = collection.count_documents({})

  # Generate a random index within the range of total images
  random_index = randint(0, total_images - 1)

  # Query MongoDB to get a random document
  random_image = collection.find().limit(-1).skip(random_index).next()

  return render_template("image_details.html", image=random_image)


# Image Details
@app.route("/image_details/<image_id>")
def image_details(image_id):
  # Connect to MongoDB
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Query MongoDB to find the document with the specified image ID
  image = collection.find_one({"_id": ObjectId(image_id)})
  return render_template("image_details.html", image=image)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
