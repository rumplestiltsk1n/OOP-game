import math
import sys
import pygame
import time
import random

pygame.font.init()
pygame.mixer.init()

# Full HD
WIDTH = 1920
HEIGHT = 1080

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake 🐍')
icon = pygame.image.load('images/snake_icon.ico')
pygame.display.set_icon(icon)

# Color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

BACKGROUND_COLOR = BLACK
TIPS_FONT_COLOR = WHITE
PAUSE_COLOR = WHITE

SCORE_COLOR = WHITE
HIGH_SCORE_FONT_COLOR = WHITE

GAME_OVER_FONT_COLOR = RED
YOU_WIN_FONT_COLOR = GREEN

# Music
playlist = [
    'music/jimmying a_bull.ogg',
    'music/satara_tribes.ogg',
    'music/we_are_from_Ukraine.ogg',
    'music/Elden Ring.ogg',
    'music/Final Reckoning.ogg',
    'music/Hallmore Sentinel.ogg',
    'music/Legend.ogg',
    'music/No Tomorrow.ogg',
    'music/Rave.ogg',
    'music/Rush E.ogg',
]

# Loop random music from the playlist
pygame.mixer.music.load(playlist[random.randrange(0, len(playlist))])
pygame.mixer.music.play(-1)

GAME_OVER_SOUND = pygame.mixer.Sound('music/ouch.ogg')

# Size of the snake blocks and fruits
SCALE = 30

# max number of segments without starting 4
MAX_SCORE = WIDTH // SCALE * HEIGHT // SCALE - 4

# Radius of rounded corners
SEGMENT_CURVE = 25

SNAKE_SPEED = 10
high_score = 0

# Fonts
TIPS_FONT = pygame.font.SysFont('verdana', 20)  # 20
SCORE_FONT = pygame.font.SysFont('verdana', 20)
HIGH_SCORE_FONT = pygame.font.SysFont('verdana', 20)
GAME_OVER_FONT = pygame.font.SysFont('times new roman', 50, True)
YOU_WIN_FONT = pygame.font.SysFont('times new roman', 100, True)


def you_win():
    # Creating a text surface on which text will be drawn
    surface = YOU_WIN_FONT.render('You WIN!', True, YOU_WIN_FONT_COLOR)

    # Creating a rectangular object for the text surface object
    rect = surface.get_rect()

    # Setting position of the text
    rect.midtop = (WIDTH / 2, HEIGHT / 4)

    # Draw the text on screen
    SCREEN.blit(surface, rect)
    pygame.display.flip()
    pygame.display.update()

    time.sleep(1)

    main()


