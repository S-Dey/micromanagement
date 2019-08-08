import pickle, time
from flask import Flask, render_template,url_for, request, redirect, flash
from time import gmtime, strftime
from googleapiclient.discovery import build
from datetime import datetime
from httplib2 import Http
from oauth2client import file, client, tools
from google.auth.transport.requests import Request

# Storage for input from forms
class Storage:
    focuslist = []
    locationlist = []
    desclist = []
    timelist = []
    @staticmethod
    def getFocus(focuslist):
        return focuslist[0]

    @staticmethod
    def getLocation(locationlist):
        return locationlist[0]

    @staticmethod
    def getDesc(desclist):
        return desclist[0]

    @staticmethod
    def getTime(timelist):
        return timelist[0]

    @staticmethod
    def clearLists(focuslist, locationlist, desclist, timelist):
        focuslist.clear()
        locationlist.clear()
        desclist.clear()
        timelist.clear()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        focus = request.form['focus']
        location = request.form['location']
        desc = request.form['desc']
        start_time = strftime("%Y-%m-%dT%H:%M:%S") # Start time for gcal
        setter = Storage()
        setter.focuslist.append(focus)
        setter.locationlist.append(location)
        setter.desclist.append(desc)
        setter.timelist.append(start_time)
        try:
            startTime = datetime.now().strftime('%H:%M') # Start time that is displayed to user
            return render_template('taskongoing.html', startTime = startTime, focus = focus)
        except:
            flash('Error adding your input! Task is not added to your calendar.')
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/taskongoing', methods = ['POST', 'GET'])
def taskongoing():
    if request.method == 'POST':
        createEvent()
        return render_template('index.html')
    else:
        return render_template('taskongoing.html')

def createEvent():
    getter = Storage()
    rtime = getter.timelist
    rfocus = getter.focuslist
    rlocation = getter.locationlist
    rdesc = getter.desclist
    start_time = getter.getTime(rtime)
    focus = getter.getFocus(rfocus)
    location = getter.getLocation(rlocation)
    desc = getter.getDesc(rdesc)
    end_time = strftime("%Y-%m-%dT%H:%M:%S")
    getter.clearLists(rfocus, rlocation, rdesc, rtime)
    '''
    for some reason argparse wont work in heroku

    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None
    '''
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('storage.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        #creds = tools.run_flow(flow, store, flags) if flags else tools.run(flow, store)    tools is also interfering with heroku

    CAL = build('calendar', 'v3', http=creds.authorize(Http()))
    
    TIMEZONE = 'Europe/Helsinki'

    EVENT = {
        'summary' : focus,
        'location' : location,
        'description' : desc,
        'start' : {
            'dateTime' : start_time, 'timeZone' : TIMEZONE,  
        },
        'end' : {
            'dateTime': end_time, 'timeZone' : TIMEZONE,
        }
    }

    e = CAL.events().insert(calendarId='primary', body=EVENT).execute()
    try:
        e.get('htmlLink')
        flash('Task added to your calendar!')

    except Exception:
        flash('There was an error adding your task to calendar!')
        

if __name__ == "__main__":
    app.run(debug=True)