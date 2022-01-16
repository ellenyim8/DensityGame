import random
import sys
import pygame
import os
import time
import math

os.environ['SDL_VIDEO_CENTERED'] = '1'

WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (241, 238, 11)
RED = (240, 10, 10)
BLUE = (10, 50, 240)
PINK = (200, 10, 150)

SHIP_WIDTH = SHIP_HEIGHT = 20
WIDTH = 920
HEIGHT = 570
TOP_BUFFER = 38
PILL_WIDTH = 10
PILL_HEIGHT = 25

pygame.init()


class Text:
    def __init__(self, text, size, xpos, ypos, color):
        self.font = pygame.font.SysFont(text, size)
        self.image = self.font.render(str(text), 1, color)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(xpos - self.rect.width / 2, ypos - self.rect.height / 2)
        self.color = color


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, side):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 7
        self.density = SHIP_WIDTH * SHIP_HEIGHT
        self.image = pygame.Surface((math.sqrt(self.density), math.sqrt(self.density))).convert()
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.type = side

    def move_ship(self):
        key = pygame.key.get_pressed()
        # movements for left ship
        if self.type == 'left':
            if key[pygame.K_w]:
                self.rect.y -= self.speed
            elif key[pygame.K_s]:
                self.rect.y += self.speed
            elif key[pygame.K_a]:
                self.rect.x -= self.speed
            elif key[pygame.K_d]:
                self.rect.x += self.speed

            # boundaries
            if self.rect.right > WIDTH / 2:
                self.rect.right = WIDTH / 2
            elif self.rect.left < 0:
                self.rect.left = 0
            elif self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
            elif self.rect.top < TOP_BUFFER:
                self.rect.top = TOP_BUFFER

        elif self.type == 'right':
            # movements for right ship
            if key[pygame.K_UP]:
                self.rect.y -= self.speed
            elif key[pygame.K_DOWN]:
                self.rect.y += self.speed
            elif key[pygame.K_LEFT]:
                self.rect.x -= self.speed
            elif key[pygame.K_RIGHT]:
                self.rect.x += self.speed

            # boundaries
            if self.rect.left < WIDTH / 2:      # doesn't hit center
                self.rect.left = WIDTH / 2
            elif self.rect.right > WIDTH:       # doesn't hit right side
                self.rect.right = WIDTH
            elif self.rect.bottom > HEIGHT:     # doesn't hit bottom
                self.rect.bottom = HEIGHT
            elif self.rect.top < TOP_BUFFER:    # doesn't hit top
                self.rect.top = TOP_BUFFER

    def update(self, pill_group):
        self.move_ship()
        collision = pygame.sprite.spritecollide(self, pill_group, True)
        for p in collision:
            self.density += p.density * 5

        self.rect.width = self.rect.height = math.sqrt(self.density)
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


class Pill(pygame.sprite.Sprite):
    def __init__(self, pos, density):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 2
        self.density = density
        self.image = pygame.Surface((PILL_WIDTH, PILL_HEIGHT)).convert()
        self.image.fill(self.set_color())
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos, HEIGHT / 15)

    def set_color(self):
        if self.density == 1:
            return YELLOW
        elif self.density == 2:
            return BLUE
        elif self.density == 3:
            return RED
        elif self.density == 4:
            return BLACK

    def update(self):
        self.rect = self.rect.move((0, self.speed))
        if self.rect.y > HEIGHT:
            self.kill()


class Game:
    def __init__(self, play, intro, outro):
        self.play = play
        self.intro = intro
        self.outro = outro

    def update(self, left_density, right_density):
        if left_density.density >= 5000:
            left_density.density += 1000
            left_density.image = pygame.transform.scale(left_density.image, (left_density.rect.width, left_density.rect.height))
            if right_density.density > 20:
                right_density.density -= 20
                right_density.image = pygame.transform.scale(right_density.image, (right_density.rect.width, right_density.rect.height))

        elif right_density.density >= 5000:
            right_density.density += 1000
            right_density.image = pygame.transform.scale(right_density.image, (right_density.rect.width, right_density.rect.height))
            if left_density.density > 20:
                left_density.density -= 20
                left_density.image = pygame.transform.scale(left_density.image, (left_density.rect.width, left_density.rect.height))

        if left_density.density >= 10000:
            self.intro = False
            self.play = False
            self.outro = True

        if right_density.density >= 10000:
            self.intro = False
            self.play = False
            self.outro = True

