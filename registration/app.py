'''------------------------------------------------------------------------------------------------
Program:    app
Package:    1.2.1
Py Ver:     2.7
Purpose:    This program runs the user registration web interface for the digital engine simulator.

Dependents: sys
            json
            time
            datetime
            flask
            db

Developer:  J. Berendt
Email:      support@73rdstreetdevelopment.co.uk

Comments:

Use:        To start the web interface:
            > python app.py

            In a browser, go to 127.0.0.1:5000
            [the host ip and port number are defined in config.json]

---------------------------------------------------------------------------------------------------
UPDATE LOG:
Date        Programmer      Version     Update
27.07.17    J. Berendt      0.0.1       Written  pylint(10/10)
27.07.17    J. Berendt      0.1.0       Updated version number to match package.
                                        Updated to use db fields as described in the design doc.
28.07.17    J. Berendt      0.1.1       MODULE: None
                                        DATABASE:
                                        Updated avatardata id field name to rownum.
28.07.17    J. Berendt      0.1.2       MODULE:
                                        Updated img2blob() to use the program dir for replace,
                                        rather than a value in the config. pylint (10/10)
                                        DATABASE:
                                        Updated schema name to digitalenginesimulator, to match
                                        deployment environment.
02.08.17    J. Berendt      0.1.3       MODULE:
                                        Added the port number to the config file.
                                        HTML:
                                        Updated css to use company colours.
04.08.17    J. Berendt      1.0.0       MODULE:
                                        Moved the CFG global constant declaration to main().
                                        Added docstring documentation to each method / function.
                                        pylint (10/10)
07.08.17    J. Berendt      1.1.0       Added -v and --version arguments, for CLI version
                                        display.
25.08.17    J. Berendt      1.2.0       Generalised company branding for github
                                        Added host, debug and treaded keys/values to config.json
                                        Added license and readme files for program design and use.
                                        Added seahorse to animal selection ... as a github joke.
                                        pylint (10/10)
08.09.17    J. Berendt      1.2.1       Updated the avatardata table creation script to include
                                        the 'completiontime' field.
                                        Updated the README to include guidance for displaying the
                                        UI on a portable device.
------------------------------------------------------------------------------------------------'''

import json
import os
import sys
import time

from datetime import datetime as dt
from flask import Flask, render_template, request
from db import DBConn
from _version import __version__


APP = Flask(__name__)
APP.secret_key = 'devkey'

#IGNORED DUE TO DBC AND CONFIG BEING VALID GLOBAL 'CONSTANTS'
#pylint: disable=global-variable-undefined



#-----------------------------------------------------------------------
#PROGRAM SETUP
def setup():

    '''
    PURPOSE:
    This function is used to read and return the config file as a
    dictionary.
    '''

    #READ CONFIG FILE INTO GLOBAL CONST
    return json.loads(open('config.json').read())


#-----------------------------------------------------------------------
#DATABASE SETUP
def db_setup():

    '''
    PURPOSE:
    Using the db.DBConn() class, this method is used to create the
    avatardata database table, if the table does not already exist.
    '''

    global DBC

    #CREATE DB INSTANCE
    DBC = DBConn('db_config.json')
    #ENSURE TABLE(S) IS/ARE CREATES
    DBC.create()


#-----------------------------------------------------------------------
#OPEN RESTRATION FORM
@APP.route('/', methods=['GET', 'POST'])
def registration():

    '''
    PURPOSE:
    This method loads the main registration page.
    '''

    return render_template('registration.html')


