# FRITZ!Box Status Page
A status page for AVM FRITZ!Box routers to easily check internet speed and availability

![Example](example.png)

- written in Python 3.12.8 using NiceGUI and fritzconnection
- only works with AVM FRTIZ!Box Routers!
    - Requires an extra user account for connecting to the fritzbox via API: https://en.avm.de/service/knowledge-base/dok/FRITZ-Box-7590/1522_Accessing-FRITZ-Box-from-the-home-network-with-user-accounts/
- Heavily inspired by Speedtest-Tracker from @alexjustesen : https://github.com/alexjustesen/speedtest-tracker

## CAUTION: BETA! This is not a fully release yet, I'm still working on v1.0

## Docker compose file:
```yaml
services:
  fritzbox-status-page:
    image: ghcr.io/maze404/fritzbox-status-page:main
    container_name: fritzbox-status-page
    ports:
      - "8000:8080"
    restart: unless-stopped
```

## Docker run command:
```sh
docker run -d --name fritzbox-status-page -p 8000:8080 ghcr.io/maze404/fritzbox-status-page:main
```

- ToDo:
    - [x] Show if the router is currently connnected to the internet
    - [x] Show upload and download speed
    - [x] Show if DNS is working
    - [x] Settings page for entering router IP and user credentials, DNS domain to check against, etc.
    - [x] Implement a refresh interval that can be customized
    - [ ] Move settings to its own page instead of the overview page
    - [x] Create docker build for this program
    - [ ] Show Diagrams for keeping track of the upload and download speeds (Idea taken from https://github.com/alexjustesen/speedtest-tracker )
    - [ ] Show router log messages on extra page
    - [ ] Add a button to restart the router if needed
        - [ ] Add an option to restart the router as soon as it looses internet connection
    - [ ] Add a button to enable or disable the router's wifi

I'm sorry if the code is messy, this is my first project in python and i have little to no clue about object orientation :)

If you have any more ideas, feel free to contribute to the project or send me a message!