from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'app.sqlite')

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

# Player model
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    score = db.Column(db.Integer)

    def __init__(self, username, password, score=0):
        self.username = username
        self.password = password
        self.score = score

# Player schema for serialization
class PlayerSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'score')

player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if player exists and password is correct
    player = Player.query.filter_by(username=username).first()
    if player and player.password == password:
        return jsonify({'message': 'Login successful'})
    
    return jsonify({'message': 'Invalid username or password'}), 401

# Get all players endpoint
@app.route('/players', methods=['GET'])
def get_players():
    all_players = Player.query.all()
    result = players_schema.dump(all_players)
    return jsonify(result)

# Get a specific player endpoint
@app.route('/players/<username>', methods=['GET'])
def get_player(username):
    player = Player.query.filter_by(username=username).first()
    if player:
        result = player_schema.dump(player)
        return jsonify(result)
    
    return jsonify({'message': 'Player not found'}), 404

# Add a new player endpoint
@app.route('/players', methods=['POST'])
def add_player():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if player already exists
    existing_player = Player.query.filter_by(username=username).first()
    if existing_player:
        return jsonify({'message': 'Username already taken'}), 400
    
    # Create new player
    new_player = Player(username, password)
    db.session.add(new_player)
    db.session.commit()
    result = player_schema.dump(new_player)
    return jsonify(result), 201


if __name__ == '__main__':
    app.run(debug=True)