def main():
    # Initialize local variables
    fps = 60
    timer = 0
    run = Game(True, True, False)

    pygame.display.set_caption("Density")
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    clock = pygame.time.Clock()

    # creates vertical and horizontal line across the screen
    vertical = pygame.Surface((1, HEIGHT)).convert()
    horizontal = pygame.Surface((WIDTH, 1)).convert()

    # create game objects
    left_ship = Ship(WIDTH / 4 - SHIP_WIDTH / 2, HEIGHT - (4 * SHIP_HEIGHT), 'left')
    right_ship = Ship((WIDTH / 1.5), HEIGHT - (4 * SHIP_HEIGHT), 'right')

    #intro text
    font = pygame.font.SysFont("Arial", 150)
    title = font.render("Density", 1, BLACK)
    title_rect = title.get_rect()
    title_rect = title_rect.move(WIDTH / 2 - title_rect.width / 2, HEIGHT / 2 - title_rect.height / 2)
    font1 = pygame.font.SysFont("Times New Roman", 100)
    sub_title = font1.render("-Click Here-", 2, BLACK)
    sub_title_rect = title.get_rect()
    sub_title_rect = title_rect.move(WIDTH / 2 - title_rect.width + TOP_BUFFER, HEIGHT / 2 - title_rect.height / 1.5)

    #score text
    left_score= Text(str(left_ship.density), 50, WIDTH/2 - 250, 0 + 20, BLACK)
    right_score = Text(str(right_ship.density), 50, WIDTH - 250, 0 + 20, BLACK)

    #win text
    left_wins = Text("Left Player Has Won.", 50, WIDTH/5, 0+20, BLACK)
    right_wins = Text("Right Player Has Won. ", 50, WIDTH/2 + TOP_BUFFER*5, 0+20, BLACK)

    #winner per round
    left_win = Text("Left Player Won! ", 100, WIDTH/2, HEIGHT/2, BLACK)
    right_win = Text("Right Player Won! ", 100, WIDTH/2, HEIGHT/2, BLACK)
    #replay
    ending = Text("--Click to Play Again--", 50, WIDTH/2, HEIGHT/2 + TOP_BUFFER*2, BLACK)

    # create groups
    ship_group = pygame.sprite.Group()
    ship_group.add(left_ship, right_ship)
    pill_group = pygame.sprite.Group()

    #intro
    while run.intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                run.intro = False

        screen.fill(WHITE)
        screen.blit(title, title_rect)

        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(sub_title, sub_title_rect)

        clock.tick(60)
        pygame.display.flip()

    # game loop
    while run.play:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # update groups
        run.update(left_ship, right_ship)
        ship_group.update(pill_group)
        pill_group.update()

        if timer % 10 == 0:
            pill = Pill(random.randrange(0, WIDTH - PILL_WIDTH),
                        int(random.choice("1111111111111111222334")))
            pill2 = Pill(random.randrange(0, WIDTH + PILL_WIDTH),
                         int(random.choice("111111111111111222334")))
            pill_group.add(pill)
            pill_group.add(pill2)

        # blit groups
        screen.fill(WHITE)
        screen.blit(vertical, (WIDTH / 2, HEIGHT / 15))
        screen.blit(horizontal, (0, HEIGHT / 15))
        screen.blit(left_ship.image, left_ship.rect)
        screen.blit(right_ship.image, right_ship.rect)

        # draw groups
        ship_group.draw(screen)
        pill_group.draw(screen)

        left_score.image = left_score.font.render("DENSITY: " + str(left_ship.density), 1, BLACK)
        right_score.image = right_score.font.render("DENSITY: " + str(right_ship.density), 1, BLACK)

        # left_wins.image = left_wins.font.render("WINS: 0", 1, BLACK)
        # right_wins.image = right_wins.font.render("WINS: 0", 1, BLACK)

        screen.blit(left_score.image, left_score.rect)
        screen.blit(right_score.image, right_score.rect)

        # need to add wins score for each side
        screen.blit(left_wins.image, left_wins.rect)
        screen.blit(right_wins.image, right_wins.rect)

        timer += 1
        clock.tick(fps)
        pygame.display.flip()

    while run.outro:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                screen.blit(ending.image, ending.rect)
                pygame.display.flip()
                pygame.time.wait(100)
                main()

        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(ending.image, ending.rect)

        if left_ship.density > right_ship.density:
            screen.blit(left_win.image, left_win.rect)
        else:
            screen.blit(right_win.image, right_win.rect)

        clock.tick(60)
        pygame.display.flip()


if __name__ == "__main__":
    main()
