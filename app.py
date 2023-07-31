import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta as td
# import scipy.stats as st

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Static Routes
@app.route("/")
def home():
    html = (
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/<start><br>"
        "/api/v1.0/<start>/<end><br>"
    )
    return html

@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date.today() - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    precipitation_dict = {date: prcp for date, prcp in precipitation}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station, Station.name).all()

    stations_dict = {station: name for station, name in stations}
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    one_year_ago = dt.date.today() - dt.timedelta(days=365)

    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()

    tobs_dict = {date: tobs for date, tobs in tobs_data}
    return jsonify(tobs_dict)

# Dynamic routes
@app.route("/api/v1.0/<start>")
def start_date(start):
    summary_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    summary = list(np.ravel(summary_stats))
    
    return jsonify({
        "Start Date": start,
        "TMIN": summary[0],
        "TAVG": summary[1],
        "TMAX": summary[2]
    })

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    summary_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    summary = list(np.ravel(summary_stats))
    
    return jsonify({
        "Start Date": start,
        "End Date": end,
        "TMIN": summary[0],
        "TAVG": summary[1],
        "TMAX": summary[2]
    })

# Run server
if __name__ == "__main__":
    app.run(debug=True, port=5001)
