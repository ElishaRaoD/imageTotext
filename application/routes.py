from application import app, utils, db
from flask import render_template, request, redirect, session, send_file
from application.forms import QRCodeData
# import secrets
import os
# from PIL import Image
# OCR
import cv2
import easyocr
# pip install gTTS
from gtts import gTTS

from application.model import ImageRecord


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        # set a session value
        sentence = ""

        global filename
        f = request.files.get('file')
        filename = f.filename
        file_location = os.path.join(app.config['UPLOADED_PATH'], filename)
        f.save(file_location)

        print(file_location)

        # OCR here
        reader = easyocr.Reader(['ja', 'en'])

        img = cv2.imread(file_location)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = reader.readtext(img)
        extracted_text = ' '.join([res[1] for res in results])
        print(extracted_text)

        extracted_filename = filename.split('.')[0] + '_extracted.txt'

        with open(os.path.join(app.config['EXTRACTED_TEXT_UPLOAD'], extracted_filename), 'w',
                  encoding='utf-8') as extracted_file:
            extracted_file.write(extracted_text)
            f.save(extracted_file)

            print(extracted_file)

            print(extracted_filename)

            # Save the image record in the database
            image_record = ImageRecord(
                original_filename=filename,
                extracted_text=extracted_text,
                # translated_text=translated_text,
                # audio_filename=audio_filename
            )
            db.session.add(image_record)
            # db.session.commit()

        session["extracted_text"] = extracted_text
        # delete file after you are done working with it
        os.remove(file_location)

        return redirect("/decoded/")
    else:
        return render_template("upload.html", title="Home")


@app.route('/result')
def result():
    # Retrieve image records from the database (you need to implement this part)
    image_records = ImageRecord.query.all()
    return render_template('result.html', image_records=image_records)


@app.route('/download', methods=['GET'])
def download():
    global filename
    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')
        filename = f.filename
        file_location = os.path.join(app.config['UPLOADED_PATH'], filename)

    extracted_filename = filename.split('.')[0] + '_extracted.txt'
    path = 'static/extracted_text/' + extracted_filename
    print(path)
    return send_file(path, as_attachment=True)


@app.route("/decoded", methods=["GET", "POST"])
def decoded():
    global filename
    sentence = session.get("extracted_text")
    lang, _ = utils.detect_language(sentence)

    sentences = session.get("sentences")
    lang, _ = utils.detect_language(sentences)

    form = QRCodeData()
    if request.method == 'POST':

        if request.method == 'POST' and 'file' in request.files:
            f = request.files.get('file')
            filename = f.filename
            file_location = os.path.join(app.config['UPLOADED_PATH'], filename)

        text_data = form.data_field.data
        translate_to = form.language.data
        # print("Data here", translate_to)

        translated_text = utils.translate_text(text_data, translate_to)
        print(translated_text)

        # translated_filename = secrets.token_hex(2) + '_translated.txt'
        translated_filename = filename.split('.')[0] + '_translated.txt'

        with open(os.path.join(app.config['TRANSLATED_TEXT_UPLOAD'], translated_filename), 'w',
                  encoding='utf-8') as translated_file:
            translated_file.write(translated_text)

        # translated_text.save(translated_file)

        print(translated_file)

        # Generate audio output
        tts = gTTS(translated_text, lang=translate_to)
        generated_audio_filename = filename.split('.')[0] + '.mp3'
        file_location = os.path.join(
            app.config['AUDIO_FILE_UPLOAD'],
            generated_audio_filename
        )
        # save file as audio
        tts.save(file_location)

        form.data_field.data = translated_text

        image_record = ImageRecord(
            original_filename=filename,
            # extracted_text=extracted_text,
            translated_text=translated_text,
            audio_filename=generated_audio_filename
        )
        db.session.add(image_record)
        # db.session.commit()

        return render_template("decoded.html",
                               title="Decoded",
                               form=form,
                               lang=utils.languages.get(lang),
                               audio=True,
                               file=generated_audio_filename
                               )

    form.data_field.data = sentence
    session["sentence"] = ""

    return render_template("decoded.html",
                           title="Decoded",
                           form=form,
                           lang=utils.languages.get(lang),
                           audio=False
                           )


@app.route('/download1', methods=['GET'])
def download1():
    global filename

    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')
        filename = f.filename
        file_location = os.path.join(app.config['UPLOADED_PATH'], filename)

    translated_filename = filename.split('.')[0] + '_translated.txt'
    path = 'static/translated_text/' + translated_filename
    print(path)
    return send_file(path, as_attachment=True)