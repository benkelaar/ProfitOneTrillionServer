from google.appengine.ext import webapp

import json
import logging
import copy

ids = 0
games = dict();
openGames = [game for (_, game) in games if not game.has_started()]

profitDict = {
    "Ceres": 522.0,
    "Isis": 521.0,
    "Hestia": 453.0,
    "Doris": 371.0,
    "Angelina": 797.0,
    "Niobe": 490.0,
    "Beatrix": 456.0,
    "Aurora": 390.0,
    "Aegle": 398.0,
    "Lydia": 539.0,
    "Kassandra": 836.0,
    "Meliboea": 423.0,
    "Juewa": 435.0,
    "Polana": 847.0,
    "Adria": 675.0,
    "Baucis": 720.0,
    "Ino": 388.0,
    "Oceana": 531.0,
    "Russia": 759.0,
    "Kriemhild": 546.0,
    "Bettina": 427.0,
    "Aletheia": 501.0,
    "Amalia": 747.0,
    "Bavaria": 803.0,
    "Heidelberga": 972.0,
    "Lacadiera": 379.0,
    "Dorothea": 613.0,
    "Pariana": 369.0,
    "May": 532.0,
    "Padua": 912.0,
    "Aeria": 557.0,
    "Dodona": 519.0,
    "Janina": 554.0,
    "Delia": 795.0,
    "Vienna": 997.0,
    "Admete": 649.0,
    "Natalie": 609.0,
    "Venusia": 430.0
}

def _game_from_blob(blob):
    jsonDict = json.loads(blob)
    gameId = jsonDict["gameId"]
    return games[gameId], jsonDict

def _set_response(response, responseDict):
    response.headers['Content-Type'] = 'application/json'
    response.out.write(json.dumps(responseDict)) # Game ID


class Game():
    def __init__(self, playerOne, playerTwo=None):
        self.gameId = ids+1
        ids = self.gameId
        self.playerOne = playerOne
        self.playerTwo = playerTwo
        self.asteroids = copy.deepcopy(profitDict)
    
    def has_started(self):
        return self.playerTwo is not None

class Player():
    def __init__(self, name, location, color, profit=0):
        self.name = name
        self.location = location
        self.color = color
        self.profit = profit

class Start(webapp.RequestHandler):
    def post(self):
        blob = self.request.get('json')
        responseDict = {}
        try:
            player = json.loads(blob)
            game = Game(player)
            games[game.gameId] = game
            responseDict["id"] = game.gameId
        except:
            logging.error("Exception reading data for new game.")
            pass
        _set_response(self.response, responseDict)
        
    def get(self):
        blob = self.request.get('json')
        responseDict = {}
        try:
            game, _ = _game_from_blob(blob)
            responseDict["started"] = game.has_started()
            if game.has_started():
                responseDict["opponent"] = game.playerTwo
        except:
            logging.error("Exception reading data for game check.")
            responseDict["started"] = False
       
        _set_response(self.response, responseDict)

class Move(webapp.RequestHandler):        
    def post(self):
        blob = self.request.get('json')
        responseDict = {}
        try:
            game, move = _game_from_blob(blob)
            name = move["name"]
            target = move["target"]
            mined = move["mined"]
            opponent = game.playerTwo if game.playerOne.name == name else game.playerOne
            player = game.playerOne if game.playerOne.name == name else game.playerTwo
            sourceMetals = game.asteroids[player.location]
            moveAllowed = opponent.location != target
            mineAllowed = sourceMetals - mined > -3
            responseDict["moveAllowed"] = moveAllowed
            responseDict["mineAllowed"] = mineAllowed
            if mineAllowed:
                game.asteroids[player.location] = sourceMetals - mined
            if moveAllowed:
                player.location = target
                player.profit = move["profit"]
        except:
            logging.error("Exception reading data for move.")
            pass
        _set_response(self.response, responseDict)
        
class Join(webapp.RequestHandler):
    def post(self):
        blob = self.request.get('json')
        responseDict = {}
        try:
            game, jsonDict = _game_from_blob(blob)
            game.playerTwo = jsonDict["player"]
            responseDict["started"] = game.has_started()
        except:
            logging.error("Exception reading data joining game.")
            responseDict["started"] = False
        _set_response(self.response, responseDict)        
         
    
    def get(self):
        _set_response(self.response, openGames)        


app = webapp.WSGIApplication([
        ('/move', Move),
        ('/start', Start),
        ('/join', Join)
        ], debug=True)