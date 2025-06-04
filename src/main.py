import tkinter as tk
import random
import time

class SnakeGame:
    def __init__(self, master):
        self.master = master

        # init ui
        self.master.title("Snake Game")
        self.top_frame = tk.Frame(master, height=40, bg="gray20")
        self.top_frame.pack(fill=tk.X)

        self.score_var = tk.StringVar()
        self.time_var = tk.StringVar()
        tk.Label(self.top_frame, textvariable=self.score_var, bg="gray20", fg="white", font=("Arial", 14)).pack(side=tk.LEFT, padx=20)
        tk.Label(self.top_frame, textvariable=self.time_var, bg="gray20", fg="white", font=("Arial", 14)).pack(side=tk.RIGHT, padx=20)

        self.canvas = tk.Canvas(master, width=400, height=400, bg="black")
        self.canvas.pack()

        # init game
        self.snake_size = 20
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.game_running = False
        self.start_time = None
        self.score = 0
        self.pending_growth = 0

        self.red_food_pos = None
        self.yellow_food_pos = None
        self.speed_up_food_pos = None
        self.speed_down_food_pos = None
        self.spawn_red_food()
        self.spawn_yellow_food()
        self.spawn_speed_up_food()
        self.spawn_speed_down_food()

        self.obstacle1_pos = None
        self.obstacle2_pos = None
        self.obstacle3_pos = None
        self.spawn_obstacles()

        # init render and update
        self.FPS_SET = 60
        self.UPS_SET = 60
        self.snake_speed = 20
        self.update_counter = 0
        self.last_update_time = 0
        self.last_render_time = 0
        self.last_increase_time = 0
        self.u_pool = 0
        self.r_pool = 0

        # Bind keys
        self.master.bind("<Up>", lambda e: self.change_direction("Up"))
        self.master.bind("<Down>", lambda e: self.change_direction("Down"))
        self.master.bind("<Left>", lambda e: self.change_direction("Left"))
        self.master.bind("<Right>", lambda e: self.change_direction("Right"))
        self.master.bind("<space>", lambda e: self.start_game())

        # Create start message
        self.canvas.create_text(200, 200, text="Press SPACE to start", fill="white", font=("Arial", 16))

    def start_game(self):
        if not self.game_running:
            # reset game state
            self.snake = [(100, 100), (80, 100), (60, 100)]
            self.direction = "Right"
            self.next_direction = "Right"
            self.score = 0
            self.snake_speed = 20
            self.pending_growth = 0
            self.spawn_red_food()
            self.spawn_yellow_food()
            self.spawn_speed_up_food()
            self.spawn_speed_down_food()
            self.spawn_obstacles()

            self.game_running = True
            self.start_time = time.time()
            self.last_update_time = time.time() * 1000
            self.last_render_time = time.time() * 1000
            self.game_loop()

    def game_loop(self):
        current_time = time.time() * 1000  # milliseconds

        # Update Game State
        update_interval = 1000 / self.UPS_SET
        if current_time - self.last_update_time >= update_interval:
            self.update_game()
            self.last_update_time = current_time

        # Render Game
        render_interval = 1000 / self.FPS_SET
        if current_time - self.last_render_time >= render_interval:
            self.render()
            self.last_render_time = current_time

        # Increase Speed every 5 secs
        if current_time - self.last_increase_time >= 5000:
            self.change_speed(-2)
            self.last_increase_time = current_time

        # next loop
        if self.game_running:
            self.master.after(1, self.game_loop)

    def update_game(self):
        self.update_counter += 1
        if self.update_counter >= self.snake_speed:
            self.update_snake()
            self.update_counter = 0

    def render(self):
        self.canvas.delete("all")
        if self.game_running:
            # Score and Time
            elapsed_time = int(time.time() - self.start_time)
            self.score_var.set(f"Score: {self.score}")
            self.time_var.set(f"Time: {elapsed_time}s")
            
            # Foods
            if self.red_food_pos:
                self.canvas.create_oval(
                    self.red_food_pos[0], self.red_food_pos[1],
                    self.red_food_pos[0] + self.snake_size,
                    self.red_food_pos[1] + self.snake_size,
                    fill="red"
                )
            if self.yellow_food_pos:
                self.canvas.create_oval(
                    self.yellow_food_pos[0], self.yellow_food_pos[1],
                    self.yellow_food_pos[0] + self.snake_size,
                    self.yellow_food_pos[1] + self.snake_size,
                    fill="yellow"
                )
            if self.speed_up_food_pos:
                self.canvas.create_oval(
                    self.speed_up_food_pos[0], self.speed_up_food_pos[1],
                    self.speed_up_food_pos[0] + self.snake_size,
                    self.speed_up_food_pos[1] + self.snake_size,
                    fill="pink"
                )
            if self.speed_down_food_pos:
                self.canvas.create_oval(
                    self.speed_down_food_pos[0], self.speed_down_food_pos[1],
                    self.speed_down_food_pos[0] + self.snake_size,
                    self.speed_down_food_pos[1] + self.snake_size,
                    fill="green"
                )
            # Obstacles
            if self.obstacle1_pos:
                self.canvas.create_rectangle(
                    self.obstacle1_pos[0], self.obstacle1_pos[1],
                    self.obstacle1_pos[0] + self.snake_size, self.obstacle1_pos[1] + self.snake_size,
                    fill="white"
                )
            if self.obstacle2_pos:
                self.canvas.create_rectangle(
                    self.obstacle2_pos[0], self.obstacle2_pos[1],
                    self.obstacle2_pos[0] + self.snake_size, self.obstacle2_pos[1] + self.snake_size,
                    fill="white"
                )
            if self.obstacle3_pos:
                self.canvas.create_rectangle(
                    self.obstacle3_pos[0], self.obstacle3_pos[1],
                    self.obstacle3_pos[0] + self.snake_size, self.obstacle3_pos[1] + self.snake_size,
                    fill="white"
                )

            # Snake
            for segment in self.snake:
                self.canvas.create_rectangle(
                    segment[0], segment[1],
                    segment[0] + self.snake_size, segment[1] + self.snake_size,
                    fill="green"
                )
        else:
            if self.start_time:
                elapsed_time = int(time.time() - self.start_time)
                self.canvas.create_text(
                    200, 200,
                    text=f"Game Over!\nScore: {self.score}\nTime: {elapsed_time}s\nPress SPACE to restart",
                    fill="white",
                    font=("Arial", 16),
                    justify="center"
                )
            else:
                self.canvas.create_text(200, 200, text="Press SPACE to start", fill="white", font=("Arial", 16))

    def change_speed(self, delta):
        self.snake_speed += delta
        if self.snake_speed < 6: # max speed
            self.snake_speed = 6
        if self.snake_speed > 30:
            self.snake_speed = 30 # minimum speed

    def spawn_obstacles(self):
        while True:
            pos = (random.randint(1, 19)*self.snake_size,
                   random.randint(1, 19)*self.snake_size)
            if pos != self.red_food_pos and pos != self.yellow_food_pos and pos != self.speed_up_food_pos and pos != self.speed_down_food_pos and pos not in self.snake:
                if pos != self.obstacle2_pos and pos != self.obstacle3_pos:
                    self.obstacle1_pos = pos
                    break
        while True:
            pos = (random.randint(1, 19)*self.snake_size,
                   random.randint(1, 19)*self.snake_size)
            if pos != self.red_food_pos and pos != self.yellow_food_pos and pos != self.speed_up_food_pos and pos != self.speed_down_food_pos and pos not in self.snake:
                if pos != self.obstacle1_pos and pos != self.obstacle3_pos:
                    self.obstacle2_pos = pos
                    break
        while True:
            pos = (random.randint(1, 19)*self.snake_size,
                   random.randint(1, 19)*self.snake_size)
            if pos != self.red_food_pos and pos != self.yellow_food_pos and pos != self.speed_up_food_pos and pos != self.speed_down_food_pos and pos not in self.snake:
                if pos != self.obstacle2_pos and pos != self.obstacle1_pos:
                    self.obstacle3_pos = pos
                    break

    def spawn_red_food(self):
        while True:
            pos = (random.randint(1, 19)*self.snake_size, 
                   random.randint(1, 19)*self.snake_size)
            if pos != self.yellow_food_pos and pos != self.speed_up_food_pos and pos != self.speed_down_food_pos and pos not in self.snake:
                self.red_food_pos = pos
                break

    def spawn_yellow_food(self):
        while True:
            pos = (random.randint(1, 19)*self.snake_size,
                   random.randint(1, 19)*self.snake_size)
            if pos != self.yellow_food_pos and pos != self.speed_up_food_pos and pos != self.speed_down_food_pos and pos not in self.snake:
                self.yellow_food_pos = pos
                break

    def spawn_speed_up_food(self):
        while True:
            pos = (random.randint(1, 19)*self.snake_size,
                   random.randint(1, 19)*self.snake_size)
            if pos != self.yellow_food_pos and pos != self.red_food_pos and pos != self.speed_down_food_pos and pos not in self.snake:
                self.speed_up_food_pos = pos
                break

    def spawn_speed_down_food(self):
        while True:
            pos = (random.randint(1, 19)*self.snake_size,
                   random.randint(1, 19)*self.snake_size)
            if pos != self.yellow_food_pos and pos != self.red_food_pos and pos != self.speed_up_food_pos and pos not in self.snake:
                self.speed_down_food_pos = pos
                break

    def change_direction(self, new_direction):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if opposites[new_direction] != self.direction:
            self.next_direction = new_direction

    def update_snake(self):
        head = self.snake[0]
        if self.next_direction == "Up":
            new_head = (head[0], head[1] - self.snake_size)
            self.direction = "Up"
        elif self.next_direction == "Down":
            new_head = (head[0], head[1] + self.snake_size)
            self.direction = "Down"
        elif self.next_direction == "Left":
            new_head = (head[0] - self.snake_size, head[1])
            self.direction = "Left"
        else:
            new_head = (head[0] + self.snake_size, head[1])
            self.direction = "Right"

        # Check collisions
        if (new_head[0] < 0 or new_head[0] >= 400 or
            new_head[1] < 0 or new_head[1] >= 400 or
            new_head in self.snake or
            new_head == self.obstacle1_pos or
            new_head == self.obstacle2_pos or
            new_head == self.obstacle3_pos
        ):
            self.game_over()
            return

        # Check foods
        if new_head == self.red_food_pos:
            self.score += 1
            self.pending_growth += 1
            self.spawn_red_food()
        if new_head == self.yellow_food_pos:
            self.score += 2
            self.pending_growth += 2
            self.spawn_yellow_food()
        if new_head == self.speed_up_food_pos:
            self.score += 1
            self.pending_growth += 1
            self.spawn_speed_up_food()
            self.change_speed(-2)
        if new_head == self.speed_down_food_pos:
            self.score += 1
            self.pending_growth += 1
            self.spawn_speed_down_food()
            self.change_speed(2)

        # Growth
        self.snake.insert(0, new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.snake.pop()

    def game_over(self):
        self.game_running = False
        elapsed_time = int(time.time() - self.start_time)

def main():
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()