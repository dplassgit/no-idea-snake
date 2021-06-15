import os
import random
import cherrypy

"""
Dumb battlesnake server in python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""
move_names = ["up", "down", "left", "right"]
moves_dx = [0, 0, -1, 1]
moves_dy = [1, -1, 0, 0]

""" Snake object. """
class AnSnake(object):
  def __init__(self, data):
    self.width = data["board"]["width"]
    self.height = data["board"]["height"]
    me = data["you"]
    self.id = me["id"]
    self.last_move = -1
    self.food_target = None

  def make_board(self, data):
    board = [['.' for x in range(self.width)] for y in range(self.height)]
    # A fine foods amount.
    self.foods = []
    for food in data["board"]["food"]:
      board[food["y"]][food["x"]] = "F"
      self.foods.append((food["y"], food["x"]))

    # Mark enemy segments with "e"
    for snake in data["board"]["snakes"]:
      body = snake["body"]
      for segment in body:
        board[segment["y"]][segment["x"]] = "e"
      head = snake["head"]
      # The head
      # TODO: get length somewhere
      board[head["y"]][head["x"]] = "E"

    # Mark my segments with "m"
    you = data["you"]
    for segment in you["body"]:
      board[segment["y"]][segment["x"]] = "m"
    head = you["head"]
    board[head["y"]][head["x"]] = "M"

    return board

  # Ideas:
  # 1. evaluate each direction, pick best
  # 2. how to evaluate a move:
  #   *. if there's a blockage, -100 OK
  #   *. if it's in the same direction, +1 OK?
  #   *. if it has food and we're > 70 (modulo length?), +1 OK
  #   *. if it has food and we're < 40 +10 OK
  #   *. count "outs" - the more outs, the higher the score OK
  # 3. food override: if hungry, pick closest food and find the best move towards it. (?) (NOT DONE)
  # returns int
  def new_move_score(self, try_move_idx):
    # means it's not blocked
    dx = moves_dx[try_move_idx]
    dy = moves_dy[try_move_idx]
    movable = self.movable(self.y+dy, self.x+dx)
    if not movable:
      return -100
    # TODO: if there's a head within this area and
    # their length is smaller than mine, higher score
    # TODO: if the LOOKAHEAD has a head, score it.

    # the new location is free.
    score = 0
    if self.board[self.y+dy][self.x+dx] == 'F':
      if self.health < 40:
        score += 20
      elif self.length < self.width:
        # Care about food a little more if we're short.
        score += 3
      else:
        score += 1
    outs = self.count_outs(self.y+dy, self.x+dx)
    # 0 outs = bad
    score += 2*outs
    if try_move_idx == self.last_move:
      score += 1
    return score

  def count_outs(self, y, x):
    outs = 0
    if self.movable(y+1,x): 
      outs += 3
      if self.movable(y+2,x):
        outs += 1
      if self.movable(y+1,x+1):
        outs += 1
      if self.movable(y+1,x-1):
        outs += 1
    if self.movable(y-1,x): 
      outs += 3
      if self.movable(y-2,x):
        outs += 1
      if self.movable(y-1,x+1):
        outs += 1
      if self.movable(y-1,x-1):
        outs += 1
    if self.movable(y,x+1): 
      outs += 3
      if self.movable(y,x+2):
        outs += 1
      if self.movable(y+1,x+1):
        outs += 1
      if self.movable(y-1,x+1):
        outs += 1
    if self.movable(y,x-1): 
      outs += 3
      if self.movable(y,x-2):
        outs += 1
      if self.movable(y+1,x-1):
        outs += 1
      if self.movable(y-1,x-1):
        outs += 1

    return outs

  def movable(self, y, x):
    movable = True
    movable = movable and (y >= 0)
    movable = movable and (x >= 0)
    movable = movable and (y < self.height)
    movable = movable and (x < self.width)
    if not movable:
      return False
    return self.board[y][x] in ('.', 'F')

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

  def move(self, data):
    self.me = data["you"]
    self.x = self.me["head"]["x"]
    self.y = self.me["head"]["y"]
    self.health = self.me["health"]
    self.length =  self.me["length"]
  
    self.board = self.make_board(data)
    #for row in range(self.height - 1, -1, -1):
    #  print(''.join(self.board[row]))

    # Pick a direction to move in, unless it's bad
    if self.last_move == -1:
      self.last_move = 0

    move = ''
    # if hungry, move towards food
    #if self.health < 40:
      #move = self.move_towards_food()

    if move == '':
      # Find best move 
      best = -200
      best_idx = self.last_move
      for idx in range(0, 4):
        score = self.new_move_score(idx)
        print(f'Eval direction {move_names[idx]} score {score}')
        if score > best:
          best = score
          best_idx = idx
      move = move_names[best_idx]
      print(f'Picked direction {move} score {best}')
      self.last_move = best_idx

    if move == '':
      print("Could not find a good move!")
      move = "up"

    return move


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
      data = cherrypy.request.json
      snake = AnSnake(data)
      # extract id from data
      snakes[snake.id] = snake
      print(f"START id {snake.id}")
      return "ok"

  @cherrypy.expose
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  def move(self):
      data = cherrypy.request.json
      turn = data["turn"]
      me = data["you"]
      snake_id = me["id"]
      snake = snakes[snake_id]
      if snake:
        move = snake.move(data)
      else:
        print(f"WTF UNKNOWN SNAKE ID {snake_id} RECEIVED")
        snake = AnSnake(data)
        # extract id from data
        snakes[snake.id] = snake
        move = snake.move(data)

      print(f"MOVE: {move} at {snake.x}, {snake.y} health {snake.health} length {snake.length} turn {turn}")
      return {"move": move}

  @cherrypy.expose
  @cherrypy.tools.json_in()
  def end(self):
      data = cherrypy.request.json
      me = data["you"]
      snake_id = me["id"]
      del snakes[snake_id]
      snakes[snake_id] = None
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
  
