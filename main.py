# Imports
from flask import Flask, render_template, request, redirect, url_for
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
  # Connecting to MongoDB.
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Querying MongoDB to find the document with the most recent date.
  most_recent_image = collection.find_one(sort=[("Date", -1)])

  # Getting the date of the most recent image
  date_current = most_recent_image["Date"]

  # Query MongoDB for the documents with the dates of the previous days.
  date_1 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=1)
  date_2 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=2)
  date_3 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=3)
  date_4 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=4)
  date_5 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=5)
  date_6 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=6)
  date_7 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=7)
  date_8 = datetime.strptime(date_current, "%Y-%m-%d") - timedelta(days=8)

  image_1 = collection.find_one({"Date": date_1.strftime("%Y-%m-%d")})
  image_2 = collection.find_one({"Date": date_2.strftime("%Y-%m-%d")})
  image_3 = collection.find_one({"Date": date_3.strftime("%Y-%m-%d")})
  image_4 = collection.find_one({"Date": date_4.strftime("%Y-%m-%d")})
  image_5 = collection.find_one({"Date": date_5.strftime("%Y-%m-%d")})
  image_6 = collection.find_one({"Date": date_6.strftime("%Y-%m-%d")})
  image_7 = collection.find_one({"Date": date_7.strftime("%Y-%m-%d")})
  image_8 = collection.find_one({"Date": date_8.strftime("%Y-%m-%d")})

  # Querying MongoDB to get available dates.
  available_dates = collection.distinct("Date")

  return render_template("index.html",
                         image=most_recent_image,
                         image_1=image_1,
                         image_2=image_2,
                         image_3=image_3,
                         image_4=image_4,
                         image_5=image_5,
                         image_6=image_6,
                         image_7=image_7,
                         image_8=image_8,
                         available_dates=available_dates)


# About
@app.route("/about")
def about():
  # Connecting to MongoDB.
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Getting the total number of documents in the collection.
  total_images = collection.count_documents({})

  # Generating a random index within the range of total images.
  random_index = randint(0, total_images - 1)

  # Querying MongoDB to get a random document.
  random_image = collection.find().limit(-1).skip(random_index).next()

  return render_template("about.html", image=random_image)


# Random Image
@app.route("/random")
def random():
  # Connect to MongoDB
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Getting the total number of documents in the collection.
  total_images = collection.count_documents({})

  # Generating a random index within the range of total images.
  random_index = randint(0, total_images - 1)

  # Querying MongoDB to get a random document.
  random_image = collection.find().limit(-1).skip(random_index).next()

  return render_template("image_details.html", image=random_image)


# Image Details
@app.route("/image_details/<image_id>")
def image_details(image_id):
  # Connecting to MongoDB.
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Querying MongoDB to find the document with the specified image ID.
  image = collection.find_one({"_id": ObjectId(image_id)})
  return render_template("image_details.html", image=image)


# Search
@app.route("/search", methods=["POST"])
def search():
  search_date = request.form.get("searchDate")

  # Performing database query to find images for the selected date.
  client = MongoClient(my_secret)
  db = client["astronomy"]
  collection = db["apod"]

  # Querying MongoDB to find the image with the selected date.
  selected_image = collection.find_one({"Date": search_date})

  if selected_image:
    # If an image is found, redirect to the image details page.
    return redirect(
        url_for("image_details", image_id=str(selected_image["_id"])))
  else:
    return render_template("error.html",
                           message="No image found for the selected date.")


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
