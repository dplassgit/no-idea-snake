import os
import random

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
possible_moves = ["up", "down", "left", "right"]
moves_dx = [0, 0, -1, 1]
moves_dy = [1, -1, 0, 0]

class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "dplassgit",
            "color": "#ff00ff",
            "head": "bendr",
            "tail": "pixel",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        self.last_move = -1
        print("START")
        return "ok"

    def make_board(self, data):
      board = [['.' for x in range(self.width)] for y in range(self.height)]
      self.foods = []
      for food in data["board"]["food"]:
        board[food["y"]][food["x"]] = "F"
        self.foods.append((food["y"], food["x"]))
      for snake in data["board"]["snakes"]:
        body = snake["body"]
        for segment in body:
          board[segment["y"]][segment["x"]] = "e"
        head = snake["head"]
        board[head["y"]][head["x"]] = "E"
      you = data["you"]
      for segment in you["body"]:
        board[segment["y"]][segment["x"]] = "m"
      head = you["head"]
      board[head["y"]][head["x"]] = "M"
      return board
  
    def good_move(self, try_move_idx):
      good = True
      dx = moves_dx[try_move_idx]
      dy = moves_dy[try_move_idx]
      good = good and (self.y+dy >= 0)
      good = good and (self.x+dx >= 0)
      good = good and (self.y+dy < self.height)
      good = good and (self.x+dx < self.width)
      if good:
        good = self.board[self.y+dy][self.x+dx] in ('.', 'F')

      return good

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = cherrypy.request.json

        self.width = data["board"]["width"]
        self.height = data["board"]["height"]
        self.me = data["you"]
        self.health  = self.me["health"]
        self.x = self.me["head"]["x"]
        self.y = self.me["head"]["y"]
        print("x,y=%d,%d" % (self.x, self.y))

        self.board = self.make_board(data)
        #for row in range(self.height, 0, -1):
        #  print(''.join(self.board[row]))

        # Pick a direction to move in, unless it's bad
        if self.last_move == -1:
          self.last_move = 0

        move = ''
        if self.good_move(self.last_move):
          move = possible_moves[self.last_move]
        else:
          for i in range(0, 4):
            if self.good_move(i):
              move = possible_moves[i]
              self.last_move = i
              break
        if move == '':
          print("Could not find a good move!")
          move = "up"
        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
