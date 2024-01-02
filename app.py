#%%
import os
import json

import io
import logging

from flask import (
    redirect,
    send_file,
    Flask,
    render_template,
    request,
    send_from_directory,
    url_for,
    jsonify
)
from flask_cors import CORS

# from werkzeug.wsgi import wrap_file
# from werkzeug.datastructures import Headers

import export_doc
import main_gpt

global client

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
   """
   Testing API
   """
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
def first_run():
    """
    Main API function to run the first generation
    """
    data = request.get_json()
    logging.info("API request param:", data)
    # client meaning client name here
    #TODO:
    section_name = data["section_name"]
    #=================================
    #TODO: Temp correction for the name of "Industry / Section Analysis"
    if section_name.strip() == "Industrial Section Analysis":
        section_name = "Industry / Section Analysis"
    #=================================
    client = data["client"]
    rm_note_txt = data["rm_note_txt"]
    output_json = main_gpt.run_first_gen(section_name, rm_note_txt, client) 

    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(output_json)

@app.route('/regen', methods=['POST'])
def regen():
    """
    Main API function to run the re-generation
    """
    data = request.get_json()
    logging.info("API request param:", data)
    section_name = data["section_name"]
    #=================================
    #TODO: Temp correction for the name of "Industry / Section Analysis"
    if section_name.strip() == "Industrial Section Analysis":
        section_name = "Industry / Section Analysis"
    #=================================
    previous_paragraph = data["previous_paragraph"]
    rm_instruction = data["rm_instruction"]
    
    #TODO: 2023-12-27 Temp fix for adding client for regen function
    #client = data["client"]
    output_json = main_gpt.regen(section_name, previous_paragraph, rm_instruction, client="GogoX")
    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(output_json)

@app.route('/export', methods=['POST'])
def export_document():
    """
    Main API function to export the docx document
    """
    try:
        data = request.get_json()
        if not data or "client_name" not in data or "consolidated_text" not in data:
            return jsonify({"error": "Invalid request data"}), 400

        logging.info("API request param:", data)
        client_name = data["client_name"]
        consolidated_text = data["consolidated_text"]
        blob_name, document_bytes = export_doc.create_docx(client_name, consolidated_text)
  
        # if (not blob_name) | (not container_name) | (not document_bytes):
        #     return jsonify({"error": "Failed to create document"}), 500

        # Convert BytesIO to a file-like object
        document_bytes.seek(0)
        file_like_object = io.BytesIO(document_bytes.read())

        return send_file(
            file_like_object,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            attachment_filename=blob_name
        )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Unexpected error occurred"}), 500

if __name__ == '__main__':
   app.debug = True
   app.run()
