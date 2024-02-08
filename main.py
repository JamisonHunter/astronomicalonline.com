# Imports
from flask import Flask, render_template
from pymongo import MongoClient
import pandas as pd
import requests
import schedule
from random import randint
from datetime import datetime, timedelta
from bson import ObjectId
import threading
import time
import creds

app = Flask(__name__, static_folder='static')


def updatedb():
  api_key = creds.NASA_API_KEY

  today = datetime.today().strftime("%Y-%m-%d")

  # Define the endpoint URL for the APOD API
  apod_url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}&date={today}'

  # Make a GET request to the APOD API
  response = requests.get(apod_url)

  apod_data = {}

  if response.status_code == 200:
    apod_data = response.json()
  else:
    print("Failed to retrieve data from the APOD API.")
    return

  # Extract relevant information
  title = apod_data.get('title', '')
  date = apod_data.get('date', '')
  explanation = apod_data.get('explanation', '')
  image_url = apod_data.get('url', '')

  # Connect to MongoDB
  client = MongoClient(creds.MONGO_URI)
  db = client["astronomy"]
  collection = db["apod"]

  # Check if the record for today already exists in the database
  if collection.find_one({"Date": date}):
    print("Record for today already exists in the database.")
    return

  # Create a pandas DataFrame with the data for today's image
  df = pd.DataFrame({
      'Title': [title],
      'Date': [date],
      'Explanation': [explanation],
      'Image URL': [image_url]
  })

  # Convert DataFrame to dictionary
  data_dict = df.to_dict(orient='records')

  # Insert the record into the MongoDB collection
  collection.insert_many(data_dict)

  print("Data inserted successfully into MongoDB.")


def schedule_daily_update():
  schedule.every().day.at("23:00").do(updatedb)

  # Keep the program running to allow the scheduler to continue executing
  while True:
    schedule.run_pending()
    time.sleep(60)


# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=schedule_daily_update)
scheduler_thread.start()


# Routes
@app.route("/")
def index():
  # Connect to MongoDB
  client = MongoClient(creds.MONGO_URI)
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


@app.route("/about")
def about():
  return render_template("about.html")


@app.route("/random")
def random():
  # Connect to MongoDB
  client = MongoClient(creds.MONGO_URI)
  db = client["astronomy"]
  collection = db["apod"]

  # Get the total number of documents in the collection
  total_images = collection.count_documents({})

  # Generate a random index within the range of total images
  random_index = randint(0, total_images - 1)

  # Query MongoDB to get a random document
  random_image = collection.find().limit(-1).skip(random_index).next()

  return render_template("image_details.html", image=random_image)


@app.route("/image_details/<image_id>")
def image_details(image_id):
  # Connect to MongoDB
  client = MongoClient(creds.MONGO_URI)
  db = client["astronomy"]
  collection = db["apod"]

  # Query MongoDB to find the document with the specified image ID
  image = collection.find_one({"_id": ObjectId(image_id)})
  return render_template("image_details.html", image=image)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
