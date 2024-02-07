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


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
