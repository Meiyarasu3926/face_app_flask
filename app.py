from flask import Flask, request, render_template
import os
import face_recognition
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Directory to store images
IMAGE_DIR = "employee_photos"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Directory for temporary comparison images
TEMP_DIR = "temp_comparison"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

# Route to register a new image
@app.route('/register', methods=['GET', 'POST'])
def register_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('register.html', error="No image provided.")

        file = request.files['image']
        file_path = os.path.join(IMAGE_DIR, file.filename)
        file.save(file_path)

        try:
            image = face_recognition.load_image_file(file_path)
            face_recognition.face_encodings(image)[0]
        except IndexError:
            os.remove(file_path)
            return render_template('register.html', error="No face detected in the uploaded image.")

        return render_template('register.html', success="Image registered successfully.")

    return render_template('register.html')

# Route to compare uploaded image with registered images
@app.route('/compare', methods=['GET', 'POST'])
def compare_images():
    if request.method == 'POST':
        # Cleanup previous temporary files
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = os.path.join(TEMP_DIR, temp_file)
            os.remove(temp_file_path) 

        if 'image' not in request.files:
            return render_template('compare.html', error="No image provided.")

        file = request.files['image']
        file_path = os.path.join(TEMP_DIR, file.filename)
        file.save(file_path)

        try:
            uploaded_image = face_recognition.load_image_file(file_path)
            uploaded_encoding = face_recognition.face_encodings(uploaded_image)[0]
        except IndexError:
            os.remove(file_path)
            return render_template('compare.html', error="No face detected in the uploaded image.")

        for existing_file in os.listdir(IMAGE_DIR):
            existing_file_path = os.path.join(IMAGE_DIR, existing_file)
            existing_image = face_recognition.load_image_file(existing_file_path)

            try:
                existing_encoding = face_recognition.face_encodings(existing_image)[0]
                match = face_recognition.compare_faces([existing_encoding], uploaded_encoding)
                distance = face_recognition.face_distance([existing_encoding], uploaded_encoding)[0]
                similarity = (1 - distance) * 100

                if match[0]:
                    os.remove(file_path)  # Remove the temporary file
                    return render_template(
                        'compare.html',
                        success=f"Image matches with {existing_file.split('.')[0]}. Similarity: {similarity:.2f}%"
                    )
            except IndexError:
                continue

        os.remove(file_path)  # Remove the temporary file if no match found
        return render_template('compare.html', error="No matching image found.")

    return render_template('compare.html')

if __name__ == "__main__":
    app.run(debug=True)

