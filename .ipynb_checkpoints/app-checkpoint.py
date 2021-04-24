{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Dependencies\n",
    "import numpy as np\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func\n",
    "from flask import Flask, jsonify\n",
    "from gevent.pywsgi import WSGIServer\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "# create engine to hawaii.sqlite\n",
    "engine = create_engine(\"sqlite:///Resources/hawaii.sqlite\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "# reflect an existing database into a new model\n",
    "Base = automap_base()\n",
    "# reflect the tables\n",
    "Base.prepare(engine, reflect=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "['measurement', 'station']"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# View all of the classes that automap found\n",
    "Base.classes.keys()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Save references to each table\n",
    "Measurement = Base.classes.measurement\n",
    "Station = Base.classes.station"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create our session (link) from Python to the DB\n",
    "session = Session(engine)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Flask setup\n",
    "app = Flask(__name__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Flask Route\n",
    "#Home Page\n",
    "#List all routes that are available\n",
    "\n",
    "@app.route(\"/\")\n",
    "def home():\n",
    "    print(\"Server active for Home Page\")\n",
    "    return (\n",
    "        f\"Welcome to the SQL-Alchemy APP API!<br/>\"\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"/api/v1.0/tobs<br/>\"\n",
    "        f\"/api/v1.0/<start><br>\"\n",
    "        f\"/api/v1.0<start>/<end><br>\"\n",
    "    ) \n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "# /api/v1.0/precipitation\n",
    "# Convert the query results to a dictionary using date as the key and prcp as the value.\n",
    "# Return the JSON representation of your dictionary.\n",
    "\n",
    "@app.route(\"/api/v1.0/precipitation\")\n",
    "def precipitation():\n",
    "    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    all_precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()\n",
    "    precip_dict = dict(all_precip)\n",
    "    return jsonify(precip_dict)\n",
    "\n",
    "session.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "# /api/v1.0/stations\n",
    "# Return a JSON list of stations from the dataset.\n",
    "@app.route(\"/api/v1.0/stations\")\n",
    "def stations():\n",
    "    all_stations = (session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())\n",
    "    list_stations = list(np.ravel(all_stations))\n",
    "    return jsonify(stations_list)\n",
    "\n",
    "session.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "# /api/v1.0/tobs\n",
    "# Query the dates and temperature observations of the most active station for the last year of data.\n",
    "# Return a JSON list of temperature observations (TOBS) for the previous year.\n",
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def tobs():\n",
    "    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    all_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').all()\n",
    "    list_tobs = list(all_tobs)\n",
    "    return jsonify(list_tobs)\n",
    "\n",
    "session.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "# /api/v1.0/<start> \n",
    "# /api/v1.0/<start>/<end>\n",
    "# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.\n",
    "# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.\n",
    "# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.\n",
    "@app.route(\"/api/v1.0/<start>\")\n",
    "def start(start):\n",
    "    all_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()\n",
    "    list_start = list(all_start)\n",
    "    return jsonify(list_start)\n",
    "\n",
    "session.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Start_End\n",
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "def start_end(start, end):\n",
    "    start_end = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()\n",
    "    list_start_end = list(start_end)\n",
    "    return jsonify(list_start_end)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      "   Use a production WSGI server instead.\n",
      " * Debug mode: on\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Restarting with windowsapi reloader\n"
     ]
    },
    {
     "ename": "SystemExit",
     "evalue": "1",
     "output_type": "error",
     "traceback": [
      "An exception has occurred, use %tb to see the full traceback.\n",
      "\u001b[1;31mSystemExit\u001b[0m\u001b[1;31m:\u001b[0m 1\n"
     ]
    }
   ],
   "source": [
    "# Wrap it up\n",
    "if __name__ == '__main__':\n",
    "    app.run(debug=True)\n",
    "    \n",
    "http_server = WSGIServer(('', 5000), app)\n",
    "http_server.serve_forever()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:root] *",
   "language": "python",
   "name": "conda-root-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
