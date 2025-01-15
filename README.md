# FRITZ!Box Status Page

A status page for AVM FRITZ!Box routers to easily check internet speed and availability

Overview            |  Settings
:-------------------------:|:-------------------------:
<img src=".images/example-darkmode.png" width="500">  |  <img src=".images/example-darkmode_settings.png" width="500">
<img src=".images/example-lightmode.png" width="500">  |  <img src=".images/example-lightmode_settings.png" width="500">

- written in Python 3.13.1 using NiceGUI and fritzconnection
- Heavily inspired by Speedtest-Tracker from @alexjustesen : <https://github.com/alexjustesen/speedtest-tracker>

## Requirements

- AVM FRITZ!Box router
  - A dedicated user account for connecting to the router via API: <https://en.avm.de/service/knowledge-base/dok/FRITZ-Box-7590/1522_Accessing-FRITZ-Box-from-the-home-network-with-user-accounts/>
- Docker or docker compose
- x86 or ARM CPU

## Docker compose file

```yaml
services:
  fritzbox-status-page:
    image: ghcr.io/maze404/fritzbox-status-page:main
    container_name: fritzbox-status-page
    ports:
      - "8000:8080"
    environment:
      - DB_MODE=
      - DB_HOST=
      - DB_PORT=
      - DB_NAME=
      - DB_USER=
      - DB_PASSWORD=
    volumes:
      - /YOUR/CUSTOM/PATH/config:/app/config #Optional, but will make the settings persistent
      - /YOUR/CUSTOM/PATH/log:/app/log #Optional, except if you want to have a look at the logs
    restart: unless-stopped
```

The environment variables are generally optional. If you choose to remove them or leave them empty, then the program will default to an internal sqlite database.

If you do want to use the environment variables, then you have the following options:

- `DB_MODE`: `sqlite` or `mysql`. Sqlite will make all other environment variables obsolete!
- `DB_HOST`: The IP address of the *mysql* database
- `DB_PORT`: The port for mysql (`3306` by default)
- `DB_NAME`: Name of the mysql database
- `DB_USER`: Username for the mysql database
- `DB_PASSWORD`: Password for the above mentioned database user.

The program will setup the database on its own on the first start. If you are still using a version that was using a settings.json file, then you will have to re-enter your router connection information in the settings.

## Docker run command

```sh
docker run -d --name fritzbox-status-page -p 8000:8080 -v /YOUR/CUSTOM/PATH/config:/app/config -v /YOUR/CUSTOM/PATH/log:/app/log ghcr.io/maze404/fritzbox-status-page:main
```

*I highly advise to use the docker-compose file above as the docker run command is really only suited in case you don't want to use an external database.*

## ToDo's

- [x] Show if the router is currently connnected to the internet
- [x] Show upload and download speed
- [x] Show if DNS is working
- [x] Settings page for entering router IP and user credentials, DNS domain to check against, etc.
- [x] Implement a refresh interval that can be customized
- [x] Move settings to its own page instead of the overview page
- [x] Create docker build for this program
- [x] Toggle darkmode on/off
- [x] After setup, make top left logo redirect to router webinterface
- [x] Refine the UI for light/darkmode usage and readability
- [x] Add support for mysql and sqlite databases
- [x] Remove settings.json and fully switch to databases
- [ ] Show Diagrams for keeping track of the upload and download speeds (Idea taken from <https://github.com/alexjustesen/speedtest-tracker> )
- [ ] Show router log messages on extra page
- [ ] Add a button to restart the router if needed
  - [ ] Add an option to restart the router as soon as it looses internet connection
- [ ] Add a button to enable or disable the router's wifi

I'm sorry if the code is messy, this is my first project in python and i have little to no clue about object orientation :)

If you have any more ideas, feel free to contribute to the project or send me a message!

*If you're someone who works at AVM: Hi! I love your routers!*
