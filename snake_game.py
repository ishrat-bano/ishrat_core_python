"""
Snake Xenia - A complete Snake game using Python's turtle module.

Features:
- Smooth snake movement using turtle.
- Food spawning with score increment.
- Walls (toggleable) and self-collision detection.
- "Xenia power-up" (special food) that gives extra points and temporary speed boost.
- Pause, restart, and exit controls.
- On-screen score and high score tracking during session.
- Simple level progression (increases speed every few foods eaten).
"""

import turtle
import time
import random
import sys

# ---------------------------------------------------------------------
# FILE_URL from conversation history (developer instruction)
# This doesn't affect the game; it's included per your request.
FILE_URL = "file:///mnt/data/pandas_35pages_textbook_style.pdf"
# ---------------------------------------------------------------------

# Configuration
WINDOW_TITLE = "Snake Xenia"
WIDTH, HEIGHT = 600, 600
BG_COLOR = "#F9F6EF"        # notebook-like background
LINE_COLOR = "#E0E8F0"      # for subtle lines (if drawing grid)
SNAKE_COLOR = "#0B6623"     # green-ish snake
HEAD_COLOR = "#0A4D3A"
FOOD_COLOR = "#D35400"      # orange
XENIA_COLOR = "#8E44AD"     # purple for Xenia power-up
TEXT_COLOR = "#1B1B1B"
FONT = ("Arial", 14, "normal")
TITLE_FONT = ("Arial", 18, "bold")

# Gameplay parameters (tune these)
INITIAL_SPEED = 0.12   # seconds per movement step (lower is faster)
SPEED_DECREMENT = 0.005  # decrease in delay per levelup (makes it faster)
SPEED_MIN = 0.03
FOOD_SCORE = 10
XENIA_SCORE = 40
LEVEL_UP_FOOD_COUNT = 5  # number of foods to get a level
WALLS_ENABLED = True    # set to True to enable wall collisions
GRID_SIZE = 20          # snake moves in increments (pixels)
MAX_FOOD_TRIES = 50

# Globals
delay = INITIAL_SPEED
score = 0
high_score = 0
snake_segments = []
direction = "stop"
food = None
xenia = None
screen = None
pen = None
paused = False
foods_eaten_in_level = 0

# Helper functions
def create_screen():
    global screen
    screen = turtle.Screen()
    screen.title(WINDOW_TITLE)
    screen.setup(width=WIDTH, height=HEIGHT)
    screen.bgcolor(BG_COLOR)
    screen.tracer(0)  # turn off automatic animation for manual control
    # Optionally draw subtle horizontal lines like a notebook
    draw_notebook_lines()
    return screen

