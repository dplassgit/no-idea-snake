import os
import random
import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
move_names = ["up", "down", "left", "right"]
moves_dx = [0, 0, -1, 1]
moves_dy = [1, -1, 0, 0]

class AnSnake(object):
  pass

# Map from key to AnSnake objects
snakes = {}

class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "APIVersion": "1",
            "Author": "dplassgit",
            "Color": "#0000ff",
            "Head": "bendr",
            "Tail": "pixel",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        self.last_move = -1
        self.food_target = None
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
      # avoid the outer edge unless very hungry
      if self.health < 40:
        limit = 0
      else:
        limit = 1
      good = good and (self.y+dy > limit - 1)
      good = good and (self.x+dx > limit - 1)
      good = good and (self.y+dy < self.height - limit)
      good = good and (self.x+dx < self.width - limit)
      if good:
        # TODO: if there's a head within this area and
        # their length is greater than mine, run away
        # If their length is smaller, it's still good.
        good = self.board[self.y+dy][self.x+dx] in ('.', 'F')

      if not good:
        # allow us to stay in the outer edge
        limit = 0
        good = good and (self.y+dy > limit - 1)
        good = good and (self.x+dx > limit - 1)
        good = good and (self.y+dy < self.height - limit)
        good = good and (self.x+dx < self.width - limit)
      if good:
        # TODO: if there's a head within this area and
        # their length is greater than mine, run away
        # If their length is smaller, it's still good.
        good = self.board[self.y+dy][self.x+dx] in ('.', 'F')
      return good

    # return a (good) move towards food
    def move_towards_food(self):
      if not self.foods:
        self.food_target = None
        return ''
      if not self.food_target:
        # 1. pick random food
        self.food_target  = random.choice(self.foods)    
      print("going towards food", str(self.food_target))
      # 2. move towards it, if there's a good_move
      dx = self.food_target[1] - self.x
      dy = self.food_target[0] - self.y

      # right
      if dx > 0 and self.good_move(3):
        print("trying to go right towards food")
        return move_names[3]
      # left
      if dx < 0 and self.good_move(2):
        print("trying to go left towards food")
        return move_names[2]
      # down
      if dy < 0 and self.good_move(1):
        print("trying to go down towards food")
        return move_names[1]
      # up
      if dy > 0 and self.good_move(0):
        print("trying to go up towards food")
        return move_names[0]

      print("no good move towards food target")
      self.food_target = None
      # 3. TODO: if no good move, try a different food
      return ''

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
      
        self.board = self.make_board(data)
        # for row in range(self.height - 1, -1, -1):
        #   print(''.join(self.board[row]))

        # Pick a direction to move in, unless it's bad
        if self.last_move == -1:
          self.last_move = 0

        move = ''
        # if hungry, move towards food
        if self.health < 40:
          move = self.move_towards_food()

        if move == '':
          # Otherwise, keep going in the same direction if possible.
          if self.good_move(self.last_move):
            move = move_names[self.last_move]
          else:
            for i in range(0, 4):
              if self.good_move(i):
                move = move_names[i]
                self.last_move = i
                break
        if move == '':
          print("Could not find a good move!")
          move = "up"
        print(f"MOVE: {move} at {self.x}, {self.y} health {self.health}")
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
