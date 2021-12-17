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
    cursor.execute("SELECT dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth, dlcdtimer, dalerttimer FROM pooltempconfig") 
    data=cursor.fetchall()
    return render_template('paramsv3.html', data = data, msg = "Change Parameters below then click 'Update'")

@app.route ('/update', methods=['GET', 'POST'])
def update():
    configuration_error = False
    conn = mariadb.connect(**config)
    cursor = conn.cursor()
    dmaxpooltemp=request.form['maxpooltemp']
    if not is_number(dmaxpooltemp):
        configuration_error = True
    else:
        dmaxpooltemp=float(dmaxpooltemp)
        if dmaxpooltemp < 20 or dmaxpooltemp > 36:
            configuration_error = True  
    dstarthour=request.form['starthour']
    dendhour=request.form['endhour']
    if not is_number(dstarthour) or not is_number(dendhour):
        configuration_error = True
    else:
        dstarthour=float(dstarthour)
        dendhour=float(dendhour)        
        if dstarthour > 24 or dstarthour > dendhour:
            configuration_error = True      
        if dendhour > 24 or dendhour < 1:
            configuration_error = True
    droofpooldelta=request.form['roofpooldelta']
    if not is_number(droofpooldelta):
        configuration_error = True
    else:
        droofpooldelta=float(droofpooldelta)
        if droofpooldelta > 10 or droofpooldelta < 0:
            configuration_error = True
    dsleeptime=request.form['sleeptime']
    if not is_number(dsleeptime):
        configuration_error = True
    else:
        dsleeptime=float(dsleeptime)
        if dsleeptime > 1200 or dsleeptime < 0:
            configuration_error = True
    dstartmonth=request.form['startmonth']
    if not is_number(dstartmonth):
        configuration_error = True
    else:
        dstartmonth=float(dstartmonth)
        if dstartmonth > 12 or dstartmonth < 1:
            configuration_error = True
    dendmonth=request.form['endmonth']
    if not is_number(dendmonth):
        configuration_error = True
    else:
        dendmonth=float(dendmonth)
        if dendmonth > 12 or dendmonth < 1:
            configuration_error = True 
    dlcdtimer=request.form['lcdtimer']
    if not is_number(dlcdtimer):
        configuration_error = True
    else:
        dlcdtimer=float(dlcdtimer)
        if dlcdtimer > 600 or dlcdtimer < 0:
            configuration_error = True     
    dalerttimer=request.form['alerttimer']
    if not is_number(dalerttimer):
        configuration_error = True
    else:
        dalerttimer=float(dalerttimer)
        if dalerttimer > 43200 or dalerttimer < 0:
            configuration_error = True 
    if not configuration_error:
        cursor.execute("UPDATE pooltempconfig set dmaxpooltemp='{}', dstarthour='{}', dendhour='{}',droofpooldelta='{}', dsleeptime='{}', dstartmonth='{}', dendmonth='{}', dlcdtimer='{}', dalerttimer='{}' where id='1'". format(dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth, dlcdtimer, dalerttimer))
        conn.commit()
    cursor.execute("SELECT dmaxpooltemp, dstarthour, dendhour, droofpooldelta, dsleeptime, dstartmonth, dendmonth, dlcdtimer, dalerttimer FROM pooltempconfig")
    data=cursor.fetchall()
    if configuration_error:
        return render_template('paramsv3.html', data = data, msg="Configuration Change - Out of Range")
    else:
        return render_template('paramsv3.html', data = data, msg="Configuration Updated")

#Determine if number
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass 
    return False

if __name__ == "__main__" :
    from waitress import serve
    serve(app, port=8880, host = '0.0.0.0')
