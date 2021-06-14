import os
import random

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


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
        
        print("START")
        return "ok"

    def print_board(self, data):
      board = [['.' for x in range(self.width)] for y in range(self.height)]
      for food in data["board"]["food"]:
        board[food["y"]][food["x"]] = "F"
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
      for row in range(self.height-1, 0, -1):
        print(''.join(board[row]))
  
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = cherrypy.request.json

        self.width = data["board"]["width"]
        self.height = data["board"]["height"]
        self.me = data["you"]
        self.x = self.me["head"]["x"]
        self.y = self.me["head"]["y"]
        print("x,y=%d,%d" % (self.x, self.y))

        self.print_board(data)

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        move = random.choice(possible_moves)

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
