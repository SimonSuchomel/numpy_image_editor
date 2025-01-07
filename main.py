import numpy as np
import cherrypy
from PIL import Image

class WebServer:
    @cherrypy.expose
    def index(self):
        return f'''
        <html>
        <head>
            <title>Image Editor</title>
        </head>
        <body>
            <h1>Image Editor</h1>
            <form action="/open_file">
                <input type="file" >
            </form>
            
            <!-- Temporary Part (WIP) -->

            <div>
                <h2>Adjust Image</h2>
                <form action="/adjust_size">
                    <input type="submit" value="Resize">
                </form>
                <form action="/brightness">
                    <input type="submit" value="Adjust Brightness">
                </form>
                <form action="/solarize">
                    <input type="submit" value="Solarize">
                </form>
                <form action="/negative">
                    <input type="submit" value="Convert to Negative">
                </form>
                <form action="/highlight_edges">
                    <input type="submit" value="Highlight Edges"> 
                </form>
            </div>

            <h2>Image Preview:</h2>

        </body>
        </html>
        '''

if __name__ == '__main__':
    cherrypy.quickstart(WebServer())


