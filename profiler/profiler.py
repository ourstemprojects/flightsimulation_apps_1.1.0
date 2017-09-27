'''------------------------------------------------------------------------------------------------
Program:    profiler.py
Version:    0.3.0
Platform:   Windows / Linux
Py Ver:     2.7
Purpose:    This program creates the 'results for [player]' graph on the digital engine simulator
            scoreboard.

Dependents: datetime
            json
            os
            sys
            time
            db
            matplotlib
            numpy
            seaborn
            scipy
            _version

Developer:  J. Berendt
Email:      support@73rdstreetdevelopment.co.uk

Comments:

Use:        > python profiler.py

---------------------------------------------------------------------------------------------------
UPDATE LOG:
Date        Programmer      Version     Update
31.07.17    J. Berendt      0.0.1       Start of development.  pylint (10/10)
11.08.17    J. Berendt      0.1.0       First stable release.  pylint (10/10)
11.08.17    J. Berendt      0.2.0       Added the figure size into the config file.
                                        BUG01: Player profile graph has a black border.
                                        BUG02: Player profile graph does not fit inside the <div>
                                        on the linux laptop.
                                        FIX01: Added ax1.axis('off') to the graph setup.
                                        FIX02: Adjusted the figsize parameter of plt.figure().
11.08.17    J. Berendt      0.2.1       No functional changes.
                                        Updated target profile to make it more achievable.
25.08.17    J. Berendt      0.3.0       No functional changes.  pylint (10/10)
                                        Generalised company branding for github.
                                        Added GPL license file.
                                        Added readme file for design, deployment and use.
------------------------------------------------------------------------------------------------'''

#ALLOW OPENING DOCSTRING
#pylint: disable=pointless-string-statement

import json
import os
import sys
import time

from datetime import datetime as dt

import db
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from scipy.interpolate import spline
from _version import __version__


#-----------------------------------------------------------------------
#FUNCTION USED TO LOAD THE CONFIG FILE
def setup_config():

    return json.loads(open('config.json').read())


#-----------------------------------------------------------------------
#FUNCTION USED TO SETUP THE DATABASE CONNECTION
def setup_db():

    return db.DBConn(db_config_file='db_config.json')


#-----------------------------------------------------------------------
#FUNCTION USED TO CONVERT A BYTESTRING TO A LIST OF INTEGERS
def decode(df, col_name):

    '''
    RATIONALE:
    When the actual and target profiledata arrays are pulled from the
    database, they are returned to pandas as a bytearray. Basically
    meaning, an encoded literal string is returned, which cannot be
    used by the program as the program sees a string, rather than
    individual integer (of encoded) values.
    For example: bytearray[u'[95, 55, 23, 14, 23]'].  Notice the 'list'
    is enclosed by a unicode string.

    This function is used to decode and parse the bytearray string into
    a list of integer values which can be used by the program.
    '''

    #DECODE FROM HEX >> REPLACE SQ BARCKETS FROM STRING >> SPLIT
    decoded = df[col_name].str.decode('ascii')[0].replace('[', '').replace(']', '').split(', ')

    #CONVERT TO LIST OF INTEGERS >> RETURN LIST
    return [int(i) for i in decoded]


#-----------------------------------------------------------------------
#METHOD TO PLOT PLAYER RESULTS AGAINST TARGET
def create_graph(data, alias, score):

    '''
    PURPOSE:
    The create_graph() method uses matplotlib to create a profile
    graph for the pibike dashboard.

    The profile graph is designed to show the target profile, overlaid
    with the player's actual profile.  This data is collected from the
    digitalenginesimulator.gamedata table.

    DESIGN:
    Profile smoothing:
        The config file has two fields which control the smoothing of
        the player's profile.  This smoothing is *purely* for asthetics,
        as a 'smooth' line is more appealing than a 'jagged' line.
            - smooth_lines: boolean value to turn smoothing on/off
            - smooth_factor: integer value to tune the smoothness of the
              trend.  This value is the number of xaxis points - high
              values generate a smoother line.

    Output graphs:
        Two graph files are stored from this method:
        The first is for display on the scoreboard; so each new file
        will have the same filename as the last file.
        The second file contains the player's alias in the filename,
        and can be provided to the player upon request.

        The location of both files is defined in the config file.

    Output graph location:
        The graphs are stored into the scoreboard program's
        directory structure, as the profile graph is called by the
        scoreboard.
    '''

    #DECODE VALUES
    actual = decode(df=data, col_name='actualprofiledata')
    target = decode(df=data, col_name='targetprofiledata')

    #SETUP FIGURE
    fig = plt.figure(figsize=CFG['figsize'])
    ax1 = fig.add_subplot(111, facecolor=CFG['white'])

    #PLOT TARGET PROFILE
    plt.plot(target, color=CFG['grey_light'], alpha=0.75)

    #PLOT ACTUAL PROFILE
    #TEST FOR SMOOTHED LINED
    if CFG['smooth_lines'] == 1:
        #CALCULATE SMOOTHED VALUES
        x_smoothed = np.linspace(0, 90, CFG['smooth_factor'])
        y_smoothed = spline(range(90), actual, x_smoothed)
        #PLOT SMOOTHED ACTUAL
        plt.plot(x_smoothed, y_smoothed, color=CFG['blue2'], linewidth=4)
    else:
        #PLOT ACTUAL
        plt.plot(actual, color=CFG['blue2'], linewidth=4)

    #CONFIGURE APPEARANCE
    #-------------------------------------------------------------------
    #TARGET FILL
    ax1.fill_between(range(90), target, color=CFG['blue_light'], alpha=.3)
    #TURN OFF GRID AND AXIS LABELS
    ax1.yaxis.grid(False)
    ax1.get_xaxis().set_visible(False)
    ax1.get_yaxis().set_visible(False)
    #SET AXIS RANGES
    ax1.set_ylim([0, 18])
    ax1.set_xlim([-1, 90])
    ax1.axis('off')

    #PROFILE ANNOTATION SETUP
    labels = CFG['labels']
    coords = CFG['coords']
    align  = CFG['align']

    #ADD ANNOTATIONS
    for idx, _ in enumerate(labels):
        ax1.annotate(labels[idx], xy=coords[idx], ha=align[idx],
                     verticalalignment='bottom', color=CFG['grey_dark'])
    #-------------------------------------------------------------------

    #SET GRAPH TITLE >> ADD PLAYER'S SCORE
    plt.title('RESULTS FOR %s' % alias.upper(),
              fontsize=25, color=CFG['grey_med'], y=1.15, ha='center')
    plt.suptitle('your score is: %s' % score, fontsize=12, color=CFG['grey_med'], ha='center')

    #STORE IMAGE FOR DISPLAY
    plt.savefig(os.path.join(CFG['dir_graph'], 'profile.png'), bbox_inches='tight', dpi=300)

    #STORE IMAGE FOR PLAYER (IF REQUESTED)
    plt.savefig(os.path.join(CFG['dir_graph_player'], '%s_profile.png' % alias),
                bbox_inches='tight', dpi=300)