#-----------------------------------------------------------------------
#METHOD FOR ADDING A RECORD TO THE DATABASE
@APP.route('/add_rec', methods=['GET', 'POST'])
def add_record():

    '''
    PURPOSE:
    When the user clicks 'Register' on the registration page, this
    method loads the user's selections into the avatardata table of
    the MySQL database.

    DESIGN:
    The db.py module and its DBConn class are used to perform all
    database related tasks.

    Before a new record is added, the following tests are performed:
        - the user must have selected an avatar
        - the user chosen alias *must not* already exist in the db

    If both tests are passed, the record is added to the database and
    the user is informed of their alias.
    '''

    #TEST REQUEST TYPE
    if request.method == 'POST':

        try:

            #INITIALISE
            response = ''
            msg = ''

            #STORE ALIAS NAME
            alias = build_alias(form_object=request.form)

            #TEST AVATAR WAS SELECTED
            if request.form['image_name'] != '':

                #EXTRACT USER VALUES FROM HTML FORM
                values = getuservalues(form_object=request.form)

                #TEST IF ALIAS WAS FOUND
                if DBC.user_exists(alias=alias) == 0:

                    #ADD NEW RECORD
                    DBC.insert(values=values)

                    #MESSAGE FOR WEB OUTPUT
                    msg = 'Your user alias has been registered successfully!  Thank you.'

                else:
                    #MESSAGE FOR WEBOUTPUT
                    msg = ('Sorry ... that alias (%s) has already been taken. ' \
                           'Please pick another one.' % alias)
                    #FAILURE FLAG FOR WEB
                    response = "FAIL"

            else:
                #MESSAGE FOR WEBOUTPUT
                msg = 'Sorry ... please select an avatar.'
                #FAILURE FLAG FOR WEB
                response = "FAIL"

        except Exception as err:
            #NOTIFICATION
            msg = 'ERR: Record not added. (%s)' % err

        #LOAD RESPONSE PAGE
        return render_template('response.html', msg=msg, alias=alias, response=response)


#-----------------------------------------------------------------------
#FUNCTION TO BUILD USER ALIAS
def build_alias(form_object):

    '''
    PURPOSE:
    This function is used to build the user alias, simply by
    concatinating the colour, animal and number strings together.
    '''

    colour = form_object['colour']
    animal = form_object['animal']
    number = form_object['number']

    return colour + animal + number


#-----------------------------------------------------------------------
#FUNCTION USED TO EXTRACT USER VALUES FROM HTML AND RETURN AS A TUPLE
def getuservalues(form_object):

    '''
    PURPOSE:
    This function is used to extract the user's selected values from
    the registration page.

    DESIGN:
    Epoch time is used to describe the user's queue position.  The
    epoch value is created using an integer conversion of the
    time module's time.time() function.

    The avatar image is converted to binary format using the local
    imb2blob() function.

    The user's STATUS and GAMEHIGHSCORE values are defaulted to
    'QUEUED' and 0.0, respectively.
    '''

    #GET USER VALUES
    datecreated     = dt.now()
    colour          = form_object['colour']
    animal          = form_object['animal']
    number          = form_object['number']
    name            = colour + animal + number
    queueposition   = int(time.time())
    email           = form_object['email'].lower()
    phone           = form_object['phone']
    avatar          = img2blob(form_object['image_name'])

    #RETURN WRAPPED VALUES
    return (datecreated, name, queueposition, 'QUEUED', 0.0, colour,
            animal, number, email, phone, avatar)


#-----------------------------------------------------------------------
#FUNCTION TO CONVERT A FILE (FROM FILENAME) TO BINARY (FOR BLOB STORAGE)
def img2blob(filename):

    '''
    PURPOSE:
    The img2blob() function is used to convert the passed image file
    to binary format.

    DESIGN:
    The selected avatar image's filename is returned from the
    jinja / html template to python as
    'http://127.0.0.1:5000/filename.ext'.  In order to convert the image
    into binary format, the actual directory path to the image is
    needed, for the open(filepath).read() function calls.

    To make this work, a simple str.replace() hack is used to replace
    the 'http://127.0.0.1:5000' with the program's __file__ variable,
    to get the program's execution directory.
    '''

    #STRING REPLACEMENT TO FROM HTML SITE TO ACTUAL IMAGE LOCATION
    fname = filename.replace(CFG['site'], os.path.dirname(os.path.realpath(__file__)))
    #RETURN BINARY VALUE
    return open(fname, 'rb').read()


#-----------------------------------------------------------------------
#MAIN CONTROLLER
def main():

    global CFG

    #READ THE CONFIG FILE INTO A GLOBAL CONSTANT
    CFG = setup()

    #DATABASE SETUP
    db_setup()

    #RUN IT!
    APP.run(host=CFG['host'], port=CFG['port'],
            debug=CFG['app_debug'],
            threaded=CFG['app_threaded'])


#-----------------------------------------------------------------------
#RUN PROGRAM
if __name__ == '__main__':

    #TEST FOR ARGUMENTS
    if len(sys.argv) == 2:
        if sys.argv[1] == '-v' or sys.argv[1] == '--version':
            #GET PROGRAM NAME
            NAME = os.path.splitext(sys.argv[0])
            #PRINT VERSION NUMBER
            print '{prog} - v{version}'.format(prog=NAME[0], version=__version__)
    else:
        #RUN PROGRAM
        main()
