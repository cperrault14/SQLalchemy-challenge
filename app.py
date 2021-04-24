#Dependencies
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from gevent.pywsgi import WSGIServer


# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#Flask setup
app = Flask(__name__)

#Flask Route
#Home Page
#List all routes that are available

@app.route("/")
def home():
    print("Server active for Home Page")
    return (
        f"Welcome to the SQL-Alchemy APP API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0<start>/<end><br>"
    ) 

# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    all_precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    precip_dict = dict(all_precip)
    return jsonify(precip_dict)

session.close()

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    all_stations = (session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())
    list_stations = list(np.ravel(all_stations))
    return jsonify(stations_list)

session.close()

# /api/v1.0/tobs
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    all_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').all()
    list_tobs = list(all_tobs)
    return jsonify(list_tobs)

session.close()

# /api/v1.0/<start> 
# /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def start(start):
    all_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    list_start = list(all_start)
    return jsonify(list_start)

session.close()

# Start_End
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    start_end = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    list_start_end = list(start_end)
    return jsonify(list_start_end)

# Wrap it up
if __name__ == '__main__':
    app.run(debug=True)
    
http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()