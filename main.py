import os
import cherrypy
import numpy as np
from PIL import Image
from scipy.signal import convolve2d

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
                        .resize-controls, .edge-controls, .brightness-controls, .negative-controls, .solarize-controls {
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
                    }

                        function toggleNegative() {
                            const controls = document.getElementById('negativeControls');
                            controls.style.display = controls.style.display === 'none' || controls.style.display === '' ? 'block' : 'none';
                        }

                        function toggleSolarize() {
                            const controls = document.getElementById('solarizeControls');
                            controls.style.display = controls.style.display === 'none' || controls.style.display === '' ? 'block' : 'none';
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
                            const edgeType = document.querySelector('input[name="edgeType"]:checked').value;
                            const brightness = document.getElementById('brightness').value;
                            const resizeControls = document.getElementById('resizeControls');
                            
                            const solarizeType = document.querySelector('input[name="solarizeType"]:checked').value;
                            const solarize = solarizeType === 'apply';
                            
                            const negativeType = document.querySelector('input[name="negativeType"]:checked').value;
                            const negative = negativeType !== 'none';
                            
                            //  URL with all necessary parameters
                            let url = `/process_image?brightness=${brightness}&edgeType=${edgeType}`;
                            
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

                            <!-- Edge Detection Controls -->
                            <button class="styled-button" onclick="toggleEdgeDetection()">Highlight Edges</button>
                            <div id="edgeControls" class="negative-controls">
                                <div class="radio-group">
                                    <label>
                                        <input type="radio" name="edgeType" value="none" checked>
                                        None
                                    </label>
                                    <label>
                                        <input type="radio" name="edgeType" value="laplacian">
                                        Laplacian
                                    </label>
                                    <label>
                                        <input type="radio" name="edgeType" value="prewitt">
                                        Prewitt
                                    </label>
                                </div>
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
                            </div>

                            <!-- Solarize Controls -->
                            <button class="styled-button" onclick="toggleSolarize()">Solarize</button>
                            <div id="solarizeControls" class="solarize-controls">
                                <div class="radio-group">
                                    <label>
                                        <input type="radio" name="solarizeType" value="none" checked>
                                        None
                                    </label>
                                    <label>
                                        <input type="radio" name="solarizeType" value="apply">
                                        Apply
                                    </label>
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
    def process_image(self, brightness=0, width=None, height=None, edgeType="none", solarize="false",
                      negative="false", negativeType="color"):
        if not self.current_image:
            return "<p>Please upload an image first.</p>"

        try:
            image_path = os.path.join(upload_dir, self.current_image)
            output_path = os.path.join(upload_dir, self.processed_image)

            img = Image.open(image_path)

            # Preserves alpha channel if it exists
            if img.mode in ('RGBA', 'LA'):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            """ Resize option """
            if width and height:
                try:
                    new_width = int(width)
                    new_height = int(height)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                except (TypeError, ValueError):
                    return "<p>Please enter valid numerical dimensions.</p>"

            img_array = np.array(img)

            """ Brightness option """
            brightness = float(brightness)
            brightness_factor = 1.0 + (brightness / 100.0)

            # Separates an alpha channel if exists
            if img_array.shape[2] == 4:
                alpha = img_array[:, :, 3]
                img_array = img_array[:, :, :3]
            else:
                alpha = None

            # Brightness scaling
            img_array = np.clip(img_array * brightness_factor, 0, 255).astype(np.uint8)

            """ Highlight edges option """
            if edgeType != "none":
                # Converts to grayscale for edge detection
                if len(img_array.shape) == 3:
                    gray = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140])
                else:
                    gray = img_array

                gray = gray / 255.0  # Normalization to [0, 1]

                if edgeType == "laplacian":
                    kernel = np.array([[-1, -1, -1],
                                       [-1, 8, -1],
                                       [-1, -1, -1]])
                    edges = np.abs(convolve2d(gray, kernel, mode='same', boundary='symm'))

                    # Enhances edge visibility
                    edges = (edges - edges.min()) / (edges.max() - edges.min())  # Normalization
                    edges = np.power(edges, 0.5)  # Contrast enhancement
                    edges = np.clip(edges * 255, 0, 255).astype(np.uint8)


                    mask = edges > 55

                elif edgeType == "prewitt":
                    kernel_x = np.array([[1, 0, -1],
                                         [1, 0, -1],
                                         [1, 0, -1]])
                    kernel_y = np.array([[1, 1, 1],
                                         [0, 0, 0],
                                         [-1, -1, -1]])
                    gx = convolve2d(gray, kernel_x, mode='same', boundary='symm')
                    gy = convolve2d(gray, kernel_y, mode='same', boundary='symm')
                    edges = np.sqrt(gx ** 2 + gy ** 2)

                    # Normalization of edges to [0, 255]
                    edges = (edges / edges.max() * 255) if edges.max() > 0 else edges
                    edges = np.clip(edges, 0, 255).astype(np.uint8)


                    mask = edges > 35

                # Creates a black and white image with edges
                img_array = np.zeros_like(img_array)
                img_array[mask] = [0, 0, 0]  # Black for edges
                img_array[~mask] = [255, 255, 255]  # White for non-edge areas

            """ Solarize option """
            if solarize.lower() == "true":
                threshold_value = 128
                img_array = np.where(img_array > threshold_value, 255 - img_array, img_array)

            """ Convert to negative option """
            if negative.lower() == "true":
                if negativeType == "bw":
                    grayscale = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140]).astype( np.float32)  # Grayscale conversion

                    # Inverts the grayscale image
                    grayscale_negative = 255 - grayscale

                    # Ensures that the result is in the valid range [0, 255]
                    img_array = np.stack([grayscale_negative] * 3,
                                         axis=-1)  # Converts single channel to RGB by repeating grayscale
                    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
                else:
                    img_array = 255.0 - img_array

            img_array = np.clip(img_array, 0, 255).astype(np.uint8)

            # Alpha channel for transparent images
            if alpha is not None:
                result_image = Image.fromarray(np.dstack((img_array, alpha)))
            else:
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