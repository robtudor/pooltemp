import mariadb
from flask import Flask, render_template, request
app = Flask( __name__ )

config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'accadm',
    'password': 'm2qiaa1253',
    'database': 'pooltemp'
}
@app .route( '/' )
def index():
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT date, time, rooftemp, pooltemp, pumpstate FROM pool_temp ORDER BY date DESC LIMIT 1")
    for date, time, rooftemp, pooltemp, pumpstate in cursor:
        bdate=str(date)
        btime=str(time)
        brooftemp=str(rooftemp)+"C"
        bpooltemp=str(pooltemp)+"C"
        header="Current Pool Temps "
    data = [ header, bdate, btime, brooftemp, bpooltemp, pumpstate ]
    return render_template('temperatures.html', data = data) 

@app .route( "/maxtemp" )
def maxtemp():
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT date, time, rooftemp, pooltemp, pumpstate FROM pool_temp WHERE date = DATE(NOW()) ORDER BY rooftemp DESC LIMIT 1 ")
    for date, time, rooftemp, pooltemp, pumpstate in cursor:
        bdate=str(date)
        btime=str(time)
        brooftemp=str(rooftemp)+"C"
        bpooltemp=str(pooltemp)+"C"
        header="Maximum Pool Temps "
    data = [header, bdate, btime, brooftemp, bpooltemp, pumpstate ]
    return render_template('temperatures.html', data = data)

@app .route( "/mintemp" )
def mintemp():
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT date, time, rooftemp, pooltemp, pumpstate FROM pool_temp WHERE date = DATE(NOW()) ORDER BY rooftemp ASC LIMIT 1 ")
    for date, time, rooftemp, pooltemp, pumpstate in cursor:
        bdate=str(date)
        btime=str(time)
        brooftemp=str(rooftemp)+"C"
        bpooltemp=str(pooltemp)+"C"
        header="Minimum Pool Temps "
    data = [header, bdate, btime, brooftemp, bpooltemp, pumpstate ]
    return render_template('temperatures.html', data = data)

@app .route( "/changeparam" )
def changeparam():
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth, dlcdtimer FROM pooltempconfig") 
    data=cursor.fetchall()
    return render_template('paramsv2.html', data = data, msg = "Change Parameters below then click 'Update'")

@app.route ('/update', methods=['GET', 'POST'])
def update():
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
    dmaxpooltemp=float(request.form['maxpooltemp'])
    dstarthour=int(request.form['starthour'])
    dendhour=int(request.form['endhour'])
    droofpooldelta=float(request.form['roofpooldelta'])
    dsleeptime=int(request.form['sleeptime'])
    dstartmonth=int(request.form['startmonth'])
    dendmonth=int(request.form['endmonth'])
    dlcdtimer=int(request.form['lcdtimer'])
    cursor.execute("UPDATE pooltempconfig set dmaxpooltemp='{}', dstarthour='{}', dendhour='{}',droofpooldelta='{}', dsleeptime='{}', dstartmonth='{}', dendmonth='{}', dlcdtimer='{}' where id='1'". format(dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth, dlcdtimer))
    conn.commit()
    cursor.execute("SELECT dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth, dlcdtimer FROM pooltempconfig")
    data=cursor.fetchall()
    return render_template('paramsv2.html', data = data, msg="Configuration Updated")

if __name__ == "__main__" :
    from waitress import serve
    serve(app, port=8880, host = '0.0.0.0')