import os
import json
import flask
from flask import redirect, send_file
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from flask_cors import CORS
import logging
from werkzeug.wsgi import wrap_file
import export_doc
import extract_info


app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


# route for healthcheck
@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    # Returning an api for showing in reactjs
    return {"status": "OK"}


# route for extracting information from RM notes
@app.route('/generate', methods=['POST'])
def extract_rm_notes():

    data = request.get_json()
    logging.info("API request param:", data)
    #client_name = data["client_name"]
    section_name = data["section_name"]
    # Client_name = Client_name + "_rm_note.json"
    rm_note_txt = data["rm_note_txt"]
    output_json = extract_info.run_first_gen(section_name, rm_note_txt) 

    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(output_json)


@app.route('/regen', methods=['POST'])
def regen():
    data = request.get_json()
    logging.info("API request param:", data)
    section_name = data["section_name"]
    previous_paragraph = data["previous_paragraph"]
    rm_instruction = data["rm_instruction"]
    output_json = extract_info.regen(section_name, previous_paragraph, rm_instruction)
    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(output_json)

@app.route('/export', methods=['POST'])
def export_document():
    try:
        data = request.get_json()
        if not data or "client_name" not in data or "consolidated_text" not in data:
            return jsonify({"error": "Invalid request data"}), 400

        logging.info("API request param:", data)
        client_name = data["client_name"]
        consolidated_text = data["consolidated_text"]
        blob_name, container_name, storage_service, document_bytes = export_doc.create_docx(client_name, consolidated_text)
  
        if not blob_name or not container_name or not storage_service or not document_bytes:
            return jsonify({"error": "Failed to create document"}), 500

        blob_url = f"https://{storage_service}.blob.core.windows.net/{container_name}/{blob_name}"
        response_json = {
            "message": "Document created successfully",
            "redirect_url": blob_url
        }

        # Prepare the document part of the response
        document_part = wrap_file(request.environ, document_bytes)
        document_headers = Headers()
        document_headers.add('Content-Disposition', 'attachment', filename=blob_name)
        document_headers.add('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        # Prepare the JSON part of the response
        json_part = Response(json.dumps(response_json), mimetype='application/json')

        # Create a multipart response
        response = Response(mimetype='multipart/mixed')
        response.response = [document_part, json_part]
        response.headers = document_headers

        return response
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Unexpected error occurred"}), 500

if __name__ == '__main__':
   app.run()
if __name__ == '__main__':
   app.run()
