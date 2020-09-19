from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

# create engine
engine = create_engine('sqlite:///hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
# step 1:
app = Flask(__name__)
@app.route("/")
def helloWorld():
    # urls that tell the user the end points that are available
    return "Hello World"

@app.route("/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    lastdayInDB = dt.date(2017, 8, 20)
    lastdayminusoneyear = lastdayInDB - dt.timedelta(days=365)
    lastyearsResults = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >=lastdayminusoneyear).all()
    session.close()

#Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
  #Return the JSON representation of your dictionary
    results = []
    for date, prcp in lastyearsResults:
        result_dict = {}
        result_dict["Date"] = date
        result_dict["Precipitation"] = prcp
        
        results.append(result_dict)
    
    return jsonify(results)
    # return "Hi"
    
@app.route("/stations")
def stations():
    #return a list of all station in JSON
    stationlist = session.query(Station.station).all()
    stationOneDim = list(np.ravel(stationlist))
    session.close()
    return jsonify(stationOneDim)
    
    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/tobs")
def tobs():
    session = Session(engine)
    lastdayInDB = dt.date(2017, 8, 20)
    lastdayminusoneyear = lastdayInDB - dt.timedelta(days=365)
    lastyeartemp = session.query(Measurement.station, Measurement.tobs).filter(Measurement.date >=lastdayminusoneyear).\
    filter(Measurement.station == 'USC00519281').all()
    tobsOneDim = list(np.ravel(lastyeartemp))
    session.close()
    return jsonify(tobsOneDim)

# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
@app.route("/<start_date>")
#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
def calc_temps(start_date):
    session = Session(engine)
    tempstart = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    tempravel = list(np.ravel(tempstart))
    session.close()
    
    return jsonify(tempravel)

@app.route("/<start_date>/<end_date>")
def calc_temps2(start_date, end_date):
    session = Session(engine)
    tempend = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    tempravel2 = list(np.ravel(tempend))
    session.close()
    return jsonify(tempravel2)



#2nd step:
if __name__ == '__main__':
    app.run(debug=True)