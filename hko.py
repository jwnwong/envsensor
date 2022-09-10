from time import sleep
import requests, csv, io
import json, datetime
import sqlite3

def storehko(measure,rows):
    
    with sqlite3.connect('dht.db') as connection: 
        cursor = connection.cursor()
        for r in rows:
            [date, time, station, measure, value]= r
            try:
                value = float(value)
            except:
                value = 'NULL'
  
            update_values = f'"{date}","{time}","{station}","{measure}",{value}'
            sql_stmt = "insert into hko values("+update_values+")"
            
            cursor.execute(sql_stmt)
        cursor.close()

    connection.close()
    
    return

def gethko(measure='temperature'):

    if measure == 'temperature':
        url = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_temperature.csv"
    elif measure == 'humidity':
        url = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_humidity.csv"
    elif measure == 'pressure':
        url = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_pressure.csv"
    else:
        return []
    
    with requests.get(url) as req:
        if (req.status_code == 200):
            rows = [ [  f'{r[0][:4]}-{r[0][4:6]}-{r[0][6:8]}',      # date
                        f'{r[0][8:10]}:{r[0][10:12]}:00',           # time
                        r[1], measure, r[2] ]
                 for r in csv.reader(io.StringIO(req.text))][1:]
        
        else:
            print(f"Tried but: {req.status_code}")
            return []
    return rows 

def findlastupdate(measure):
    with sqlite3.connect('dht.db') as connection: 
        cursor = connection.cursor()
        
        cursor.execute(f'select max(date), max(time) from hko where measure = "{measure}" and date = (select max(date) from hko)')
        record = cursor.fetchone()
        cursor.close()
    connection.close()    
    if record[0] is None or record[1] is None: 
        return "2000-01-01 00:00:00"
    else:
        return record[0]+" "+record[1]




if __name__ == '__main__':
    
    exitflag = False
    
    while not exitflag:

        for measure in ['temperature','humidity','pressure']:
            # send request to HKO
            last_update = findlastupdate(measure)
            rows=gethko(measure)
            if type(rows) == list and len(rows) > 0:
                if rows[0][0] + " " + rows[0][1] != last_update:
                    storehko(measure,rows)
                    last_update = rows[0][0]+" "+rows[0][1]
                    print(f'{measure} updated at: {last_update}')
                else:
                    print(f'{measure} has no update')
            
        sleep(60*5) 
