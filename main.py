import os
import cherrypy
from PIL import Image

upload_dir = os.path.join(os.getcwd(), 'uploads') # defines the path for the uploads directory
class WebServer:
    @cherrypy.expose
    def index(self):
        return f'''
        <html>
        <head>
            <title>Image Editor</title>
            <style>
                body {{
                    display: flex;
                    flex-direction: row;
                    justify-content: flex-start;
                    align-items: flex-start;
                }}
                .controls {{
                    flex: 1;
                    max-width: 300px;
                    margin-right: 20px;
                }}
                .preview {{
                    flex: 2;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                .open-file-input {{
                    display: none;
                }}
                .open-file-label, .styled-button {{
                    display: inline-block;
                    padding: 5px 10px;
                    background-color: gray;
                    color: white;
                    cursor: pointer;
                    text-align: center;
                    border: none;
                    border-radius: 5px;
                    font-family: arial;
                }}
                h1 {{
                font-family: sans-serif;
                }}
                h2 {{
                font-family: sans-serif;
                }}
            </style>
            <script>
                function uploadFile(input) {{
                    const formData = new FormData();
                    formData.append('file', input.files[0]);

                    fetch('/open_file', {{
                        method: 'POST',
                        body: formData
                    }})
                    .then(response => response.text())
                    .then(html => {{
                        document.getElementById('preview').innerHTML = html;
                    }})
                    .catch(error => console.error('Error:', error));
                }}
            </script>
        </head>
        <body>
            <div class="controls">
                <h1>Image Editor</h1>
                <label class="open-file-label" for="file-input">Choose File</label>
                <input id="file-input" class="open-file-input" type="file" name="file" accept=".jpg, .png" onchange="uploadFile(this)" required>

                <h2>Adjust Image</h2>
                <form action="/adjust_size">
                    <input type="submit" class="styled-button" value="Resize">
                </form>
                <form action="/brightness">
                    <input type="submit" class="styled-button" value="Adjust Brightness" >
                </form>
                <form action="/solarize">
                    <input type="submit" class="styled-button" value="Solarize">
                </form>
                <form action="/negative">
                    <input type="submit" class="styled-button" value="Convert to Negative">
                </form>
                <form action="/highlight_edges">
                    <input type="submit" class="styled-button" value="Highlight Edges"> 
                </form>
            </div>
            <div class="preview" id="preview">
            </div>
        </body>
        </html>
        '''

    @cherrypy.expose
    def open_file(self, file):
        if file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, 'wb') as f:
                f.write(file.file.read())

            return f'''
            <img src="/uploads/{file.filename}" alt="Uploaded Image" style="max-width:100%; height:auto;">
            '''
        else:
            return "<p>Invalid file type. Please enter .jpg or .png.</p>"

    @cherrypy.expose
    def uploads(self, filename):
        file_path = os.path.join(upload_dir, filename)
        if os.path.exists(file_path):
            return cherrypy.lib.static.serve_file(file_path, content_type='image/jpeg')

if __name__ == '__main__':
    cherrypy.quickstart(WebServer())
    # TODO - When exiting image opener -> error
