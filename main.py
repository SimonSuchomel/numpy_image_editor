import os
import cherrypy
import numpy as np
from PIL import Image

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
                        .resize-controls, .edge-controls, .brightness-controls, .negative-controls {
                            display: none;
                            margin-top: 15px;
                            padding: 15px;
                            background-color: #fff;
                            border-radius: 5px;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        }
                        .edge-controls label, .resize-controls label, .brightness-controls label {
                            display: block;
                            margin-top: 10px;
                            font-weight: bold;
                            color: #333;
                        }
                        .edge-controls input, .resize-controls input[type="number"], .brightness-controls input {
                            width: 100px;
                            padding: 5px;
                            margin: 5px;
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
                        .dimension-inputs {
                            display: flex;
                            align-items: center;
                            gap: 10px;
                            margin-bottom: 10px;
                        }
                        .aspect-ratio-container {
                            display: flex;
                            align-items: center;
                            gap: 5px;
                            margin-top: 10px;
                        }
                        .radio-group {
                            display: flex;
                            flex-direction: column;
                            gap: 10px;
                            margin-top: 10px;
                        }
                        .radio-group label {
                            display: flex;
                            align-items: center;
                            gap: 5px;
                            font-size: 0.9em;
                            color: #555;
                        }
                        .nested-control {
                            margin-top: 10px;
                        }
                        input[type="range"] {
                            width: 100%;
                            margin: 10px 0;
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

                        function adjustSize() {
                            const resizeControls = document.getElementById('resizeControls');
                            resizeControls.style.display = resizeControls.style.display === 'none' || resizeControls.style.display === '' ? 'block' : 'none';
                        }

                        function adjustBrightness() {
                            const controls = document.getElementById('brightnessControls');
                            controls.style.display = controls.style.display === 'none' || controls.style.display === '' ? 'block' : 'none';
                        }

                        function toggleEdgeDetection() {
                            const controls = document.getElementById('edgeControls');
                            controls.style.display = controls.style.display === 'none' || controls.style.display === '' ? 'block' : 'none';
                            if (controls.style.display === 'block') {
                                document.getElementById('threshold').value = 0;
                                document.getElementById('thresholdValue').textContent = '0';
                            }
                        }

                        function toggleNegative() {
                            const controls = document.getElementById('negativeControls');
                            controls.style.display = controls.style.display === 'none' || controls.style.display === '' ? 'block' : 'none';
                        }

                        function updateThresholdValue() {
                            const threshold = document.getElementById('threshold').value;
                            document.getElementById('thresholdValue').textContent = threshold;
                        }

                        function updateBrightnessValue() {
                            const brightness = document.getElementById('brightness').value;
                            document.getElementById('brightnessValue').textContent = brightness;
                        }

                        function maintainAspectRatio(changedInput) {
                            const width = document.getElementById('width');
                            const height = document.getElementById('height');
                            const aspectRatio = document.getElementById('maintainAspectRatio').checked;

                            if (aspectRatio && changedInput.value) {
                                const img = document.querySelector('#preview img');
                                if (img) {
                                    const ratio = img.naturalWidth / img.naturalHeight;
                                    if (changedInput === width) {
                                        height.value = Math.round(width.value / ratio);
                                    } else {
                                        width.value = Math.round(height.value * ratio);
                                    }
                                }
                            }
                        }

                        function processImage() {
                            const width = document.getElementById('width').value;
                            const height = document.getElementById('height').value;
                            const threshold = document.getElementById('threshold').value;
                            const brightness = document.getElementById('brightness').value;
                            const resizeControls = document.getElementById('resizeControls');
                            const solarize = document.getElementById('solarizeCheck').checked;
                            const negativeType = document.querySelector('input[name="negativeType"]:checked').value;
                            const negative = negativeType !== 'none';

                            let url = `/process_image?threshold=${threshold}&brightness=${brightness}`;

                            if (resizeControls.style.display === 'block' && width && height) {
                                url += `&width=${width}&height=${height}`;
                            }

                            url += `&solarize=${solarize}&negative=${negative}&negativeType=${negativeType}`;

                            fetch(url)
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

                            <!-- Resize Controls -->
                            <div id="resizeControls" class="resize-controls">
                                <div class="dimension-inputs">
                                    <div>
                                        <label for="width">Width:</label>
                                        <input type="number" id="width" min="1" 
                                               oninput="maintainAspectRatio(this)">
                                    </div>
                                    <div>
                                        <label for="height">Height:</label>
                                        <input type="number" id="height" min="1"
                                               oninput="maintainAspectRatio(this)">
                                    </div>
                                </div>
                                <div class="aspect-ratio-container">
                                    <input type="checkbox" id="maintainAspectRatio" checked>
                                    <label for="maintainAspectRatio">Maintain aspect ratio</label>
                                </div>
                            </div>

                            <button class="styled-button" onclick="adjustBrightness()">Adjust Brightness</button>

                            <!-- Brightness Controls -->
                            <div id="brightnessControls" class="brightness-controls">
                                <label for="brightness">Brightness: <span id="brightnessValue">0</span></label>
                                <input type="range" id="brightness" name="brightness"
                                       min="-100" max="100" step="1" value="0"
                                       oninput="updateBrightnessValue()">
                            </div>

                            <button class="styled-button" onclick="toggleEdgeDetection()">Edge Detection</button>

                            <!-- Edge Detection Controls -->
                            <div id="edgeControls" class="edge-controls">
                                <label for="threshold">Edge Threshold: <span id="thresholdValue">0</span></label>
                                <input type="range" id="threshold" name="threshold"
                                       min="0" max="255" step="1" value="0"
                                       oninput="updateThresholdValue()">
                            </div>

                            <!-- Negative Controls -->
                            <button class="styled-button" onclick="toggleNegative()">Convert to Negative</button>
                            <div id="negativeControls" class="negative-controls">
                                <div class="radio-group">
                                    <label>
                                        <input type="radio" name="negativeType" value="none" checked>
                                        None
                                    </label>
                                    <label>
                                        <input type="radio" name="negativeType" value="color">
                                        Colorful
                                    </label>
                                    <label>
                                        <input type="radio" name="negativeType" value="bw">
                                        Black & White
                                    </label>
                                </div>
                                <div class="nested-control">
                                    <input type="checkbox" id="solarizeCheck">
                                    <label for="solarizeCheck">Solarize</label>
                                </div>
                            </div>
                        </div>

                        <div class="section-divider"></div>
                        <button onclick="processImage()" class="styled-button process-button">Process Image</button>
                    </div>
                    <div class="preview" id="preview">
                        <p>Upload an image to begin</p>
                    </div>
                </body>
            </html>
            '''

    @cherrypy.expose
    def process_image(self, threshold=0, brightness=0, width=None, height=None, solarize="false", negative="false",
                      negativeType="color"):
        if not self.current_image:
            return "<p>Please upload an image first.</p>"

        try:
            image_path = os.path.join(upload_dir, self.current_image)
            output_path = os.path.join(upload_dir, self.processed_image)

            img = Image.open(image_path)

            if width and height:
                try:
                    new_width = int(width)
                    new_height = int(height)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                except (TypeError, ValueError):
                    return "<p>Please enter valid numerical dimensions.</p>"

            img_array = np.array(img).astype(np.float32)

            try:
                brightness = float(brightness)
                brightness_factor = 1.0 + (brightness / 100.0)
                img_array = img_array * brightness_factor
            except ValueError:
                pass

            if solarize.lower() == "true":
                threshold_value = 128
                img_array = np.where(img_array > threshold_value, 255 - img_array, img_array)

            if negative.lower() == "true":
                if negativeType == "bw":
                    # Convert to grayscale first (using standard RGB weights)
                    grayscale = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140])
                    negative = 255 - grayscale
                    # Stack the same values for all channels to maintain RGB format
                    img_array = np.stack([negative] * 3, axis=-1)
                else:
                    # Regular color negative
                    img_array = 255 - img_array

            try:
                threshold = float(threshold)
                if threshold > 0:
                    edges_rgb = np.zeros_like(img_array)

                    for channel in range(3):
                        channel_data = img_array[:, :, channel]
                        gy, gx = np.gradient(channel_data)
                        edges = np.sqrt(gx ** 2 + gy ** 2)

                        if edges.max() > 0:
                            edges = (edges / edges.max() * 255)

                        edges[edges < threshold] = 0
                        edges_rgb[:, :, channel] = edges

                    edge_magnitude = np.max(edges_rgb, axis=2)

                    for channel in range(3):
                        img_array[:, :, channel] = np.where(
                            edge_magnitude >= threshold,
                            img_array[:, :, channel],
                            0
                        )
            except ValueError:
                pass

            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
            result_image = Image.fromarray(img_array)
            result_image.save(output_path)

            timestamp = int(cherrypy.response.time)
            return f'<img src="/uploads/{self.processed_image}?t={timestamp}" alt="Processed Image" />'

        except Exception as e:
            cherrypy.log(f"Error processing image: {str(e)}")
            return f"<p>Error processing image: {str(e)}</p>"

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
                return "<p>Invalid file type. Please upload a .jpg or .png image.</p>"
        return "<p>No file uploaded. Please select a file to upload.</p>"



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


    # TODO Solarize button not in toggle Convert to negative
    # TODO Edge detection Colorful or Black & White option
    # TODO After Choosing file - reset current_image