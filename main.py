import os

import cherrypy
import numpy as np
from PIL import Image, ImageFilter

upload_dir = os.path.join(os.getcwd(), 'uploads')


class WebServer:
    def __init__(self):
        self.current_image = None
        self.processed_image = "processed_image.png"

    @cherrypy.expose
    def index(self):
        return '''
        <html>
            <head>
                <title>Image Editor</title>
                <style>
                    body {
                        display: flex;
                        flex-direction: row;
                        justify-content: flex-start;
                        align-items: flex-start;
                        margin: 0;
                        padding: 20px;
                        font-family: Arial, sans-serif;
                    }
                    .controls {
                        flex: 1;
                        max-width: 300px;
                        margin-right: 20px;
                        background: #f5f5f5;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .preview {
                        flex: 2;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 90vh;
                        background: #fff;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    img {
                        max-width: 100%;
                        max-height: 90vh;
                        object-fit: contain;
                    }
                    .open-file-input {
                        display: none;
                    }
                    .open-file-label, .styled-button {
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #4CAF50;
                        color: white;
                        cursor: pointer;
                        text-align: center;
                        border: none;
                        border-radius: 5px;
                        margin: 5px 0;
                        width: 100%;
                        box-sizing: border-box;
                        transition: background-color 0.3s;
                    }
                    .open-file-label:hover, .styled-button:hover {
                        background-color: #45a049;
                    }
                    .image-adjustments {
                        margin-top: 15px;
                        padding: 15px;
                        background-color: #fff;
                        border-radius: 5px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }
                    .edge-controls {
                        margin-top: 15px;
                        padding: 15px;
                        background-color: #fff;
                        border-radius: 5px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    }
                    .edge-controls label {
                        display: block;
                        margin-top: 10px;
                        font-weight: bold;
                        color: #333;
                    }
                    .edge-controls input {
                        width: 100%;
                        margin: 8px 0;
                    }
                    h1 {
                        font-size: 24px;
                        color: #333;
                        margin-bottom: 20px;
                    }
                    h2 {
                        font-size: 18px;
                        color: #666;
                        margin: 20px 0 10px 0;
                    }
                    #preview img {
                        border-radius: 5px;
                    }
                    .process-button {
                        background-color: #2196F3;
                        margin-top: 20px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    .process-button:hover {
                        background-color: #1976D2;
                    }
                    .section-divider {
                        border-top: 1px solid #ddd;
                        margin: 20px 0;
                    }
                </style>
                <script>
                    function uploadFile(input) {
                        const formData = new FormData();
                        formData.append('file', input.files[0]);

                        fetch('/open_file', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.text())
                        .then(html => {
                            document.getElementById('preview').innerHTML = html;
                        })
                        .catch(error => console.error('Error:', error));
                    }

                    function toggleEdgeDetection() {
                        const controls = document.getElementById('edgeControls');
                        controls.style.display = controls.style.display === 'none' || controls.style.display === '' ? 'block' : 'none';
                        if (controls.style.display === 'block') {
                            document.getElementById('threshold').value = 0;
                            document.getElementById('thresholdValue').textContent = '0';
                        }
                    }

                    function updateThresholdValue() {
                        const threshold = document.getElementById('threshold').value;
                        document.getElementById('thresholdValue').textContent = threshold;
                    }

                    function processImage() {
                        const threshold = document.getElementById('threshold').value;
                        fetch(`/highlight_edges?threshold=${threshold}`)
                            .then(response => response.text())
                            .then(html => {
                                document.getElementById('preview').innerHTML = html;
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                document.getElementById('preview').innerHTML = '<p>Error processing image</p>';
                            });
                    }
                </script>
            </head>
            <body>
                <div class="controls">
                    <h1>Image Editor</h1>

                    <!-- File Upload Section -->
                    <label class="open-file-label" for="file-input">Choose File</label>
                    <input id="file-input" class="open-file-input" type="file" 
                           name="file" accept=".jpg, .png" onchange="uploadFile(this)" required>

                    <!-- Image Adjustments Section -->
                    <div class="image-adjustments">
                        <h2>Adjust Image</h2>
                        <button class="styled-button" onclick="adjustSize()">Resize</button>
                        <button class="styled-button" onclick="adjustBrightness()">Adjust Brightness</button>
                        <button class="styled-button" onclick="solarize()">Solarize</button>
                        <button class="styled-button" onclick="convertNegative()">Convert to Negative</button>
                        <button class="styled-button" onclick="toggleEdgeDetection()">Edge Detection</button>

                        <!-- Edge Detection Controls -->
                        <div id="edgeControls" class="edge-controls" style="display: none;">
                            <label for="threshold">Edge Threshold: <span id="thresholdValue">0</span></label>
                            <input type="range" id="threshold" name="threshold"
                                   min="0" max="255" step="1" value="0"
                                   oninput="updateThresholdValue()">
                        </div>
                    </div>

                    <div class="section-divider"></div>

                    <!-- Final Process Button -->
                    <button onclick="processImage()" class="styled-button process-button">Process Image</button>
                </div>
                <div class="preview" id="preview">
                    <p>Upload an image to begin</p>
                </div>
            </body>
        </html>
        '''

    @cherrypy.expose
    def open_file(self, file):
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        if file:
            if hasattr(file, 'filename') and file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(upload_dir, file.filename)
                with open(file_path, 'wb') as f:
                    f.write(file.file.read())

                self.current_image = file.filename

                return f'''
                          <img src="/uploads/{file.filename}" alt="Uploaded Image" style="max-width:100%; height:auto;">
                          '''
            else:
                if self.current_image:
                    return f'''
                           <img src="/uploads/{self.current_image}" alt="Uploaded Image" style="max-width:100%; height:auto;">
                           '''
                else:
                    return "<p>Invalid file type. Please enter .jpg or .png and upload a valid image.</p>"
        else:
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
    def show_original(self):
        if not self.current_image:
            return "<p>Please upload an image first.</p>"
        return f'<img src="/uploads/{self.current_image}" alt="Original Image">'

    @cherrypy.expose
    def highlight_edges(self, threshold=0):
        if not self.current_image:
            return "<p>Please upload an image first.</p>"

        try:
            image_path = os.path.join(upload_dir, self.current_image)
            output_path = os.path.join(upload_dir, self.processed_image)

            threshold = float(threshold)

            # Opens the image and convert to numpy array
            img = Image.open(image_path)
            img_array = np.array(img)

            edges_rgb = np.zeros_like(img_array, dtype=float)

            # Calculates gradients for each color channel
            for channel in range(3):  # RGB channels
                channel_data = img_array[:, :, channel].astype(float)
                gy, gx = np.gradient(channel_data)
                edges = np.sqrt(gx ** 2 + gy ** 2)

                if edges.max() > 0:
                    edges = (edges / edges.max() * 255)

                edges[edges < threshold] = 0

                edges_rgb[:, :, channel] = edges

            edge_magnitude = np.max(edges_rgb, axis=2)

            # Creates the final image by modulating the original colors with edge intensity
            result = img_array.copy()
            for channel in range(3):
                result[:, :, channel] = np.where(
                    edge_magnitude >= threshold,
                    img_array[:, :, channel],
                    0
                )

            # Convert back to PIL Image and save
            edge_image = Image.fromarray(result.astype(np.uint8))
            edge_image.save(output_path)

            # Timestamp to force browser reload
            timestamp = int(cherrypy.response.time)
            return f'<img src="/uploads/{self.processed_image}?t={timestamp}" alt="Processed Image" />'

        except Exception as e:
            cherrypy.log(f"Error processing image: {str(e)}")
            return f"<p>Error processing image: {str(e)}</p>"

if __name__ == '__main__':
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Configuration to process images in real time
    conf = {
        '/uploads': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': upload_dir
        }
    }

    cherrypy.quickstart(WebServer(), '/', conf)