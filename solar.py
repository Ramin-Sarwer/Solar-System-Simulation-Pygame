# Ramin Sarwer (100826924)
import pygame
import sys
import os
import numpy as np
from scipy.integrate import ode

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (255, 0, 0)
GREY = (80, 78, 81)

# Set the window dimensions
WIDTH, HEIGHT = 1000, 1000

# Initialize pygame window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulation")
clock = pygame.time.Clock()

class HeavenlyBody(pygame.sprite.Sprite):
    AU = 149.6e6 * 1000 # astronomical unit
    G = 6.674e-11 # constant of Gravity
    SCALE = 250 / AU # scale factor
    dt = 1000 # time step

    def __init__(self, name, radius, mass, distance_from_parent, color, parent=None, imagefile=None):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.radius = radius
        self.mass = mass
        self.parent = parent # object being orbited
        self.distance_from_parent = distance_from_parent
        self.color = color
        self.imagefile = imagefile
        if self.imagefile:
            if os.path.exists(imagefile):
                self.image = pygame.image.load(imagefile)
                self.image = pygame.transform.scale(self.image, (2 * radius, 2 * radius))  # Scale image to match radius
                self.rect = self.image.get_rect()
        
        self.orbit = [] # orbit x,y points
        self.pos = np.array([0.0, 0.0])
        self.vel = np.array([0.0, 0.0])

        # initial position
        if self.parent is None:  # incase of sun
            self.pos = np.array([0.0, 0.0])
        else:
            self.pos = np.array([distance_from_parent + self.parent.pos[0], self.parent.pos[1]])

    def draw(self, win):
        distance_scale = 0 
        # Scale moon distance for visual purposes
        if self.name == "Moon":
            distance_scale = 20 # stops moon from rendering inside of the earth

        # scaled positions
        x = self.pos[0] * self.SCALE + WIDTH / 2 + distance_scale
        y = self.pos[1] * self.SCALE + HEIGHT / 2 + distance_scale
        

        # draw orbit lines
        if len(self.orbit) >= 3:
            points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2 + distance_scale
                y = y * self.SCALE + HEIGHT / 2 + distance_scale
                points.append((x,y))
            pygame.draw.lines(win, self.color, False, points, 2)
        


        # draw body
        if self.imagefile and os.path.exists(self.imagefile):
            self.rect.center = (int(x),int(y))
            win.blit(self.image, self.rect)
        else:
            pygame.draw.circle(win, self.color, (int(x), int(y)), self.radius)
        # draw name
        font = pygame.font.Font(None, 18)
        text = font.render(self.name, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (int(x) + self.radius + 15, int(y) - self.radius - 10)
        if self.parent != None:
            WIN.blit(text, text_rect)

    def attraction(self, other): # force of attraction calculation
        d = other.pos - self.pos
        r = np.linalg.norm(d)
        u = d / r
        force = u * self.G * self.mass * other.mass / (r * r)
        return force

    def update_pos(self, objects):
        total_force = np.array([0.0, 0.0])
        # calculate gravitational force from all objects
        for o in objects:
            if self is not o:
                total_force += self.attraction(o)

        def f(t, state, arg1, arg2):  # arg1: mass, arg2: G
            return np.concatenate([state[2:], total_force / arg1])

        # solve
        solver = ode(f)
        solver.set_integrator('dop853')
        solver.set_initial_value(np.concatenate([self.pos, self.vel]), 0)
        solver.set_f_params(self.mass, self.G)

        solver.integrate(solver.t + self.dt)

        self.pos = solver.y[:2]
        self.vel = solver.y[2:]

        self.orbit.append(self.pos) # for orbit lines


def main():
    pygame.init()
    run = True
    # initialize all bodies
    sun = HeavenlyBody(name="Sun", radius=30, mass=1.98892 * 10 ** 30, distance_from_parent=0, color=YELLOW, imagefile="assets/sun.png")
    
    earth = HeavenlyBody(name="Earth", radius=16, mass=5.9742 * 10 ** 24, distance_from_parent=-1 * HeavenlyBody.AU, color=BLUE, parent=sun, imagefile="assets/earth.png")
    earth.vel = np.array([0.0, 29.784 * 1000])
    

    mars = HeavenlyBody(name="Mars", radius=12, mass=6.39 * 10 ** 23, distance_from_parent=-1.524 * HeavenlyBody.AU, color=RED, parent=sun, imagefile="assets/mars.png")
    mars.vel = np.array([0.0, 24.077 * 1000])
    

    mercury = HeavenlyBody(name="Merury", radius=8, mass=3.30 * 10 ** 23, distance_from_parent=0.387 * HeavenlyBody.AU, color=GREY, parent=sun, imagefile="assets/mercury.png")
    mercury.vel = np.array([0.0, -47.9 * 1000])
    

    venus = HeavenlyBody(name="Venus", radius=14, mass=4.8685 * 10 ** 24, distance_from_parent=0.723 * HeavenlyBody.AU, color=ORANGE, parent=sun, imagefile="assets/venus.png")
    venus.vel = np.array([0.0, -35.02 * 1000])

    moon = HeavenlyBody(name="Moon", radius=4, mass=7.348 * 10 ** 22, distance_from_parent=0.002418 * HeavenlyBody.AU, color=WHITE, parent=earth, imagefile="assets/moon.png")
    moon.vel = np.array([0.0, 30.806 * 1000])
    
    # all bodies
    heavenlyBodies = [sun, earth, mars, mercury, venus, moon]

    while run:
        WIN.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                run = False
                
        # draw and update bodies
        for body in heavenlyBodies:
            body.update_pos(heavenlyBodies)
            body.draw(WIN)

        # Render text
        font = pygame.font.Font(None, 24)
        text = font.render("*not to scale", True, (255, 255, 255))  
        text_rect = text.get_rect()
        text_rect.bottomleft = (10, HEIGHT - 10)
        WIN.blit(text, text_rect)

        pygame.display.update()
    
    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()