# Import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create instance of Flask app
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

# Route to query Mongo database and render index.html template 
@app.route('/')
def index():
    # Find one record of data from Mongo database
    mars = mongo.db.mars_mission.find_one()
    # Return template and data
    return render_template('index.html', mars=mars)

# Route /scrape to import scrape_mars.py script and call scrape function;
# store return value in Mongo as Python dictionary.
@app.route('/scrape')
def scrape():
    mars = mongo.db.mars_mission
    # Run the scrape function
    data = scrape_mars.scrape()

    # Update Mongo database  
    # update() method is deprecated; using replace_one
    mars.replace_one(
        {},
        data,
        upsert=True
    )

    # Redirect back to home page
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
