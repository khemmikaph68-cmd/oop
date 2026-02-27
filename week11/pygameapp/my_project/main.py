import sys
import pygame
import random
import heapq
import time

# --- Settings ---
TILE_SIZE = 30
MAZE_WIDTH = 25   # ควรเป็นเลขคี่
MAZE_HEIGHT = 21  # ควรเป็นเลขคี่
SCREEN_WIDTH = MAZE_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAZE_HEIGHT * TILE_SIZE

# --- Colors ---
COLOR_WALL = (40, 40, 40)       # ผนังเขาวงกต (เทาเข้ม)
COLOR_PATH = (220, 220, 220)    # พื้นทางเดิน (ขาวหม่น)
COLOR_PLAYER = (0, 150, 255)    # ผู้เล่น (ฟ้า)
COLOR_ENEMY = (255, 0, 0)       # ปีศาจ (แดง)
COLOR_TROPHY = (255, 215, 0)    # ถ้วยรางวัล (ทอง)
COLOR_SKILL = (0, 255, 255)     # สกิลเวทมนตร์ (ฟ้าอ่อน)
COLOR_TEXT = (255, 255, 255)
COLOR_BG = (0, 0, 0)

# --- Directions ---
DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)] # บน, ล่าง, ซ้าย, ขวา

class MazeGenerator:
    """สร้างเขาวงกตด้วยวิธี Recursive Backtracker + เจาะรูเพื่มเพื่อลบล้างทางตัน (Braid Maze)"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self._generate()
        self._remove_dead_ends()

    def _generate(self):
        stack = [(1, 1)]
        self.grid[1][1] = 0

        while stack:
            cx, cy = stack[-1]
            neighbors = []

            for dx, dy in DIRS:
                nx, ny = cx + dx * 2, cy + dy * 2
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if self.grid[ny][nx] == 1:
                        neighbors.append((nx, ny, dx, dy))

            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                self.grid[cy + dy][cx + dx] = 0
                self.grid[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

    def _remove_dead_ends(self):
        """เจาะกำแพงบางส่วนออกเพื่อเชื่อมทาง (ให้มีทางหนีเพิ่มขึ้น ไม่ตันตลอด)"""
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 0:
                    walls_around = 0
                    possible_drill = []

                    for dx, dy in DIRS:
                        if self.grid[y + dy][x + dx] == 1:
                            walls_around += 1
                            # เช็คว่าถ้าทุบกำแพงนี้ ทะลุไปเจอทางเดินอีกฝั่งหรือไม่
                            if 0 < x + dx * 2 < self.width - 1 and 0 < y + dy * 2 < self.height - 1:
                                if self.grid[y + dy * 2][x + dx * 2] == 0:
                                    possible_drill.append((dx, dy))

                    # ถ้าช่องนี้เป็นทางตัน (มีกำแพงล้อม 3 ด้าน) ให้เจาะสุ่มเพื่อเชื่อมทาง
                    if walls_around >= 3 and possible_drill:
                        if random.random() < 0.6:  # โอกาส 60% ที่จะเจาะให้ทางเชื่อมกัน
                            dx, dy = random.choice(possible_drill)
                            self.grid[y + dy][x + dx] = 0

    def is_wall(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.grid[y][x] == 1

class AStarEnemy:
    def __init__(self, x, y, maze):
        self.x = x
        self.y = y
        self.maze = maze
        self.path = []
        
        # สถานะความเร็ว
        self.base_delay = 0.25 # วินาที (วิ่งเร็วกว่าคนปกติหน่อย)
        self.current_delay = self.base_delay
        
        # สถานะโดน Slow
        self.slow_timer = 0.0
        self.is_slowed = False

        self.timer = 0.0

    def apply_slow(self, duration_sec):
        self.is_slowed = True
        self.slow_timer = duration_sec
        self.current_delay = 0.7 # สโลว์ให้เดินช้าลงมากๆ (0.7 วิ ต่อก้าว)

    def draw(self, surface):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, COLOR_ENEMY, rect)
        
        # วาดหน้าตาดุร้าย (ถ้าโดน slow จะทำหน้าเอ๋อๆ สีสว่างขึ้น)
        eye_color = COLOR_SKILL if self.is_slowed else COLOR_BG
        pygame.draw.circle(surface, eye_color, (self.x * TILE_SIZE + 8, self.y * TILE_SIZE + 10), 3)
        pygame.draw.circle(surface, eye_color, (self.x * TILE_SIZE + 22, self.y * TILE_SIZE + 10), 3)
        pygame.draw.line(surface, eye_color, (self.x * TILE_SIZE + 10, self.y * TILE_SIZE + 22), (self.x * TILE_SIZE + 20, self.y * TILE_SIZE + 22), 3)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, target_x, target_y):
        start = (self.x, self.y)
        goal = (target_x, target_y)

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for dx, dy in DIRS:
                next_node = (current[0] + dx, current[1] + dy)
                if self.maze.is_wall(next_node[0], next_node[1]):
                    continue
                    
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(goal, next_node)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        current = goal
        path = []
        if current not in came_from:
            return [] 

        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def update(self, dt, target_x, target_y):
        # อัปเดตสถานะการ Slow
        if self.is_slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.is_slowed = False
                self.current_delay = self.base_delay

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.current_delay
            self.path = self.find_path(target_x, target_y)
            if self.path:
                next_step = self.path[0]
                self.x, self.y = next_step

class MagicProjectile:
    """กระสุนสกิลเวทมนตร์ ปาเพื่อ Slow ปีศาจ"""
    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = float(start_x * TILE_SIZE + TILE_SIZE // 2)
        self.y = float(start_y * TILE_SIZE + TILE_SIZE // 2)
        
        # คำนวณเวกเตอร์ความเร็ว
        dx = (target_x * TILE_SIZE + TILE_SIZE // 2) - self.x
        dy = (target_y * TILE_SIZE + TILE_SIZE // 2) - self.y
        length = (dx**2 + dy**2)**0.5
        
        if length > 0:
            self.vx = (dx / length) * 600.0 # ความเร็วกระสุน
            self.vy = (dy / length) * 600.0
        else:
            self.vx, self.vy = 0, 0
            
        self.radius = 8
        self.active = True

    def update(self, dt, maze):
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # เช็คชนกำแพง
        grid_x = int(self.x // TILE_SIZE)
        grid_y = int(self.y // TILE_SIZE)
        if maze.is_wall(grid_x, grid_y):
            self.active = False
            
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, COLOR_SKILL, (int(self.x), int(self.y)), self.radius)

class MazeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze of Terror - Escape!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Tahoma', 36)
        self.small_font = pygame.font.SysFont('Tahoma', 20)

        self.reset_game()
        self.running = True

    def reset_game(self):
        self.maze = MazeGenerator(MAZE_WIDTH, MAZE_HEIGHT)
        self.player_x = 1
        self.player_y = 1
        
        self.trophy_x = MAZE_WIDTH - 2
        self.trophy_y = MAZE_HEIGHT - 2
        self.maze.grid[self.trophy_y][self.trophy_x] = 0
        self.maze.grid[self.trophy_y-1][self.trophy_x] = 0
        self.maze.grid[self.trophy_y][self.trophy_x-1] = 0

        ex, ey = MAZE_WIDTH // 2, MAZE_HEIGHT // 2
        while self.maze.is_wall(ex, ey) or (ex <= 8 and ey <= 8):
            ex = random.randint(MAZE_WIDTH // 2, MAZE_WIDTH - 2)
            ey = random.randint(MAZE_HEIGHT // 2, MAZE_HEIGHT - 2)
            
        self.enemy = AStarEnemy(ex, ey, self.maze)

        self.projectiles = []
        
        # ระบบคูลดาวน์สกิล (คลิกเมาส์เพื่อปา)
        self.skill_cooldown = 5.0 # สกิลใช้งานได้ทุกๆ 5 วินาที
        self.current_cooldown = 0.0

        self.state = "PLAYING"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == "PLAYING":
                    dx, dy = 0, 0
                    if event.key in (pygame.K_LEFT, pygame.K_a): dx = -1
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): dx = 1
                    elif event.key in (pygame.K_UP, pygame.K_w): dy = -1
                    elif event.key in (pygame.K_DOWN, pygame.K_s): dy = 1

                    nx = self.player_x + dx
                    ny = self.player_y + dy
                    
                    if not self.maze.is_wall(nx, ny):
                        self.player_x, self.player_y = nx, ny
                        
                elif self.state in ["WIN", "LOSE"]:
                    if event.key == pygame.K_r:
                        self.reset_game()
            
            # ยิงสกิลใส่ปีศาจด้วยเมาส์
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "PLAYING" and event.button == 1: # คลิกซ้าย
                    if self.current_cooldown <= 0:
                        mx, my = pygame.mouse.get_pos()
                        target_grid_x = mx // TILE_SIZE
                        target_grid_y = my // TILE_SIZE
                        
                        self.projectiles.append(MagicProjectile(self.player_x, self.player_y, target_grid_x, target_grid_y))
                        self.current_cooldown = self.skill_cooldown # รีเซ็ตคูลดาวน์

    def update_logic(self, dt):
        if self.state == "PLAYING":
            # ลดคูลดาวน์สกิล
            if self.current_cooldown > 0:
                self.current_cooldown -= dt

            self.enemy.update(dt, self.player_x, self.player_y)

            # อัปเดตกระสุนและเช็คชน
            enemy_rect = pygame.Rect(self.enemy.x * TILE_SIZE, self.enemy.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            for p in self.projectiles:
                p.update(dt, self.maze)
                if p.active and p.get_rect().colliderect(enemy_rect):
                    p.active = False
                    self.enemy.apply_slow(4.0) # ทำให้ปีศาจช้าลง 4 วินาที

            self.projectiles = [p for p in self.projectiles if p.active]

            # เช็คชนะ
            if self.player_x == self.trophy_x and self.player_y == self.trophy_y:
                self.state = "WIN"
            
            # เช็คแพ้
            if self.player_x == self.enemy.x and self.player_y == self.enemy.y:
                self.state = "LOSE"

    def draw_maze(self):
        self.screen.fill(COLOR_WALL)
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if self.maze.grid[y][x] == 0:
                    rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, COLOR_PATH, rect)

    def draw_entities(self):
        center = (self.trophy_x * TILE_SIZE + TILE_SIZE//2, self.trophy_y * TILE_SIZE + TILE_SIZE//2)
        pygame.draw.circle(self.screen, COLOR_TROPHY, center, TILE_SIZE//3)
        
        p_rect = (self.player_x * TILE_SIZE, self.player_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, COLOR_PLAYER, p_rect)
        pygame.draw.circle(self.screen, COLOR_BG, (self.player_x * TILE_SIZE + 10, self.player_y * TILE_SIZE + 10), 3)
        pygame.draw.circle(self.screen, COLOR_BG, (self.player_x * TILE_SIZE + 20, self.player_y * TILE_SIZE + 10), 3)

        self.enemy.draw(self.screen)

        for p in self.projectiles:
            p.draw(self.screen)

    def draw_ui(self):
        # หลอด Cooldown Skill
        cd_ratio = max(0, 1 - (self.current_cooldown / self.skill_cooldown))
        pygame.draw.rect(self.screen, (100, 100, 100), (10, 10, 150, 15))
        pygame.draw.rect(self.screen, COLOR_SKILL, (10, 10, int(150 * cd_ratio), 15))
        
        text = self.small_font.render("Skill", True, COLOR_TEXT)
        self.screen.blit(text, (10, 30))

        if self.state != "PLAYING":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(COLOR_BG)
            self.screen.blit(overlay, (0, 0))

            if self.state == "WIN":
                msg = "YOU ESCAPED! (วิน!)"
                color = COLOR_TROPHY
            else:
                msg = "WASTED! (โดนจับได้!)"
                color = COLOR_ENEMY

            text = self.font.render(msg, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(text, rect)

            btn = self.small_font.render("Press 'R' to play again", True, COLOR_TEXT)
            b_rect = btn.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            self.screen.blit(btn, b_rect)

    def start(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update_logic(dt)

            self.draw_maze()
            self.draw_entities()
            self.draw_ui()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MazeGame()
    game.start()