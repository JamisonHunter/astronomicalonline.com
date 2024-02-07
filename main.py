# app.py
from flask import Flask, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
import creds

app = Flask(__name__, static_folder='static')

# Connect to MongoDB
client = MongoClient(creds.MONGO_URI)
db = client["astronomy"]
collection = db["apod"]


@app.route("/")
def index():
  # Get date
  date_current = "2024-02-06"
  date_1 = "2024-02-05"
  date_2 = "2024-02-04"

  # Query MongoDB for the document with date
  main_image = collection.find_one({"Date": date_current})
  image_1 = collection.find_one({"Date": date_1})
  image_2 = collection.find_one({"Date": date_2})

  return render_template("index.html",
                         image=main_image,
                         image_1=image_1,
                         image_2=image_2)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
