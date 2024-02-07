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
  # Get today's date
  today = datetime.today().strftime('%Y-%m-%d')

  # Query MongoDB for the document with today's date
  today_image = collection.find_one({"Date": today})

  # Get the images for the previous six days
  six_days_ago = (datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d')
  previous_images = collection.find({
      "Date": {
          "$gte": six_days_ago,
          "$lt": today
      }
  }).sort("Date", -1).limit(6)

  return render_template("index.html",
                         image=today_image,
                         previous_images=previous_images)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)
