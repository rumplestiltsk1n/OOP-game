import math
import pygame
import time
import random
import os

pygame.font.init()
pygame.mixer.init()

WIDTH = 1920
HEIGHT = 1080

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake 🐍')
icon = pygame.image.load('images/snake_icon.ico')
pygame.display.set_icon(icon)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SCORE_COLOR = WHITE

playlist = ['sounds/jimmying a_bull.ogg',
            'sounds/satara_tribes.ogg',
            'sounds/we_are_from_Ukraine.ogg']

# Loop random music from the playlist
pygame.mixer.music.load(playlist[random.randrange(0, len(playlist))])
pygame.mixer.music.play(-1)

GAME_OVER_SOUND = pygame.mixer.Sound('sounds/ouch.ogg')

SCORE_FONT = pygame.font.SysFont('verdana', 20)
GAME_OVER_FONT = pygame.font.SysFont('verdana', 50)
TIPS_FONT = pygame.font.SysFont('verdana', 20)
HIGH_SCORE_FONT = pygame.font.SysFont('verdana', 20)

# Size of the snake blocks and fruits
SCALE = 20
SNAKE_SPEED = 20
high_score = 0


def new_fruit_pos(snake_body):
    fruit_position = [random.randrange(1, (WIDTH // SCALE)) * SCALE,
                      random.randrange(1, (HEIGHT // SCALE)) * SCALE]
    # Exclude appearance in snake body
    while snake_body.count(fruit_position) != 0:
        fruit_position = [random.randrange(1, (WIDTH // SCALE)) * SCALE,
                          random.randrange(1, (HEIGHT // SCALE)) * SCALE]
    return fruit_position


def draw_score(score):
    score_surface = SCORE_FONT.render('Score : ' + str(score), True, SCORE_COLOR)
    SCREEN.blit(score_surface, (10, 10))
    pygame.display.update()


def game_over(score, fruit_position):
    global high_score

    if score > high_score:
        high_score = score
        draw_high_score('NEW HIGH SCORE : ' + str(high_score) + ' !')

    # Remove apple
    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(
        fruit_position[0], fruit_position[1], SCALE, SCALE))

    # Creating a text surface on which text will be drawn
    surface = GAME_OVER_FONT.render('Score : ' + str(score), True, RED)

    # Creating a rectangular object for the text surface object
    rect = surface.get_rect()

    # Setting position of the text
    rect.midtop = (WIDTH / 2, HEIGHT / 4)

    # Draw the text on screen
    SCREEN.blit(surface, rect)
    pygame.display.flip()

    GAME_OVER_SOUND.play()
    time.sleep(1)

    main()


def draw_tips(text):
    draw = TIPS_FONT.render(text, True, WHITE)
    SCREEN.blit(draw, (WIDTH / 2 - draw.get_width() / 2,
                       HEIGHT - draw.get_height() - 10))
    pygame.display.update()
    pygame.time.delay(1000)


def draw_high_score(text):
    draw = HIGH_SCORE_FONT.render(text, True, WHITE)
    SCREEN.blit(draw, (WIDTH - draw.get_width() - 10, 10))
    pygame.display.update()


def main():
    snake_color = (random.randint(0, 255),
                   random.randint(0, 255),
                   random.randint(0, 255))
    fruit_color = (random.randint(0, 255),
                   random.randint(0, 255),
                   random.randint(0, 255))

    # Centered position of the head
    snake_position = [math.floor(WIDTH / (2 * SCALE)) * SCALE,
                      math.floor(HEIGHT / (2 * SCALE)) * SCALE]
    # Default body with 4 blocks
    snake_body = [list(snake_position),
                  [snake_position[0] - SCALE, snake_position[1]],
                  [snake_position[0] - SCALE * 2, snake_position[1]],
                  [snake_position[0] - SCALE * 3, snake_position[1]]
                  ]

    score = 0

    # Fruit position
    fruit_position = new_fruit_pos(snake_body)
    fruit_spawn = True

    direction = 'RIGHT'
    change_to = direction

    fps = pygame.time.Clock()
    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os._exit(1)

            if event.type == pygame.KEYDOWN:
                # Controls
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                if event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'

                if event.key == pygame.K_ESCAPE:
                    os._exit(1)
                # Background music
                if event.key == pygame.K_m:
                    if pygame.mixer.music.get_volume() == 1:
                        pygame.mixer.music.pause()
                        pygame.mixer.music.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(1)
                        pygame.mixer.music.unpause()

        # Snake can't move inside
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Moving the snake
        if direction == 'UP':
            snake_position[1] -= SCALE
        if direction == 'DOWN':
            snake_position[1] += SCALE
        if direction == 'LEFT':
            snake_position[0] -= SCALE
        if direction == 'RIGHT':
            snake_position[0] += SCALE

        # Snake body growing mechanism
        # if fruits and snakes collide then score will be incremented
        snake_body.insert(0, list(snake_position))
        if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
            score += 1
            fruit_spawn = False
        else:
            snake_body.pop()

        if not fruit_spawn:
            fruit_position = new_fruit_pos(snake_body)

        fruit_spawn = True
        SCREEN.fill(BLACK)

        # Drawing segments of snake's body
        for position in snake_body:
            pygame.draw.rect(SCREEN, snake_color, pygame.Rect(
                position[0], position[1], SCALE, SCALE))

        # Drawing a fruit
        pygame.draw.rect(SCREEN, fruit_color, pygame.Rect(
            fruit_position[0], fruit_position[1], SCALE, SCALE))

        # Game Over conditions
        # Ox
        if snake_position[0] < 0 or snake_position[0] > WIDTH - SCALE:
            game_over(score, fruit_position)
        # Oy
        if snake_position[1] < 0 or snake_position[1] > HEIGHT - SCALE:
            game_over(score, fruit_position)

        # Touching the snake body
        for block in snake_body[1:]:
            if snake_position[0] == block[0] and snake_position[1] == block[1]:
                game_over(score, fruit_position)

        # Displaying score continuously
        draw_score(score)

        # Refresh game screen
        pygame.display.update()

        # Frame per second (refresh rate)
        fps.tick(SNAKE_SPEED)


if __name__ == "__main__":
    draw_tips('[ M ] U T E')
    main()
