#!/usr/bin/env python

#import urllib
import json
import os
from os import environ

from flask import Flask
from flask import request
from flask import make_response

import pypyodbc
import sqlite3

# Flask app should start in global layout
from SurveyWebProject import app
#app = Flask(__name__)

# Global variables
global_debug = 'Y'
my_dir = os.path.dirname(__file__)
database = '\home\site\wwwroot\data\survey.db'
#database = '/home/liamwba/mysite/survey.db' for debugging on PythonAnywhere

# Procedure used to output debug messages to the log
def debug(debugmsg):
    if global_debug is 'Y':
        print(debugmsg)

# Creates a connection to the SQLITE database
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    debug('Inside create_connection')

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return None

def ConnectAzureDB():
    azcon = pypyodbc.connect(
            'Driver={ODBC Driver 13 for SQL Server};' +
            'Server=lbpsdbserver.database.windows.net;' +
            #    'Port=5432;' +
            'Database=lbPulseSurveyDB;' +
            'Uid=lbadmin;' +
            'Pwd=Digital123;')
    return azcon

def InsertAzure():
    cnxn = ConnectAzureDB()
    crsr = cnxn.cursor()
    val1 = 'api.ai'
    val2 = 'test from api.ai'
    sql = """
    INSERT INTO details (role,team) VALUES (?, ?)
    """
    crsr.execute(sql, (val1,val2))
    cnxn.commit()
    #select here
    crsr.close()
    cnxn.close()

#Insert data from survey into sqlite database
def insert_survey_details(unit,area,role,team,department,account,company):
    debug('Inside insert_survey_details') #remove debug
    con = create_connection(database)
    cur = con.cursor()
    sql = '''INSERT INTO details (unit, area, role, team, department, account, company)
             VALUES (?,?,?,?,?,?,?) '''
    cur.execute(sql, (unit,area,role,team,department,account,company,))
    con.commit()
    con.close()

#Update record to append comments
def update_survey_details(comments,unit,area,role,team):
    debug('Inside update_survey_details') #remove debug
    con = create_connection(database)
    cur = con.cursor()
    sql = '''UPDATE details SET comments = ?
             WHERE unit = ?
             AND area = ?
             AND role = ?
             AND team = ?
             AND date_created = (select max(date_created) from details)  '''
    cur.execute(sql, (comments,unit,area,role,team,))
    con.commit()
    con.close()

#TODO finish csv output
def survey_details_csv():
    test1 = 'testing'
    test2 = 'testing2'
    f = open('survey_details.csv', 'a+')
    f.write(test1 + ',' + test2 + '\n')
    f.close()


def create_list(role,team,department,account,company):
    response_list = list()
    response_list.extend([role,team,department,account,company])
    return response_list

def generate_response(response_list):
    better_count = 0
    same_count = 0
    worse_count = 0
    for x in response_list:
        if x == 'Better':
            better_count += 1
        else:
            if x == 'Same':
                same_count += 1
            else:
               # if x == 'Worse':
                    worse_count += 1

    if better_count >= 3:
        speech = "We're pleased that you feel better overall, could you let us know why? (Press enter to submit)"
    else:
        if worse_count >= 3:
            speech = "We've noticed that you feel worse overall, could you let us know why? (Press enter to submit)"
        else:
            speech = 'Please enter any other comments (Press enter to submit)'

            print (speech)

    return speech

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#Extact parameters from the input JSON and pass to the insert procedure
def makeWebhookResult(req):
#    if req.get("result").get("action") != "survey.complete":
#       return {}
    result = req.get("result")
    parameters = result.get("parameters")
    debug(parameters) #remove debug
    unit = parameters.get("unit")
    area = parameters.get("area")
    role = parameters.get("role")
    team = parameters.get("team")
    department = parameters.get("department")
    account = parameters.get("account")
    company = parameters.get("company")
    if req.get("result").get("action") == "survey.complete":
        debug('UPDATE SQLITE')
        comments = parameters.get("comments")
        update_survey_details(comments,unit,area,role,team)
        speech = "Thanks for taking the pulse survey. Your responses have been recorded. (API)"
    else:
        if req.get("result").get("action") == "survey.initial":
            debug("INSERT SQLITE")
      #      InsertAzure()
            insert_survey_details(unit,area,role,team,department,account,company)
            response_list = create_list(role,team,department,account,company)
            speech = generate_response(response_list)
        else:
            return{}

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-pulse-survey"
    }

#Required for Docker
 #   if __name__ == "__main__":
 #       app.run(host='0.0.0.0')

'''if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)'''
