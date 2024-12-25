from nicegui import ui
from backend.logging import Logging
from frontend.overview import Overview
from frontend.settings import Settings
import os

logger = Logging()

class Website:
    def launch(self):
        ui.query('.nicegui-content').style('display: flex; margin: 0; padding: 0;')
        ui.dark_mode(True)
        ui.run(favicon='https://upload.wikimedia.org/wikipedia/de/thumb/6/68/Fritz%21_Logo.svg/2048px-Fritz%21_Logo.svg.png', title='FRITZ!Box Status Page')
        ui.add_head_html('<link rel="preconnect" href="https://fonts.googleapis.com">')
        ui.add_head_html('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
        ui.add_head_html('<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">')

        self.create_frame(self.launch)

    def create_frame(self):
        with ui.row().classes('p-0 gap-0').style('width: 100vw;'):
            Menu().create()
            with ui.grid(columns=1).style('width: calc( 100% - 250px ); display: flex; flex-direction: column; align-items: center;'):
                with ui.grid(columns=1).style('display: flex; flex-direction: column; align-items: stretch; justify-content: center;'):
                    Overview().create()
                    Settings().create()

class Menu:
    def create(self):
        with ui.column().style('background-image: linear-gradient(180deg, #1577cf, #004482); width: 250px; height: 100vh; padding: 1em; flex-shrink: 0; font-family: "Source Sans 3"; position: flex-start;'):
            ui.image('https://upload.wikimedia.org/wikipedia/de/thumb/6/68/Fritz%21_Logo.svg/2048px-Fritz%21_Logo.svg.png').style('width: 50%; margin: 0 auto 0 auto; display: block')
            ui.label('FRITZ!Box Status Page').style('color: white; font-size: 2rem; font-weight: bold; margin-bottom: 20px; text-align: left;')
            ui.button('Home').style('width: 100%; display: flex; justify-content: flex-start;')

if not os.path.exists('config'):
    os.makedirs('config')

Website.launch(Website)