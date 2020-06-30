import sqlite3
from collections import namedtuple 
from threading import RLock 

db = sqlite3.connect('sensor-data.db', check_same_thread=False)
db_lock = RLock()

Measurement = namedtuple("Measurement", "sensor_id epoch_time value")
Sensor = namedtuple("Sensor", "sensor_id sensor_hw_id sensor_desc sensor_type")

db.execute("""
    CREATE TABLE IF NOT EXISTS sensors (
        sensor_id INTEGER PRIMARY KEY, 
        sensor_hw_id TEXT NOT NULL, 
        sensor_desc TEXT NOT NULL,
        sensor_type TEXT NOT NULL
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        sensor_id INTEGER NOT NULL, 
        epoch_time INTEGER NOT NULL,
        value REAL NOT NULL,
        FOREIGN KEY(sensor_id) REFERENCES sensors(sensor_id)
    )
""")
db.commit()

all_sensors = None

def get_all_sensors():
    with db_lock:
        global all_sensors
        if all_sensors: 
            return all_sensors

        c =  db.cursor()
        all_sensors = [Sensor(*row) for row in c.execute("SELECT * FROM sensors")]
        return all_sensors 

def get_sensor_by(sensor_id=None, sensor_hw_id=None):
    global all_sensors
    if sensor_id:
        for sensor in all_sensors:
            if sensor.sensor_id == sensor_id:
                return sensor 
    if sensor_hw_id:
        for sensor in all_sensors:
            if sensor.sensor_hw_id == sensor_hw_id:
                return sensor 

def declare_sensor(sensor_hw_id, sensor_desc, sensor_type):
    with db_lock: 
        c =  db.cursor()
        for sensor in get_all_sensors():
            if sensor.sensor_hw_id == sensor_hw_id and sensor.sensor_type == sensor_type:
                c.execute("UPDATE sensors SET sensor_desc = ? WHERE sensor_id = ?", (sensor_desc, sensor.sensor_id))
                return sensor 
        c.execute(
            "INSERT INTO sensors (sensor_hw_id, sensor_desc, sensor_type) VALUES (?, ?, ?)", 
            (sensor_hw_id, sensor_desc, sensor_type)
        )
        c.execute("SELECT last_insert_rowid()")
        db.commit()
        sensor_id = c.fetchone()[0]
        all_sensors = None 

    return Sensor(sensor_id, sensor_hw_id, sensor_desc, sensor_type)

def insert_measurement(measurement):
    with db_lock:
        c = db.cursor()
        c.execute("INSERT INTO measurements VALUES (?, ?, ?)", (measurement.sensor_id, measurement.epoch_time, measurement.value))

def query_measurements(start_time=None, end_time=None, limit=None, sensor_id=None, sensor_hw_id=None):
    conditions = []
    bindings = []

    if start_time:
        conditions.append("epoch_time >= ?")
        bindings.append(start_time)
    
    if end_time:
        conditions.append("epoch_time <= ?")
        bindings.append(start_time)

    if sensor_hw_id:
        sensor_id = get_sensor_by(sensor_hw_id=sensor_hw_id).sensor_id 
    
    if sensor_id:
        conditions.append("sensor_id = ?")
        bindings.append(sensor_id)

    if len(conditions) == 0:
        query = "SELECT * FROM measurements"
    else:
        query = "SELECT * FROM measurements WHERE " + " AND ".join(conditions)
    
    if limit:
        query.append(" LIMIT ?")
        bindings.append(limit)
    
    with db_lock:
        c = db.cursor()
        return [Measurement(*record) for record in c.execute(query, bindings)]

def commit():
    db.commit()