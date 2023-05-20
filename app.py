# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, abort


#################################################
# Database Setup
#################################################
engine= create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base= automap_base
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement= Base.classes.measurement
Station= Base.classes.station

# Create our session (link) from Python to the DB
#*MY ANSWER* rather than do this I did as we learned in the Module 10 session on Flask to close each
#session after the route. 

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f'Enter a "(start date)" or a "(start date) / (end date)" for temperatures during those dates <br/>'
        f'Format: YYYY-MM-DD<br/>'
        f'/api/v1.0/&nbsp&nbsp&nbsp"(start date)/(end date)"'
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session= Session(engine)

    search_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    Precipitation_one_year= session.query(Measurement.date, Measurement.prcp) .\
        filter(Measurement.date >= search_date).order_by(Measurement.date).all()
    
    session.close()

    precipitation_dict= {date: prcp for date, prcp in Precipitation_one_year}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def station():
    session= Session(engine)

    weather_stations= session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    weather_stations_long= []
    for row in weather_stations_long:
        weather_stations_dict= {}
        weather_stations_dict["ID"]= row.station
        weather_stations_dict["Name"]= row.name
        weather_stations_dict["Lat"]= row.latitude
        weather_stations_dict["Long"]= row.longitude
        weather_stations_dict["Elevation"]= row.elevation
        weather_stations_long.append(weather_stations_dict)

    session.close()

    weather_json= jsonify(weather_stations_long)
    return (weather_json)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    search_date= dt.date(2017, 8, 23)- dt.timedelta(days=365)

    Temperature_one_year= session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= search_date).\
    filter(Measurement.station == 'USC00519281').all()

    Temperature_one_year_dict= {}

    for row in Temperature_one_year:
        Temperature_one_year_dict[row.date] = row.tobs

    session.close()

    Temperature_one_year_json= jsonify(Temperature_one_year_dict)
    return(Temperature_one_year_json)

@app.route("/api/v1.0/<start>")
def station_temps(start):
    sessions= Session(engine)

    min_max_mean = session.query(Station.station, Station.name, func.min(Measurement.tobs), \
        func.max(Measurement.tobs), func.avg(Measurement.tobs)).group_by(Station.station) .\
        filter(Measurement.station == Station.station).filter(Measurement.date >= start).all()
    
    session.close()
    
    station_temps_dict={result[0]: {"name": result[1], "min_temp": result[2], "max_temp": result[3],\
                         "avg_temp": result[4]} for result in min_max_avg}
    
    station_temps_json= jsonify(station_temps_dict)
    return(station_temps_json)

@app.route("/api/v1.0/<start>/<end>")
def station_temps_end(start, end):
    sessions= Session(engine) 

    min_max_mean= session.query(Station.station, Station.name, func.min(Measurement.tobs), \
            func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs))).group_by(Station.station).\
            filter(Measurement.station == Station.station).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    station_temp_dict = {result[0]: {"name": result[1], "min_temp": result[2], "max_temp": result[3],\
                         "avg_temp": result[4]} for result in min_max_avg}
    
    station_temp_json= jsonify(station_temp_dict)
    return(station_temp_json)

#I included this because we did it in the all the examples on Flask. Please give me feedback if it isn't
#necessary!

if __name__ == '__main__':
    app.run(debug= True)