def new_fruit_pos(snake_body):
    # if len(snake_body) == MAX_SCORE:
    #     you_win()

    fruit_position = [random.randrange(0, (WIDTH // SCALE)) * SCALE,
                      random.randrange(0, (HEIGHT // SCALE)) * SCALE]
    # Exclude appearance in snake body
    while snake_body.count(fruit_position) != 0:
        fruit_position = [random.randrange(0, (WIDTH // SCALE)) * SCALE,
                          random.randrange(0, (HEIGHT // SCALE)) * SCALE]
    return fruit_position


def draw_tips(text):
    draw = TIPS_FONT.render(text, True, TIPS_FONT_COLOR)
    SCREEN.blit(draw, (WIDTH / 2 - draw.get_width() / 2,
                       HEIGHT - draw.get_height() - 10))
    pygame.display.update()
    pygame.time.delay(1000)


def draw_score(score):
    score_surface = SCORE_FONT.render('Score : ' + str(score), True, SCORE_COLOR)
    SCREEN.blit(score_surface, (10, 10))
    pygame.display.update()


def draw_high_score(text):
    draw = HIGH_SCORE_FONT.render(text, True, HIGH_SCORE_FONT_COLOR)
    SCREEN.blit(draw, (WIDTH - draw.get_width() - 10, 10))
    pygame.display.update()


def pause():
    is_music_muted = pygame.mixer.music.get_volume() == 0

    # Stop background music
    pygame.mixer.music.pause()
    pygame.mixer.music.set_volume(0)

    draw_pause()

    paused = True

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = False
                    # continue music if it was not muted
                    if not is_music_muted:
                        pygame.mixer.music.set_volume(1)
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def draw_pause():
    pause_rect_width = 50
    pause_rect_height = 200
    distance_between_rects = 100

    s = pygame.Surface((WIDTH, HEIGHT))  # the size of rectangle
    s.set_alpha(50)  # alpha level
    s.fill((150, 150, 150))  # fills the entire surface
    SCREEN.blit(s, (0, 0))  # (0,0) are the top-left coordinates

    pygame.draw.rect(SCREEN, PAUSE_COLOR, pygame.Rect(
        math.floor(WIDTH / 2) - math.floor(distance_between_rects / 2) - pause_rect_width,
        math.floor(HEIGHT / 2) - math.floor(pause_rect_height / 2),
        pause_rect_width, pause_rect_height), 5, 10)  # border width, border radius

    pygame.draw.rect(SCREEN, PAUSE_COLOR, pygame.Rect(
        math.floor(WIDTH / 2) + math.floor(distance_between_rects / 2),
        math.floor(HEIGHT / 2) - math.floor(pause_rect_height / 2),
        pause_rect_width, pause_rect_height), 5, 10)  # border width, border radius

    # Refresh game screen
    pygame.display.update()


def curved_corner_begin_end(segment1, segment2, corner):
    if corner == "top-left":
        if segment1[0] == segment2[0] - SCALE or segment1[1] == segment2[1] - SCALE:
            return SEGMENT_CURVE
        else:
            return 0

    if corner == "top-right":
        if segment1[0] == segment2[0] + SCALE or segment1[1] == segment2[1] - SCALE:
            return SEGMENT_CURVE
        else:
            return 0

    if corner == "bottom-left":
        if segment1[0] == segment2[0] - SCALE or segment1[1] == segment2[1] + SCALE:
            return SEGMENT_CURVE
        else:
            return 0

    if corner == "bottom-right":
        if segment1[0] == segment2[0] + SCALE or segment1[1] == segment2[1] + SCALE:
            return SEGMENT_CURVE
        else:
            return 0


def curved_corner_middle(previous, current, next, snake_color):
    if previous[0] == current[0] == next[0] or previous[1] == current[1] == next[1]:
        pygame.draw.rect(SCREEN, snake_color, pygame.Rect(current[0], current[1], SCALE, SCALE))
        return

    # top-left curve
    if (previous[0] == current[0] + SCALE and next[1] == current[1] + SCALE
            or next[0] == current[0] + SCALE and previous[1] == current[1] + SCALE):
        pygame.draw.rect(SCREEN, snake_color, pygame.Rect(current[0], current[1], SCALE, SCALE),
                         0, 0,  # border width, border radius
                         SEGMENT_CURVE)  # top-left

    # top-right curve
    if (previous[0] == current[0] - SCALE and next[1] == current[1] + SCALE
            or next[0] == current[0] - SCALE and previous[1] == current[1] + SCALE):
        pygame.draw.rect(SCREEN, snake_color, pygame.Rect(current[0], current[1], SCALE, SCALE),
                         0, 0,  # border width, border radius
                         0, SEGMENT_CURVE)  # top-left, top-right

    # bottom-left curve
    if (previous[0] == current[0] + SCALE and next[1] == current[1] - SCALE
            or next[0] == current[0] + SCALE and previous[1] == current[1] - SCALE):
        pygame.draw.rect(SCREEN, snake_color, pygame.Rect(current[0], current[1], SCALE, SCALE),
                         0, 0,  # border width, border radius
                         0, 0, SEGMENT_CURVE)  # top-left, top-right, bottom-left

    # bottom-right curve
    if (previous[0] == current[0] - SCALE and next[1] == current[1] - SCALE
            or next[0] == current[0] - SCALE and previous[1] == current[1] - SCALE):
        pygame.draw.rect(SCREEN, snake_color, pygame.Rect(current[0], current[1], SCALE, SCALE),
                         0, 0,  # border width, border radius
                         0, 0, 0, SEGMENT_CURVE)  # top-left, top-right, bottom-left, bottom-right


def game_over(score, fruit_position):
    global high_score

    if score > high_score:
        high_score = score
        draw_high_score('NEW HIGH SCORE : ' + str(high_score) + ' !')

    # Remove apple
    pygame.draw.rect(SCREEN, BACKGROUND_COLOR, pygame.Rect(
        fruit_position[0], fruit_position[1], SCALE, SCALE))

    # Creating a text surface on which text will be drawn
    surface = GAME_OVER_FONT.render('Score : ' + str(score), True, GAME_OVER_FONT_COLOR)

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


def main():
    snake_color = (random.randint(20, 255),
                   random.randint(20, 255),
                   random.randint(20, 255))

    fruit_color = (random.randint(20, 255),
                   random.randint(20, 255),
                   random.randint(20, 255))

    x = random.randint(20, 255)
    eyes_color = (x, x, x)  # shades of grey
    del x

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
                pygame.quit()
                sys.exit()

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

                if event.key == pygame.K_SPACE:
                    pause()

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

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

        # Snake body growth
        # if fruit and snake collide then score will be incremented
        snake_body.insert(0, list(snake_position))
        if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
            score += 1
            fruit_spawn = False
        else:
            snake_body.pop()

        if not fruit_spawn and score != MAX_SCORE:
            fruit_position = new_fruit_pos(snake_body)

        fruit_spawn = True
        SCREEN.fill(BACKGROUND_COLOR)

        # Drawing segments of snake's body
        # first segment
        position = snake_body[0]
        pygame.draw.rect(SCREEN, snake_color, pygame.Rect(
            position[0], position[1], SCALE, SCALE), 0, 0,
                         curved_corner_begin_end(snake_body[0], snake_body[1], "top-left"),
                         curved_corner_begin_end(snake_body[0], snake_body[1], "top-right"),
                         curved_corner_begin_end(snake_body[0], snake_body[1], "bottom-left"),
                         curved_corner_begin_end(snake_body[0], snake_body[1], "bottom-right"))
        # Eyes
        pygame.draw.circle(SCREEN, eyes_color,
                           [position[0] + SCALE // 4, position[1] + SCALE // 2],  # center
                           SCALE // 8  # radius
                           )

        pygame.draw.circle(SCREEN, eyes_color,
                           [position[0] + SCALE // 4 * 3, position[1] + SCALE // 2],  # center
                           SCALE // 8  # radius
                           )

        # middle segments
        for i in range(1, len(snake_body) - 1):
            curved_corner_middle(snake_body[i - 1], snake_body[i], snake_body[i + 1], snake_color)

        # last segment
        position = snake_body[-1]
        pygame.draw.rect(SCREEN, snake_color, pygame.Rect(
            position[0], position[1], SCALE, SCALE), 0, 0,
                         curved_corner_begin_end(snake_body[-1], snake_body[-2], "top-left"),
                         curved_corner_begin_end(snake_body[-1], snake_body[-2], "top-right"),
                         curved_corner_begin_end(snake_body[-1], snake_body[-2], "bottom-left"),
                         curved_corner_begin_end(snake_body[-1], snake_body[-2], "bottom-right"))

        # win condition after displaying all snake segments
        if score == MAX_SCORE:
            you_win()

        # Drawing a fruit
        pygame.draw.rect(SCREEN, fruit_color, pygame.Rect(
            fruit_position[0], fruit_position[1], SCALE, SCALE), 0, SEGMENT_CURVE)

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
    draw_tips('[ M ] U T E    [ space ] P A U S E')
    main()
