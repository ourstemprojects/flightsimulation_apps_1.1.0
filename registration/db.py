'''------------------------------------------------------------------------------------------------
Program:    db.py
Version:    1.0.1
Py Ver:     2.7
Purpose:    Database class for pibike registration program.

Dependents: json
            mysql.connector

Developer:  J. Berendt
Email:      support@73rdstreetdevelopment.co.uk

Comments:

Use:        From the app program:
            ---------------------
            import db

            dbc = db.DBConn('path/to/db.config')

            conn = dbc.connect()
            cur = conn.cursor()

---------------------------------------------------------------------------------------------------
UPDATE LOG:
Date        Programmer      Version     Update
25.07.17    J. Berendt      0.0.1       Written (development)
26.07.17    J. Berendt      0.0.2       Moved db table creation from the __init__ method to the
                                        create() method.  Process optimisation as the db tables
                                        should not be created EACH time a user registers.
                                        DB create script moved externally.  pylint (10/10)
27.07.17    J. Berendt      0.1.0       Updated version number to match package.
                                        Updated to use db fields as described in the design doc.
03.08.17    J. Berendt      1.0.0       Initial stable release.
                                        Added try/except block to the create() method.
                                        DB connection and cursor object creation moved inside the
                                        existing try/except blocks.
                                        Added docstrings to each method / function
                                        Extended header to 100 characters.  pylint (10/10)
25.08.17    J. Berendt      1.0.1       No functional changes.
                                        Generalised company branding for github.
------------------------------------------------------------------------------------------------'''

import json
import mysql.connector


class DBConn(object):

    '''
    PURPOSE:
    This class is used for all database actions for the registration
    program.

    DESIGN:
    On class instantiation, both the database and the program config
    files are read into class dictionary objects.

    USE:
    import db

    dbc = db.DBConn('path/to/db_config.json')

    conn = dbc.connect()
    cur = conn.cursor()
    '''

    #-------------------------------------------------------------------
    #INITIALISATION
    def __init__(self, db_config_file):

        '''
        DESIGN:
        On class instantiation, both the database and the program
        config files are read into class dictionary objects.
        '''

        #READ IN CONFIG FILES
        self._db_config = json.loads(open(db_config_file).read())
        self._config    = json.loads(open('config.json').read())


    #-------------------------------------------------------------------
    #FUNCTION RETURNS THE DB CONNECTION OBJECT
    def connect(self):

        '''
        DESIGN:
        The connect() function uses mysql.connector.connect() to make
        a connection to the database - passing in a dictionary of
        connection values.  This is the dictionary (.json file)
        initially passed into the class on instantiaion.
        '''

        return mysql.connector.connect(**self._db_config)


    #-------------------------------------------------------------------
    #ENSURE DB TABLE(S) IS/ARE CREATED
    def create(self):

        '''
        PURPOSE:
        This method is used to create the avatardata table.

        DESIGN:
        This method should be called *once* on program startup; perhaps
        from the main() method of the program.

        The create script is contained in the
        /db_resource/qry_create_avatardata.sql file.
        '''

        try:
            #CREATE CONNECTION AND CURSOR OBJECTS
            conn = self.connect()
            cur  = conn.cursor()

            #READ QUERY
            qry = open(self._config['qry_create_avatardata']).read()

            #EXECUTE / COMMIT / CLOSE CONNECTION
            cur.execute(qry)
            conn.commit()
            self._close(connection=conn)

        except Exception as err:
            #NOTIFICATION
            print 'ERR: An error occurred while creating the table.'
            print 'ERR: %s' % err


    #-------------------------------------------------------------------
    #METHOD USED TO INSERT DATA INTO THE DATABASE
    def insert(self, values):

        '''
        PURPOSE:
        The insert() method is used for inserting new registration
        data into the avatardata table.
        '''

        try:
            #CONNECT TO DB
            conn = self.connect()
            cur  = conn.cursor()

            #READ QUERY
            qry = open(self._config['qry_insert_avatardata']).read()

            #ADD NEW RECORD / COMMIT / CLOSE
            cur.execute(qry, values)
            conn.commit()

        except Exception as err:
            #ROLL BACK ON ERROR
            conn.rollback()
            #NOTIFICATION
            print 'ERR: An error occurred while inserting data.'
            print 'ERR: %s' % err

        finally:
            #CLOSE CONNECTION
            self._close(connection=conn)


    #-------------------------------------------------------------------
    #FUNCTION RETURNS ZERO IF THE USER DOES NOT EXIST
    def user_exists(self, alias):

        '''
        PURPOSE:
        This function is used to test if a name (alias) exists, before
        adding a new name (alias).
        '''

        #INITIALISE
        result = None

        try:
            #CONNECT TO DB
            conn = self.connect()
            cur = conn.cursor()

            #READ QUERY
            qry = open(self._config['qry_alias_exists']).read()

            #ADD NEW RECORD / COMMIT / CLOSE
            cur.execute(qry, (alias,))
            result = cur.fetchall()[0][0]

        except Exception as err:
            #NOTIFICATION
            print 'ERR: %s' % err

        finally:
            #CLOSE CONNECTION
            self._close(connection=conn)

        return result


    #-------------------------------------------------------------------
    #PRIVATE METHOD USED TO CLOSE A DB CONNECTION
    def _close(self, connection):

        '''
        PURPOSE:
        The _close() method is a 'private' method used to close a
        database connection.
        '''

        #:no-self-use (R0201): *Method could be a function*
        #pylint: disable=no-self-use

        connection.close()
