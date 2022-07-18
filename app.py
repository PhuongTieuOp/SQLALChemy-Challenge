from flask import Flask, jsonify, request

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func, desc, asc
import numpy as np
import pandas as pd
import datetime as dt

######################################################################
# Make database connection
######################################################################

# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model; Declare a Base using `automap_base()`
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references (classed) to each table
Msm = Base.classes.measurement
Stn = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"<h2>Welcome to Hawaii Climate explorer! </h2> "
        f"<h3>Data date range 01/01/2010-23/08/2017 </h3> "
        f"<h3>Available Routes:</h3>"
        f"<h3> * /api/v1.0/precipitation - Precipitation (prcp) in last 12 months</h3>"        
        f"<h3>* /api/v1.0/tobs - Temperature (tobs) in last 12 months</h3>" 
        f"<h3>* /api/v1.0/stations - Prcp and tobs reading stations</h3>" 
        f"<h3>* /api/v1.0/query?<start>&<end> - Enter a start date, or start/end dates to search for TMIN, TMAX, TAVG, Count</h3>" 
        f"<h3>  ie. /api/v1.0/query?start=2017-05-01; or /api/v1.0/query?start=2017-05-01&end=2017-05-31 </h3>"
    )

# Display precipition in last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date 1 year ago from the last data point in the database
    sel =   [Msm.date, 
            Msm.prcp]
    prcp_12mths = session.query(*sel).\
        filter(func.strftime(Msm.date) > "2016-08-23").order_by(desc(Msm.date)).all()

    dict_prcp = {key:value for key,value in prcp_12mths}    
    session.close()
    return jsonify(dict_prcp)

# Display station list for precipation and temperature readings
@app.route("/api/v1.0/stations")
def stations():
    # Calculate the date 1 year ago from the last data point in the database
    sel =   [Stn.station, 
            Stn.name]
    stations = session.query(*sel).all()

    dict_station = {key:value for key,value in stations}    
    session.close()
    return jsonify(dict_station)

# Display tobs for last 12months
@app.route("/api/v1.0/tobs")
def tobs():
   # Calculate the date 1 year ago from the last data point in the database
    sel =   [Msm.date, 
            Msm.tobs]
    tobs_12mths = session.query(*sel).\
        filter(func.strftime(Msm.date) >= "2016-08-23").order_by(desc(Msm.date)).all()

    dict_tobs = {key:value for key,value in tobs_12mths}    
    session.close()
    return jsonify(dict_tobs)

# Display tobs for a date range from ascending order
@app.route("/api/v1.0/query")
def tobs_range():    
    start = request.args.get('start')
    end = request.args.get('end')

    # setup select string for the query
    sel =   [func.min(Msm.tobs),
            func.max(Msm.tobs),
            func.avg(Msm.tobs),
            func.count(Msm.tobs)]

    if start != None:
        if end != None:
            tobs = session.query(*sel).filter(Msm.date >= start, Msm.date <= end).all()
        else:           
            tobs = session.query(*sel).filter(Msm.date >= start).all()

    tobs = list(tobs[0])    
    keys = ["Min Temperature", "Max Temperature", "Avg Temperature", "Count Temperature"]
    dict_tobs = {key: value for key, value in zip(keys, tobs)}

    session.close()
    return jsonify(dict_tobs)

if __name__ == "__main__":
    app.run(debug=True)
