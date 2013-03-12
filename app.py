from flask import Flask, render_template, request, make_response, url_for, send_from_directory, redirect
import datetime
import json
import dateutil.parser
import hashlib
import os
import pymongo
import random
import sys
import urlparse
import uuid

app = Flask(__name__)

mongo_url = os.getenv('MONGOHQ_URL', 'mongodb://localhost:27017/paperpets')
try:
    db = pymongo.Connection(mongo_url)[urlparse.urlparse(mongo_url).path[1:]]
except pymongo.errors.ConnectionFailure, e:
    db = None
    print e
    print >>sys.stderr, 'Could not connect to MongoDB, not logging pets.'

@app.route("/")
def index():
    return make_response(render_template('index.html'))

@app.route("/sample/")
def sample():
  response = make_response(render_template('sample.html'))
  return response

  
@app.route("/edition/")
def edition():
    # NO CHEATING
    random.seed()
    
    # Berg stuff
    if request.args.get('local_delivery_time', False):
        date = dateutil.parser.parse(request.args['local_delivery_time'])
    else:
        date = datetime.date.today()
    
    response = make_response()
    
    # only return a pet if its a weekend
    if date.weekday() == 5 or date.weekday() == 6:

      # Pick random animal
      pet_names = pets.keys()
      weights = [pets[name].get('probability', 1) for name in pet_names]
      pet = request.args.get('pet', pet_names[weighted_choice(weights)])
    
    
      # Pick characters within chosen animal
      character_names = pets[pet]['characters'].keys()
      weights = [pets[pet]['characters'][character] for character in character_names]
    
      character_name = request.args.get('character_name', character_names[weighted_choice(weights)])

      rarity = pets[pet]['characters'][character] * pets[name].get('probability', 1)
      rarity_descriptor =''
    
      # rarity scale used in ebay coin collecting
      if rarity == 1:
        rarity_descriptor = 'extremely rare'
      elif rarity == 2:
        rarity_descriptor = 'very rare'
      elif rarity == 3:
        rarity_descriptor = 'rare'
 
    
      variations = {}
      variations['pattern'] = pets[pet]['traits'][character_name]['pattern']
      variations['character'] = character_name.lower()
    
    
    
      # Log edition
      #if db is not None:
      #  db.editions.insert({
      #     # convert datetime.date to datetime.datetime
      #      'local_delivery_time': datetime.datetime.combine(date, datetime.time()),
      #      'generation_date': datetime.datetime.utcnow(),
      #      'user_id': user_id,
      #      'name': name,
      #      'pet': pet,
      #      'variations': variations
      #  })

      response = make_response(render_template('edition.html', 
          pet=pet,
          meta=pets[pet],
          name=character_name,
          variations=variations,
          rarity=rarity_descriptor,
          pet_id=pets[pet]['traits'][character_name]['id']
      ))
      
    
    etag = "%032x" % random.getrandbits(128)
    response.headers['ETag'] = etag
    return response


# Add the routes for the static files so they are at root
@app.route('/meta.json')
def meta_json():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'meta.json', mimetype='application/json')


@app.route('/icon.png')
def icon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'icon.png', mimetype='image/png')


def load_pets():
    """
    Returns a dictionary mapping pet name to its metadata.
    """
    pets = {}
    #pet_names = os.listdir(os.path.join(app.static_folder, 'pets'))
    pet_names =['fox', 'penguin', 'dino', 'whale', 'bunny']
    for name in pet_names:
        pet_dir = os.path.join(app.static_folder, 'pets', name)
        pets[name] = json.load(open(os.path.join(pet_dir, 'meta.json')))
    return pets


def weighted_choice(weights):
    """
    http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/
    """
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

pets = load_pets()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