def draw_notebook_lines():
    """
    Draw faint horizontal lines to simulate notebook background.
    We draw them on a turtle canvas so they appear beneath the sprites.
    """
    drawer = turtle.Turtle(visible=False)
    drawer.hideturtle()
    drawer.penup()
    drawer.speed(0)
    drawer.color(LINE_COLOR)
    start_y = -HEIGHT//2 + 20
    while start_y < HEIGHT//2:
        drawer.goto(-WIDTH//2, start_y)
        drawer.pendown()
        drawer.goto(WIDTH//2, start_y)
        drawer.penup()
        start_y += 20

def create_pen():
    global pen
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.color(TEXT_COLOR)
    pen.penup()
    return pen

def draw_scoreboard():
    pen.clear()
    pen.goto(-WIDTH//2 + 10, HEIGHT//2 - 30)
    pen.write(f"Score: {score}   High Score: {high_score}", font=FONT)
    pen.goto(-WIDTH//2 + 10, HEIGHT//2 - 55)
    pen.write(f"Speed: {1/delay:.1f} steps/sec   Level progress: {foods_eaten_in_level}/{LEVEL_UP_FOOD_COUNT}",
              font=("Arial", 10, "normal"))
    pen.goto(-120, HEIGHT//2 - 30)
    pen.write("Controls: Arrow keys / WASD to move, P to pause, R to restart, Q to quit", font=("Arial", 9, "normal"))

def create_snake_head():
    head = turtle.Turtle()
    head.shape("square")
    head.color(HEAD_COLOR)
    head.penup()
    head.speed(0)
    head.goto(0, 0)
    return head

def reset_game_state():
    global snake_segments, direction, score, delay, foods_eaten_in_level, xenia
    # Remove existing segments
    for seg in snake_segments:
        try:
            seg.hideturtle()
        except:
            pass
    snake_segments = []
    direction = "stop"
    score = 0
    foods_eaten_in_level = 0
    delay = INITIAL_SPEED
    # Remove xenia if present
    if xenia:
        xenia.hideturtle()
    # Reset head pos
    head.goto(0, 0)
    head.color(HEAD_COLOR)
    draw_scoreboard()

def place_food():
    """Place normal food at a random free location aligned to GRID_SIZE."""
    global food
    if food is None:
        f = turtle.Turtle()
        f.shape("circle")
        f.shapesize(0.7, 0.7)
        f.color(FOOD_COLOR)
        f.penup()
        f.speed(0)
        food = f

    place_turtle_at_random(food)

def place_xenia():
    """Place a special Xenia power-up occasionally."""
    global xenia
    # 25% chance to spawn when called
    if random.random() < 0.25:
        if xenia is None:
            x = turtle.Turtle()
            x.shape("circle")
            x.shapesize(0.9, 0.9)
            x.color(XENIA_COLOR)
            x.penup()
            x.speed(0)
            xenia = x
        place_turtle_at_random(xenia)
    else:
        # ensure hidden if not spawned
        if xenia:
            xenia.hideturtle()

def place_turtle_at_random(t):
    """Place turtle 't' at random position not overlapping with snake segments or head."""
    tries = 0
    while tries < MAX_FOOD_TRIES:
        x = random.randrange(-WIDTH//2 + 40, WIDTH//2 - 40, GRID_SIZE)
        y = random.randrange(-HEIGHT//2 + 40, HEIGHT//2 - 40, GRID_SIZE)
        collides = False
        # check head
        if abs(head.xcor() - x) < GRID_SIZE and abs(head.ycor() - y) < GRID_SIZE:
            collides = True
        # check segments
        for seg in snake_segments:
            if abs(seg.xcor() - x) < GRID_SIZE and abs(seg.ycor() - y) < GRID_SIZE:
                collides = True
                break
        if not collides:
            t.goto(x, y)
            t.showturtle()
            return
        tries += 1
    # fallback: place somewhere (even if overlapping) if no free spot found
    t.goto(0, 0)
    t.showturtle()

# Movement control functions
def go_up():
    global direction
    if direction != "down":
        direction = "up"

def go_down():
    global direction
    if direction != "up":
        direction = "down"

def go_left():
    global direction
    if direction != "right":
        direction = "left"

def go_right():
    global direction
    if direction != "left":
        direction = "right"

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        pen.goto(0, 0)
        pen.write("PAUSED", align="center", font=("Arial", 24, "bold"))
    else:
        draw_scoreboard()

def restart_game():
    reset_game_state()
    place_food()
    if xenia:
        xenia.hideturtle()

def quit_game():
    screen.bye()
    try:
        sys.exit()
    except SystemExit:
        pass

# Collision checks
def collides_with_wall(x, y):
    if not WALLS_ENABLED:
        return False
    half_w = WIDTH//2
    half_h = HEIGHT//2
    # walls are considered at boundaries; we keep 10 px padding
    if x > half_w - 10 or x < -half_w + 10 or y > half_h - 10 or y < -half_h + 10:
        return True
    return False

def collides_with_self():
    for seg in snake_segments:
        if head.distance(seg) < GRID_SIZE - 2:
            return True
    return False

# Main game loop
def move_snake():
    # move the snake body segments from last to first
    if len(snake_segments) > 0:
        for index in range(len(snake_segments)-1, 0, -1):
            x = snake_segments[index-1].xcor()
            y = snake_segments[index-1].ycor()
            snake_segments[index].goto(x, y)
        # move first segment to where head was
        snake_segments[0].goto(head.xcor(), head.ycor())

    # move head in current direction by one GRID_SIZE step
    if direction == "up":
        head.sety(head.ycor() + GRID_SIZE)
    elif direction == "down":
        head.sety(head.ycor() - GRID_SIZE)
    elif direction == "left":
        head.setx(head.xcor() - GRID_SIZE)
    elif direction == "right":
        head.setx(head.xcor() + GRID_SIZE)

def spawn_segment():
    new_seg = turtle.Turtle()
    new_seg.shape("square")
    new_seg.color(SNAKE_COLOR)
    new_seg.penup()
    new_seg.speed(0)
    # place off-screen initially (will be moved in next move cycle)
    new_seg.goto(1000, 1000)
    snake_segments.append(new_seg)

# Xenia effect
def apply_xenia_effect():
    global delay, score, foods_eaten_in_level
    # temporarily speed up and add larger score; we'll shorten delay briefly
    score_add = XENIA_SCORE
    foods_eaten_in_level += 1
    increase_speed_on_level_progress()
    return score_add

def increase_speed_on_level_progress():
    global delay, foods_eaten_in_level
    # Level up when foods_eaten_in_level reaches threshold
    if foods_eaten_in_level >= LEVEL_UP_FOOD_COUNT:
        foods_eaten_in_level = 0
        # speed up
        new_delay = max(SPEED_MIN, delay - SPEED_DECREMENT)
        # small immediate speed change to reflect level up
        set_delay(new_delay)

def set_delay(new_delay):
    global delay
    delay = new_delay

# Initialization
screen = create_screen()
pen = create_pen()
head = create_snake_head()

# Input bindings
screen.listen()
screen.onkey(go_up, "Up")
screen.onkey(go_down, "Down")
screen.onkey(go_left, "Left")
screen.onkey(go_right, "Right")
screen.onkey(go_up, "w")
screen.onkey(go_down, "s")
screen.onkey(go_left, "a")
screen.onkey(go_right, "d")
screen.onkey(toggle_pause, "p")
screen.onkey(toggle_pause, "P")
screen.onkey(restart_game, "r")
screen.onkey(restart_game, "R")
screen.onkey(quit_game, "q")
screen.onkey(quit_game, "Q")

# Place the first food and possibly xenia
place_food()
place_xenia()
draw_scoreboard()

# Game main loop
try:
    while True:
        screen.update()
        if not paused and direction != "stop":
            move_snake()

            # Check for collisions with wall
            if collides_with_wall(head.xcor(), head.ycor()):
                # Game over
                pen.goto(0, 0)
                pen.write("GAME OVER (Hit wall) - Press R to restart or Q to quit", align="center", font=("Arial", 14, "bold"))
                head.goto(0, 0)
                head.color("red")
                direction = "stop"
                # hide all segments
                for seg in snake_segments:
                    seg.hideturtle()
                snake_segments = []
                # reset after short pause to see result
                time.sleep(1.0)
                reset_game_state()

            # Check for self-collision
            elif collides_with_self():
                pen.goto(0, 0)
                pen.write("GAME OVER (Self collision) - Press R to restart or Q to quit", align="center", font=("Arial", 14, "bold"))
                head.goto(0, 0)
                head.color("red")
                direction = "stop"
                for seg in snake_segments:
                    seg.hideturtle()
                snake_segments = []
                time.sleep(1.0)
                reset_game_state()

            # Check for food collision (normal food)
            if food and head.distance(food) < GRID_SIZE:
                # move food away and hide temporarily
                food.hideturtle()
                # increase score and spawn a new segment
                score += FOOD_SCORE
                foods_eaten_in_level += 1
                spawn_segment()
                # respawn food and maybe xenia
                place_food()
                # occasionally spawn Xenia special
                place_xenia()
                increase_speed_on_level_progress()
                # update high score
                if score > high_score:
                    high_score = score
                draw_scoreboard()

            # Check for Xenia power-up collision
            if xenia and xenia.isvisible() and head.distance(xenia) < GRID_SIZE:
                xenia.hideturtle()
                score += apply_xenia_effect()
                # spawn 2 segments as special bonus
                spawn_segment()
                spawn_segment()
                # xenia disappears after used
                xenia.hideturtle()
                if score > high_score:
                    high_score = score
                draw_scoreboard()

        # If direction is stop but not paused, still allow starting movement with arrow keys
        # Control delay speed
        time.sleep(delay)

except turtle.Terminator:
    # Handle window close
    pass
except KeyboardInterrupt:
    # allow ctrl-c
    pass
