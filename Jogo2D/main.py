import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Matemático - Fases")

# Cores e fontes
BG = (135, 206, 235)
PIPE_COLOR = (34, 139, 34)
BIRD_COLOR = (255, 215, 0)
TEXT_COLOR = (30, 30, 30)
FONT = pygame.font.SysFont(None, 36)
SMALL = pygame.font.SysFont(None, 24)

CLOCK = pygame.time.Clock()
FPS = 60

# Bird
bird_x = 80
bird_y = HEIGHT // 2
bird_vel = 0
GRAVITY = 0.50
FLAP_STRENGTH = -5.5
BIRD_R = 10

# Obstáculos
GAP_H = 160
OBST_W = 80
OBST_SPEED = 2.0
SPAWN_INTERVAL = 6000

score = 0
best = 0
game_over = False


# ---------- SISTEMA DE FASES ----------
def get_phase(score):
    cycle = (score // 2) % 3
    if cycle == 0:
        return "add"
    elif cycle == 1:
        return "sub"
    else:
        return "mul"


def generate_expression_by_phase(phase):
    if phase == "add":
        a, b = random.randint(1, 9), random.randint(1, 9)
        return f"{a} + {b}", a + b
    elif phase == "sub":
        a, b = random.randint(5, 20), random.randint(1, 9)
        return f"{a} - {b}", a - b
    else:
        a, b = random.randint(2, 9), random.randint(2, 9)
        return f"{a} × {b}", a * b


def make_wrong_answer(correct):
    delta = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    return correct + delta


class QuestionObstacle:
    def __init__(self):
        self.x = WIDTH
        self.expr = ""
        self.correct_answer = 0
        self.correct_is_top = True
        self.top_value = 0
        self.bottom_value = 0
        self.passed = False

        top_gap_center = random.randint(120, HEIGHT // 2 - 30)
        bottom_gap_center = top_gap_center + GAP_H + 80
        if bottom_gap_center > HEIGHT - 120:
            bottom_gap_center = HEIGHT - 120
            top_gap_center = bottom_gap_center - GAP_H - 80

        self.top_gap_y = top_gap_center - GAP_H // 2
        self.bottom_gap_y = bottom_gap_center - GAP_H // 2

        self.set_question(score)

    def set_question(self, current_score):
        phase = get_phase(current_score)
        self.expr, self.correct_answer = generate_expression_by_phase(phase)

        self.correct_is_top = random.choice([True, False])
        wrong = make_wrong_answer(self.correct_answer)

        self.top_value = self.correct_answer if self.correct_is_top else wrong
        self.bottom_value = wrong if self.correct_is_top else self.correct_answer

    def rects(self):
        rects = [
            pygame.Rect(self.x, 0, OBST_W, self.top_gap_y),
            pygame.Rect(
                self.x,
                self.top_gap_y + GAP_H,
                OBST_W,
                self.bottom_gap_y - (self.top_gap_y + GAP_H),
            ),
            pygame.Rect(
                self.x,
                self.bottom_gap_y + GAP_H,
                OBST_W,
                HEIGHT - (self.bottom_gap_y + GAP_H),
            ),
        ]
        return rects

    def update(self, dt):
        self.x -= OBST_SPEED * (dt / (1000 / FPS))

    def draw(self, surface):
        for r in self.rects():
            pygame.draw.rect(surface, PIPE_COLOR, r)

        cx = self.x + OBST_W // 2
        top_cy = self.top_gap_y + GAP_H // 2
        bot_cy = self.bottom_gap_y + GAP_H // 2

        pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(top_cy)), 26)
        pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(bot_cy)), 26)

        surface.blit(FONT.render(str(self.top_value), True, TEXT_COLOR),
                     FONT.render(str(self.top_value), True, TEXT_COLOR).get_rect(center=(cx, top_cy)))
        surface.blit(FONT.render(str(self.bottom_value), True, TEXT_COLOR),
                     FONT.render(str(self.bottom_value), True, TEXT_COLOR).get_rect(center=(cx, bot_cy)))


obstacles = []
last_spawn = pygame.time.get_ticks() - SPAWN_INTERVAL


def reset_game():
    global bird_y, bird_vel, score, obstacles, last_spawn, game_over
    bird_y = HEIGHT // 2
    bird_vel = 0
    score = 0
    obstacles = []
    last_spawn = pygame.time.get_ticks() - SPAWN_INTERVAL
    game_over = False


def draw_window():
    WIN.fill(BG)

    phase_name = {
        "add": "Adição",
        "sub": "Subtração",
        "mul": "Multiplicação"
    }[get_phase(score)]

    WIN.blit(FONT.render(f"Score: {score}", True, TEXT_COLOR), (10, 10))
    WIN.blit(SMALL.render(f"Fase: {phase_name}", True, TEXT_COLOR), (10, 45))

    if obstacles:
        expr = obstacles[0].expr
        text = FONT.render(expr, True, (0, 0, 0))
        rect = text.get_rect(center=(WIDTH // 2, 35))
        pygame.draw.rect(WIN, (255, 255, 255), rect.inflate(20, 10))
        pygame.draw.rect(WIN, (0, 0, 0), rect.inflate(20, 10), 2)
        WIN.blit(text, rect)

    pygame.draw.circle(WIN, BIRD_COLOR, (int(bird_x), int(bird_y)), BIRD_R)

    for obs in obstacles:
        obs.draw(WIN)

    if game_over:
        msg = FONT.render("Game Over! R para reiniciar", True, (200, 30, 30))
        WIN.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.update()


def check_collision(rect, obstacles):
    for obs in obstacles:
        for r in obs.rects():
            if rect.colliderect(r):
                return True
    return bird_y - BIRD_R <= 0 or bird_y + BIRD_R >= HEIGHT


while True:
    dt = CLOCK.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird_vel = FLAP_STRENGTH
            if event.key == pygame.K_r and game_over:
                reset_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            bird_vel = FLAP_STRENGTH if not game_over else reset_game()

    if not game_over:
        now = pygame.time.get_ticks()
        if now - last_spawn > SPAWN_INTERVAL:
            obstacles.append(QuestionObstacle())
            last_spawn = now

        bird_vel += GRAVITY
        bird_y += bird_vel

        for obs in obstacles:
            obs.update(dt)

        obstacles = [o for o in obstacles if o.x + OBST_W > -50]

        bird_rect = pygame.Rect(bird_x - BIRD_R, bird_y - BIRD_R, BIRD_R * 2, BIRD_R * 2)

        if check_collision(bird_rect, obstacles):
            game_over = True
            best = max(best, score)

        for obs in obstacles:
            center_x = obs.x + OBST_W // 2
            if not obs.passed and bird_x > center_x:
                in_top = obs.top_gap_y < bird_y < obs.top_gap_y + GAP_H
                in_bottom = obs.bottom_gap_y < bird_y < obs.bottom_gap_y + GAP_H
                correct = (in_top and obs.correct_is_top) or (in_bottom and not obs.correct_is_top)

                if correct:
                    score += 1
                else:
                    game_over = True
                    best = max(best, score)

                obs.passed = True

    draw_window()