#-----------------------------------------------------------------------
#FUNCTION USED TO CREATE THE PROFILE
def new_profile():

    '''
    DESIGN:
    The new_profile() method first tests to determine if a new profile
    should be created, by counting the number of 'profiled' fields which
    are 0.  (i.e.: not yet profiled)

    If the returned value is > 0, a new profile graph is created, then,
    the 'profiled' database field is updated to 1.

    If the returned value is 0, the program continues in the while True
    loop (the_app_loop()), until a new profile is required.
    '''

    #TEST IF A PROFILE SHOULD BE CREATED
    if DBC.profile_to_be_created():

        #CONSOLE NOTIFICATION
        print '%s: New profile found.' % dt.now()

        #GET DATA
        df = DBC.new_profile_data()

        #CONSOLE NOTIFICATION
        print '%s: Creating profile for: %s' % (dt.now(), df.loc[0, 'name'])

        #CREATE THE GRAPH FOR THE DASHBOARD / SCOREBOARD
        create_graph(data=df, alias=df.loc[0, 'name'], score=df.loc[0, 'gamehighscore'])

        #UPDATE PLAYER'S PROFILED FLAG
        DBC.update_profiled_flag(alias=df.loc[0, 'name'])

    else:
        #CONSOLE NOTIFICATION
        print '%s: No new profiles to be created.' % dt.now()

        #CODE GOES BACK INTO THE LOOP FOR TEST AGAIN IN (N) SECONDS


#-----------------------------------------------------------------------
#METHOD USED TO TEST AND CREATE PROFILE GRAPH DIRECTORIES
def image_dir_test():

    '''
    PURPOSE:
    The purpose of this method is to ensure the directories for profile
    graph storage exist.  This check occurs on program startup.

    DESIGN:
    Using the built-on os library, each directory is tested to exist.
    If the directory does not exist, it is created.

    The directory paths are stored in the program config file.
    '''

    #LIST OF DIRS TO TEST
    dirs = [CFG['dir_graph'], CFG['dir_graph_player']]

    #TEST IF GRAPH DIRS EXIST
    for dir_ in dirs:
        #IF NO, CREATE THEM
        if not os.path.exists(dir_): os.makedirs(dir_)


#-----------------------------------------------------------------------
#APPLICATION LOOP TO REFRESH SCOREBOARD PLAYER'S PROFILE GRAPH
def the_app_loop():

    '''
    PURPOSE:
    This method is the main program loop, to keep the program checking
    for, and creating new profile graphs.

    DESIGN:
    In each loop, the 'profiled' field is queried to determine if a new
    profile needs to be created.  If no, the loop sleeps for (n)
    seconds, then checks again until a new profile must be created.

    After a new profile is created, the loop begins again.

    The sleep time interval is set in the config file.
    '''

    #LOOP TO REFRESH GRAPH WHEN A PLAYER FINISHES
    while True:

        #DO THE WORK
        new_profile()
        #DEBUG BREAK
        #break
        #TIMEOUT
        time.sleep(CFG['wait_time'])


#-----------------------------------------------------------------------
#MAIN CONTROLLER
def main():

    '''
    PURPOSE:
    This is the main program controller.
    '''

    global CFG
    global DBC

    #LOAD CONFIG FILE
    CFG = setup_config()
    #CREATE DB CONNECTION INSTANCE
    DBC = setup_db()

    #TEST IF PROFILE GRAPH DIRS EXIST
    image_dir_test()

    #LOOP PROGRAM TO REFRESH SCOREBOARD GRAPH
    the_app_loop()


#-----------------------------------------------------------------------
#RUN PROGRAM
if __name__ == '__main__':

    '''
    DESIGN:
    When run, the program searches for a '-v' or '--version' argument.
    If found, the script name and version (as defined in _version.py)
    are displayed to the CLI.

    If no arguments are found, the program is run.
    '''

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
