from nicegui import ui
from backend.logging import Logging
from frontend.overview import Overview
from frontend.settings import Settings
import os, json

logger = Logging()

class Website:
    def launch(self):
        ui.query('.nicegui-content').style('display: flex; margin: 0; padding: 0;')
        ui.run(favicon='https://upload.wikimedia.org/wikipedia/de/thumb/6/68/Fritz%21_Logo.svg/2048px-Fritz%21_Logo.svg.png', title='FRITZ!Box Status Page')
        ui.add_head_html('<link rel="preconnect" href="https://fonts.googleapis.com">')
        ui.add_head_html('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
        ui.add_head_html('<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">')

    @ui.page('/')
    def create_overview() -> None:
        Website.launch(Website)
        with ui.row().classes('p-0 gap-0').style('width: 100vw;'):
            Menu().create()
            with ui.grid(columns=1).style('width: calc( 100% - 250px ); display: flex; flex-direction: column; align-items: center;'):
                with ui.grid(columns=1).style('display: flex; flex-direction: column; align-items: stretch; justify-content: center;'):
                    Overview().create()

    @ui.page('/settings')
    def create_settings() -> None:
        Website.launch(Website)
        with ui.row().classes('p-0 gap-0').style('width: 100vw;'):
            Menu().create()
            with ui.grid(columns=1).style('width: calc( 100% - 250px ); display: flex; flex-direction: column; align-items: center;'):
                with ui.grid(columns=1).style('display: flex; flex-direction: column; align-items: stretch; justify-content: center;'):
                    Settings().create()

class Menu:
    def __init__(self):
        self.settings_dir = 'config'
        self.settings_path = os.path.join(self.settings_dir, 'settings.json')

    def create(self):
        with ui.grid(columns=1).classes('p-0 gap-0').style('width: 250px; height: 100vh; display: flex; flex-direction: column; z-index: 2; box-shadow: 0px 0px 14px 2px rgba(0,0,0,0.75);'):
            with ui.column().style('background-image: linear-gradient(180deg, #1577cf, #004482); padding: 1em; flex-shrink: 1; font-family: "Source Sans 3"; position: flex-start;'):
                if os.path.exists(self.settings_path):
                    with open(self.settings_path, 'r') as json_file:
                        settings = json.load(json_file)
                        address_value = settings.get('address', '')
                        with ui.link(target='http://' + address_value).style('width: 50%; margin: 0 auto 0 auto; display: block'):
                            ui.image('https://upload.wikimedia.org/wikipedia/de/thumb/6/68/Fritz%21_Logo.svg/2048px-Fritz%21_Logo.svg.png')
                else:
                    ui.image('https://upload.wikimedia.org/wikipedia/de/thumb/6/68/Fritz%21_Logo.svg/2048px-Fritz%21_Logo.svg.png').style('width: 50%; margin: 0 auto 0 auto; display: block')
                ui.label('FRITZ!Box Status Page').style('color: white; font-size: 1.5rem; font-weight: bold; margin-bottom: 20px; text-align: left; text-align: center')
            with ui.list().style('padding: 1rem; display: flex; flex-direction: column; flex-grow: 3; height: 100%'):
                ui.link('Overview', Website.create_overview).style('font-size: 1.125rem; height: 2.5rem; background-color: #1577cf; border-radius: 0.25rem; color: white; width: 100%; text-align: center; text-decoration: none; display: flex; align-items: center; padding: 0.75rem; margin: 0; margin-bottom: 0.75rem;')
                ui.link('Settings', Website.create_settings).style('font-size: 1.125rem; height: 2.5rem; border: solid; border-width: 2px; border-color: #1577cf; border-radius: 0.25rem; color: #1577cf; width: 100%; text-align: center; text-decoration: none; display: flex; align-items: center; padding: 0.75rem; margin: 0;')
            with ui.row().style('background-image: linear-gradient(180deg, #1577cf, #004482); padding: 1em; flex-shrink: 1; font-family: "Source Sans 3"; position: flex-end;'):
                with ui.link(target='https://github.com/maze404/fritzbox-status-page'):
                    ui.image('https://cdn.freebiesupply.com/logos/large/2x/github-icon-1-logo-black-and-white.png').style('filter: invert(1);').classes('w-8')
                darkmode=ui.dark_mode()
                ui.switch('Dark Mode', value=darkmode.value, on_change=lambda: darkmode.toggle())

if not os.path.exists('config'):
    os.makedirs('config')

Website.create_overview()
