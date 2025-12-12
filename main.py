import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Matemático - Rápido")

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
GAP_H = 160       # mais espaço vertical
OBST_W = 80
OBST_SPEED = 2.0  # um pouco mais rápido para reduzir "demora"

# Canos mais espaçados horizontalmente (intervalo menor para aparecer mais cedo)
SPAWN_INTERVAL = 6000

score = 0
best = 0
game_over = False


class QuestionObstacle:
    def __init__(self):
        self.x = WIDTH
        self.expr = ""
        self.correct_answer = 0
        self.correct_is_top = True
        self.top_value = 0
        self.bottom_value = 0
        self.passed = False

        # Posição dos gaps
        top_gap_center = random.randint(120, HEIGHT // 2 - 30)
        bottom_gap_center = top_gap_center + GAP_H + 80
        if bottom_gap_center > HEIGHT - 120:
            bottom_gap_center = HEIGHT - 120
            top_gap_center = bottom_gap_center - GAP_H - 80

        self.top_gap_y = top_gap_center - GAP_H // 2
        self.bottom_gap_y = bottom_gap_center - GAP_H // 2

        # Inicializa pergunta
        self.set_question(score)

    def set_question(self, current_score):
        # Gera expressão e posiciona resposta correta no topo ou embaixo
        self.expr, self.correct_answer = generate_expression(current_score)
        self.correct_is_top = random.choice([True, False])
        wrong = make_wrong_answer(self.correct_answer)

        self.top_value = self.correct_answer if self.correct_is_top else wrong
        self.bottom_value = wrong if self.correct_is_top else self.correct_answer

    def rects(self):
        rects = []
        rects.append(pygame.Rect(self.x, 0, OBST_W, self.top_gap_y))

        middle_top = self.top_gap_y + GAP_H
        middle_h = max(0, self.bottom_gap_y - middle_top)
        if middle_h > 0:
            rects.append(pygame.Rect(self.x, middle_top, OBST_W, middle_h))

        bottom_top = self.bottom_gap_y + GAP_H
        if bottom_top < HEIGHT:
            rects.append(pygame.Rect(self.x, bottom_top, OBST_W, HEIGHT - bottom_top))

        return rects

    def update(self, dt):
        self.x -= OBST_SPEED * (dt / (1000 / FPS))

    def draw(self, surface):
        for r in self.rects():
            pygame.draw.rect(surface, PIPE_COLOR, r)

        cx = self.x + OBST_W // 2
        top_cy = self.top_gap_y + GAP_H // 2
        bot_cy = self.bottom_gap_y + GAP_H // 2

        pygame.draw.circle(surface, (255,255,255), (int(cx), int(top_cy)), 26)
        pygame.draw.circle(surface, (255,255,255), (int(cx), int(bot_cy)), 26)

        top_text = FONT.render(str(self.top_value), True, TEXT_COLOR)
        bot_text = FONT.render(str(self.bottom_value), True, TEXT_COLOR)
        surface.blit(top_text, top_text.get_rect(center=(cx, top_cy)))
        surface.blit(bot_text, bot_text.get_rect(center=(cx, bot_cy)))


def generate_expression(score):
    if score < 5:
        a, b = random.randint(1, 9), random.randint(1, 9)
        return f"{a} + {b}", a + b
    elif score < 10:
        a, b = random.randint(5, 20), random.randint(1, 9)
        return f"{a} - {b}", a - b
    else:
        a, b = random.randint(2, 9), random.randint(2, 9)
        return f"{a} × {b}", a * b


def make_wrong_answer(correct):
    # Gera um errado próximo, mas nunca igual ao correto
    delta = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    wrong = correct + delta
    # Evita casos triviais iguais (por segurança adicional)
    if wrong == correct:
        wrong += 2
    return wrong


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
    WIN.blit(FONT.render(f"Score: {score}", True, TEXT_COLOR), (10, 10))
    WIN.blit(SMALL.render(f"Best: {best}", True, TEXT_COLOR), (10, 45))

    # Quadradinho da conta (mostra a conta do próximo obstáculo a ser enfrentado)
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
        WIN.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))

    pygame.display.update()


def check_collision(rect, obstacles):
    for obs in obstacles:
        for r in obs.rects():
            if rect.colliderect(r):
                return True
    if bird_y - BIRD_R <= 0 or bird_y + BIRD_R >= HEIGHT:
        return True
    return False


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
            if not game_over:
                bird_vel = FLAP_STRENGTH
            else:
                reset_game()

    if not game_over:
        now = pygame.time.get_ticks()
        if now - last_spawn > SPAWN_INTERVAL:
            obstacles.append(QuestionObstacle())
            last_spawn = now

        bird_vel += GRAVITY
        bird_y += bird_vel

        for obs in obstacles:
            obs.update(dt)

        # Remover obstáculos fora da tela
        old_len = len(obstacles)
        obstacles = [o for o in obstacles if o.x + OBST_W > -50]

        # Se algum obstáculo saiu da tela e ainda há obstáculo na lista,
        # garanta que o próximo já tenha uma nova pergunta (sincronizado).
        if old_len > len(obstacles) and obstacles:
            obstacles[0].set_question(score)

        bird_rect = pygame.Rect(bird_x - BIRD_R, bird_y - BIRD_R, BIRD_R*2, BIRD_R*2)

        if check_collision(bird_rect, obstacles):
            game_over = True
            best = max(best, score)

        # Lógica de passagem e acerto/erro
        for i, obs in enumerate(obstacles):
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

                # Assim que o jogador passa do cano atual,
                # atualize a próxima pergunta para aparecer mais rápido no HUD.
                if i + 1 < len(obstacles):
                    obstacles[i + 1].set_question(score)
                # Se não houver próximo ainda, forçamos um spawn antecipado
                # para o HUD não "demorar" a mostrar a próxima conta.
                else:
                    # Spawn antecipado se der (evita floodar)
                    if now - last_spawn > SPAWN_INTERVAL // 2:
                        obstacles.append(QuestionObstacle())
                        last_spawn = pygame.time.get_ticks()

    draw_window()
