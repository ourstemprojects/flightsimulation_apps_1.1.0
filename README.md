
### Flight Simulation Game
---

# APPS
---
The apps associated with the Flight Simulation Game are listed in the table below, along with a brief description.  

App | Description 
:--- | :---
registration | Service which runs the player's registration, via a web UI
scoreboard | Service which displays the game's scoreboard, via a web UI
profiler | Service which creates the player's profile graph for display on the scoreboard

These three apps are bundled in this repo for easy deployment and use.  For setup and user guidance, refer to the game's [Operation Guide](./_docs/Operations_Guide.pdf "link to the operations guide in this repo").  For deployment guidance, refer to the DEPLOYMENT section of this document.


## ENVIRONMENT
---
This game package was designed to run in a Linux environment, however much of the development for the apps bundle was done in Windows.  As such, we are *relatively* confident the game as a whole will also run in Windows, but have not tested this extensively.


## FULL STACK DESIGN
---
The design for the full game stack is shown in the flow image below.  

**Note:** the design below show four PCs being used; however, with this bundle, the game can be run on two or three, depending on your available setup.

PC | Use
:--- | :---
RasPi | Runs the game app
PC-1 | Runs the database, registration, scoreboard and profiler services
PC-2 | Displaying the web UIs for player registration and the scoreboard.  However, this is optional and the web UIs can be run from PC-1

![](./_design/flow_full_stack.png)

## DEPLOYMENT
---
Here are some basic steps for deploying this app bundle to your local environment.  Just as a reminder, please be sure to check and update each app's config files; which come in the forms of `config.json` and `db_config.json`.

**Note:** Update x.x.x to the version number you want to clone.

1) Clone the package from GitHub:
```bash
 > git clone https://github.com/ourstemprojects/flightsimulation_apps_x.x.x ~/<deployment_directory> 
```

2) For **all apps**: 
   - Update `db_config.json` with your database IP and login credentials

3) For the **profiler** app only:
   - Check / update the `dir_graph` and `dir_graph_player` keys in `config.json` to ensure these keys map to the **scoreboard** app's `./static/images` path
