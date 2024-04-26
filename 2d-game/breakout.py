from DIPPID import SensorUDP
import math
import pyglet
from pyglet import shapes, clock
import os

#TODO: paddle size größer machen wenn top getroffen & increasing ball speed

PORT = 5700
sensor = SensorUDP(PORT)

WINDOW_WIDTH = 370
WINDOW_HEIGHT = 480
GAME_TIME = 90

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
batch = pyglet.graphics.Batch()

score = 0
time = GAME_TIME
lost = False

# Generated with ChatGPT
def seconds_to_minutes(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return "{:02d}:{:02d}".format(minutes, remaining_seconds)

# Generated with ChatGPT
def euclidian_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def count_time(deltaTime):
    global time
    time -= 1
    time_label.text = seconds_to_minutes(time)


score_label = pyglet.text.Label(text=f'Score: {score}',
                                font_name='Arial',
                                font_size=15,
                                bold=True,
                                x=WINDOW_WIDTH - (WINDOW_WIDTH - 10), y=WINDOW_HEIGHT - 22, batch=batch)

time_label = pyglet.text.Label(text=seconds_to_minutes(time),
                               font_name='Arial',
                               font_size=15,
                               bold=True,
                               x=WINDOW_WIDTH - 60, y=WINDOW_HEIGHT - 22, batch=batch)


class Player():

    def __init__(self, x=184) -> None:
        self.x = 184
        self.y = 50
        self.width = 50
        self.height = 10
        self.color = (171, 219, 227)
        self.shape = shapes.BorderedRectangle(x=self.x,
                                              y=self.y,
                                              width=self.width,
                                              height=self.height,
                                              color=self.color,
                                              batch=batch)
        # Sensordaten glättung -> Hilfe von ChatGPT -> Siehe GPT-Prompts -> calculate_moving_average gehört dazu
        self.sensor_values = []
        self.sensor_window_size = 5

    def calculate_moving_average(self, new_value):
        self.sensor_values.append(new_value)
        if len(self.sensor_values) > self.sensor_window_size:
            self.sensor_values.pop(0)
        return sum(self.sensor_values) / len(self.sensor_values)

    def update_player(self, deltaTime) -> float:
        pos_x = player.shape.x
        if (sensor.has_capability('rotation')):
            rotation = float(sensor.get_value('rotation')['pitch'])

            # Smoothed rotation brauche ich doch nicht
            # smoothed_rotation = self.calculate_moving_average(rotation)

            # center the player
            pos_x = WINDOW_WIDTH / 2 + rotation * 5

            # check for borders
            if pos_x < 0:
                pos_x = 0
            elif pos_x > WINDOW_WIDTH - player.width:
                pos_x = WINDOW_WIDTH - player.width
        return pos_x


class Bricks():
    bricks = []

    def __init__(self, x, y, color, score):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 15
        self.color = color
        self.score = score
        self.shape = shapes.Rectangle(x=self.x,
                                      y=self.y,
                                      width=self.width,
                                      height=self.height,
                                      color=self.color,
                                      batch=batch)

    def generate_bricks():
        for row in range(4):
            if row < 1:
                # blue
                color = (30, 129, 176)
                score = 7
            elif row < 2:
                # sand
                color = (238, 238, 228)
                score = 5
            elif row < 3:
                # orange
                color = (226, 135, 67)
                score = 3
            else:
                # light yellow
                color = (234, 182, 118)
                score = 1

            # y-coordinate
            y = 400 - (10 * (row + 1) + 10 * row)
            for col in range(10):
                # x-coordinate
                x = 10 * (col + 1) + 25 * col
                Bricks.bricks.append(Bricks(x, y, color, score))

    def update_bricks():
        for index, brick in enumerate(Bricks.bricks):
            if ball.check_collision_object(brick):
                global score
                score += brick.score
                ball.handle_brick_collision(index)


class Ball():
    RADIUS = 5

    def __init__(self, x=184, y=100) -> None:
        self.x = 184
        self.y = 100
        self.radius = self.RADIUS
        self.color = (128, 57, 30)
        self.shape = shapes.Circle(x=self.x,
                                   y=self.y,
                                   radius=self.radius,
                                   color=self.color,
                                   batch=batch)

        # Ab hier von CHATGPT inspiriert und von mir verändert --------------------
        self.vx = 100
        self.vy = 100

    def update_ball(self, deltaTime):
        self.shape.x += self.vx * deltaTime
        self.shape.y += self.vy * deltaTime

    # Check borders and reflect ball. If the ball touches the bottom -> gameo ober!
    def handle_collision_wall(self):
        # left and right
        if self.shape.x <= self.RADIUS or self.shape.x >= WINDOW_WIDTH - self.RADIUS:
            self.vx = -self.vx

        # top
        if self.shape.y >= WINDOW_HEIGHT - self.RADIUS:
            self.vy = -self.vy

        # bottom
        if self.shape.y <= self.RADIUS:
            global lost
            lost = True
            clock.schedule_interval(game_over, 0.005)

    # --------------------------------------------------------------------------------

    def check_collision_object(self, other):
        collision_distance = self.radius + other.height
        # Calculation with the help of ChatGPT
        distance = euclidian_distance(self.shape.x, self.shape.y, other.shape.x + other.width/2, other.shape.y)
        return distance <= collision_distance

    def handle_player_collision(self):
        self.vy = self.vy * -1

    def handle_brick_collision(self, index):
        self.vy = self.vy * -1
        del Bricks.bricks[index]


@window.event
def update(deltaTime):
    window.clear()
    global player, ball, score, time, lost
    Bricks.update_bricks()

    # player movement
    player.shape.x = player.update_player(deltaTime)

    # ball movement
    ball.update_ball(deltaTime)

    # collision events
    if ball.check_collision_object(player):
        ball.handle_player_collision()

    ball.handle_collision_wall()

    score_label.text = f'Score: {score}'

    batch.draw()


@window.event
def on_key_press(symbol, modifiers):
    match(symbol):
        case pyglet.window.key.Q:
            os._exit(0)
        case pyglet.window.key.R:
            window.clear()
            clock.unschedule(game_over)

            global score, time, lost

            score = 0
            time = GAME_TIME
            lost = False

            ball.shape.x = 184
            ball.shape.y = 100
            ball.vx = 100
            ball.vy = 100

            player.shape.x = 184
            player.shape.y = 50
            game_start()


@window.event
def time_up(deltaTime):
    clock.schedule_interval(game_over, 0.005)


@window.event
def game_over(deltaTime):
    window.clear()
    clock.unschedule(update)
    clock.unschedule(count_time)
    global lost

    game_over_label = pyglet.text.Label(text='GAME OVER :(',
                                        font_name='ARIAL',
                                        font_size=34,
                                        bold=True,
                                        x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
                                        anchor_x='center', anchor_y='center'
                                        )

    congrats_label = pyglet.text.Label(text='Congratulations!',
                                       font_name='ARIAL',
                                       font_size=34,
                                       bold=True,
                                       x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//2,
                                       anchor_x='center', anchor_y='center'
                                       )

    final_score_label = pyglet.text.Label(text=f'FINAL SCORE: {score}',
                                          font_name='ARIAL',
                                          font_size=20,
                                          bold=True,
                                          x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT * 1/3,
                                          anchor_x='center'
                                          )

    retry_label = pyglet.text.Label(text=f'Press R to replay!',
                                    font_name='ARIAL',
                                    font_size=10,
                                    bold=True,
                                    x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT * 1/5,
                                    anchor_x='center'
                                    )

    if lost:
        game_over_label.draw()
    else:
        congrats_label.draw()

    final_score_label.draw()
    retry_label.draw()


def game_start():
    Bricks.generate_bricks()

    # update every 1/120 seconds to get 120 fps
    update_interval = 1/120

    clock.schedule_interval(update, update_interval)
    clock.schedule_interval(count_time, 1)
    clock.schedule_once(time_up, GAME_TIME)


if __name__ == '__main__':
    player = Player()
    ball = Ball()

    game_start()
    pyglet.app.run()
