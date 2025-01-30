import os
import cherrypy
import numpy as np
from PIL import Image, ImageFilter

upload_dir = os.path.join(os.getcwd(), 'uploads') # defines the path for the uploads directory
class WebServer:
    def __init__(self):
        self.current_image = None  # To track the current uploaded image
        self.edges_highlighted = False  # To track if the edges are currently highlighted

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
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 98vh;
                }}
                img {{
                    max-width: 100%;
                    max-height: 98vh;
                    object-fit: contain;
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
        # Ensure uploads directory exists
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Check if file is provided and is not empty
        if file:
            # Verify the file is a valid image format
            if hasattr(file, 'filename') and file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(upload_dir, file.filename)
                with open(file_path, 'wb') as f:
                    f.write(file.file.read())  # Save the uploaded file

                # Update the current image to the uploaded file
                self.current_image = file.filename

                # Return the image preview in the browser
                return f'''
                      <img src="/uploads/{file.filename}" alt="Uploaded Image" style="max-width:100%; height:auto;">
                      '''
            else:
                # Invalid file type, just keeps the current image
                if self.current_image:
                    return f'''
                       <img src="/uploads/{self.current_image}" alt="Uploaded Image" style="max-width:100%; height:auto;">
                       '''
                else:
                    return "<p>Invalid file type. Please enter .jpg or .png and upload a valid image.</p>"
        else:
            # No file uploaded, just keeps the current image
            if self.current_image:
                return f'''
                  <img src="/uploads/{self.current_image}" alt="Uploaded Image" style="max-width:100%; height:auto;">
                  '''
            else:
                return "<p>No file uploaded. Please select a file to upload.</p>"

    @cherrypy.expose
    def uploads(self, filename):
        file_path = os.path.join(upload_dir, filename)
        if os.path.exists(file_path):
            return cherrypy.lib.static.serve_file(file_path, content_type='image/jpeg')

    @cherrypy.expose
    def highlight_edges(self):
        ...

if __name__ == '__main__':
    cherrypy.quickstart(WebServer())
