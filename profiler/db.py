'''------------------------------------------------------------------------------------------------
Program:    db.py
Version:    0.2.1
Py Ver:     2.7
Purpose:    Database class for the pibike profiler program.

Dependents: json
            mysql.connector
            pandas
            time

Developer:  J. Berendt
Email:      support@73rdstreetdevelopment.co.uk

Comments:

Use:        >
            >

---------------------------------------------------------------------------------------------------
UPDATE LOG:
Date        Programmer      Version     Update
02.08.17    J. Berendt      0.1.0       Copied from rrfd_avatar module.
                                        Commented the following methods:
                                            - create(), insert(), user_exists(), _close()
07.08.17    J. Berendt      0.1.1       Added docstrings to each applicable method / function.
                                        Added try/except block to connect().
                                        Updated player_delete query to change status to 'DELETED'
                                        rather than removing the record from the database.
                                        Updated queue query to pull records where the status does
                                        not equal 'COMPLETE' or 'DELETED'.
                                        Moved player_move, player_delete and now_playing methods
                                        from app.py, to this module.  pylint(10/10)
09.08.17    J. Berendt      0.2.0       Copied from the scoreboard interface and adpated to the
                                        profiler program.
                                        Added profile_to_be_created() function.
                                        Added new_profile_data() funtion.
                                        Added update_profiled_flag() method.
25.08.17    J. Berendt      0.2.1       Generalised company branding for github. pylint (10/10)
------------------------------------------------------------------------------------------------'''

import json
import pandas as pd
import mysql.connector


class DBConn(object):

    #-------------------------------------------------------------------
    #INITIALISATION
    def __init__(self, db_config_file):

        #READ IN CONFIG FILES
        self._db_config = json.loads(open(db_config_file).read())
        self._config    = json.loads(open('config.json').read())


    #-------------------------------------------------------------------
    #FUNCTION RETURNS THE DB CONNECTION OBJECT
    def connect(self):

        '''
        DESIGN:
        A dictionary containing the database login credentials are kept
        in the db_config.json file, which is read into the
        self._db_config variable on class instantiation.

        This dictionary is passed into the mysql.connector.connect()
        function as a **kwargs argument.
        '''

        try:
            #RETURN A CONNECTION TO THE DATABASE
            return mysql.connector.connect(**self._db_config)

        except Exception as err:
            #NOTIFICATION
            print 'ERR: Could not connect to the database.'
            print 'ERR: %s' % err


    #-------------------------------------------------------------------
    #FUNCTION TO TEST IF ANY PLAYERS NEED A PROFILE CREATED
    def profile_to_be_created(self):

        '''
        DESIGN:
        This function is designed to return a boolean value if a new
        profile graph needs to be created by counting the number of
        database records with a 'profiled' value of 0.
        '''

        try:
            #CONNECT TO DB >> GET CURSOR OBJECT
            conn = self.connect()
            cur = conn.cursor()

            #READ QUERY
            qry = open(self._config['qry_count_profile']).read()

            #GET DATA
            cur.execute(qry)
            res = cur.fetchone()[0]

            #CLOSE CONNECTION
            conn.close()

            #RETURN BOOLEAN VALUE
            return False if res == 0 else True

        except Exception as err:
            #NOTIFICATION
            print 'ERR: An error occurred while testing if any profile graphs should be created.'
            print 'ERR: %s' % err

            return False


    #-------------------------------------------------------------------
    #FUNCTION USED TO GET DATA FOR A NEW PROFILE GRAPH
    def new_profile_data(self):

        '''
        PURPOSE:
        This function returns a dataframe used to create the player's
        profile graph.

        DESIGN:
        Using the _profile_to_be_created() function, the database is
        tested for players with a 'profiled' value of 0.  (profile needs
        to be created)

        Then the profile data is gathered and returned to the program
        to be plotted.
        '''

        try:
            #CONNECT TO DB >> GET CURSOR OBJECT
            conn = self.connect()

            #READ QUERY
            qry = open(self._config['qry_getdata_profile']).read()

            #GET DATA >> AS SERIES
            df = pd.read_sql(qry, conn)

            #CLOSE DB CONNECTION
            conn.close()

            #RETURN DATA
            return df

        except Exception as err:
            #NOTIFICATION
            print 'ERR: An error occurred while gathering the profile data.'
            print 'ERR: %s' % err

            #RETURN AN EMPTY DATAFRAME
            return pd.DataFrame()


    #-------------------------------------------------------------------
    #METHOD USED TO UPDATE THE PROFILE FLAG, AFTER GRAPH IS CREATED
    def update_profiled_flag(self, alias):

        try:
            #CONNECT TO DB >> GET CURSOR OBJECT
            conn = self.connect()
            cur = conn.cursor()

            #READ QUERY
            qry = open(self._config['qry_update_profiled']).read()

            #UPDATE PROFILED FLAG
            cur.execute(qry, (alias, ))

            #COMMIT >> CLOSE DB CONNECTION
            conn.commit()
            conn.close()

        except Exception as err:
            #NOTIFICATION
            print 'ERR: An error occurred while updating a player\'s profiled flag. \n' \
                   'Player: %s' % alias
            print 'ERR: %s' % err
            #ROLLBACK
            conn.rollback()
