from flask import Flask, render_template, request, make_response, url_for, send_from_directory, redirect
import datetime
import json
import dateutil.parser
import hashlib
import os
import random

app = Flask(__name__)

@app.route("/")
def index():
    return redirect('/edition/')

@app.route("/edition/")
@app.route("/sample/")
def edition():

    # Check for required vars
    if request.args.get('local_delivery_time', False):
        date = dateutil.parser.parse(request.args['local_delivery_time'])
    else:
        date = datetime.date.today()
        
    lang = request.args.get('lang', 'english')
    name = request.args.get('name', 'Little Printer')

    pets = os.listdir(os.path.join(app.static_folder, 'pets'))

    pet = request.args.get('pet', random.choice(pets))
    pet_dir = os.path.join(app.static_folder, 'pets', pet)

    meta = json.load(open(os.path.join(pet_dir, 'meta.json')))

    # Set the etag to be this content. This means the user will not get the same content twice, 
    # but if they reset their subscription (with, say, a different language they will get new content 
    # if they also set their subscription to be in the future)
    response = make_response(render_template('edition.html', 
        pet=pet,
        meta=meta,
    ))
    #etag = hashlib.sha224(language+name+date.strftime('%d%m%Y')).hexdigest()
    etag = "%032x" % random.getrandbits(128)
    response.headers['ETag'] = etag
    return response

#Validate config e.g. /validate_config/?config={"lang":"english","name":"Pablo"}
@app.route("/validate_config/")
def validate_config():
    json_response = {'errors': [], 'valid': True}

    # Extract config from POST
    user_settings = json.loads(request.args['config'])
    
    # If the user did choose a language:
    if not user_settings.get('lang', None):
        json_response['valid'] = False
        json_response['errors'].append('Please select a language from the select box.')

    # If the user did not fill in the name option:
    if not user_settings.get('name', None):
        json_response['valid'] = False
        json_response['errors'].append('Please enter your name into the name box.')

    # Is a valid language set?
    if user_settings.get('language', None) in greetings:
        json_response['valid'] = False
        json_response['errors'].append("We couldn't find the language you selected (%s) Please select another" % user_settings['language'])
    
    response = make_response(json.dumps(json_response))
    response.mimetype = 'application/json'
    return response

# Add the routes for the static files so they are at root
@app.route('/meta.json')
def meta_json():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'meta.json', mimetype='application/json')

@app.route('/icon.png')
def icon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'icon.png', mimetype='image/png')
                                       
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
