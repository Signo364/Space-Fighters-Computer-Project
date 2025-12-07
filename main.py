import pygame
import os
import random
import math
pygame.init()

try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except pygame.error:
    AUDIO_ENABLED = False
    print("Audio device not available, continuing without sound.")

WIDTH, HEIGHT = 900, 500
FULLSCREEN = False

def init_display():
    global WIN, FULLSCREEN
    if FULLSCREEN:
        WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SPACE BATTLE - Neon Edition")
    return WIN

WIN = init_display()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
DARK_RED = (200, 40, 40)
BRIGHT_RED = (255, 100, 100)
YELLOW = (255, 255, 60)
DARK_YELLOW = (200, 200, 40)
BRIGHT_YELLOW = (255, 255, 150)
CYAN = (0, 255, 255)
DARK_CYAN = (0, 180, 180)
GREEN = (50, 255, 50)
MAGENTA = (255, 50, 255)
ORANGE = (255, 150, 50)
PURPLE = (180, 50, 255)
PINK = (255, 100, 200)

NEON_BLUE = (50, 150, 255)
NEON_PINK = (255, 50, 180)
NEON_GREEN = (50, 255, 150)
NEON_PURPLE = (200, 100, 255)
ELECTRIC_BLUE = (100, 200, 255)

BORDER = pygame.Rect(WIDTH//2 - 5, 0, 10, HEIGHT)

if AUDIO_ENABLED:
    BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Grenade+1.mp3'))
    BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Gun+Silencer.mp3'))
    BULLET_HIT_SOUND.set_volume(0.3)
    BULLET_FIRE_SOUND.set_volume(0.3)
else:
    BULLET_HIT_SOUND = None
    BULLET_FIRE_SOUND = None

HEALTH_FONT = pygame.font.SysFont('arial', 20, bold=True)
WINNER_FONT = pygame.font.SysFont('arial', 80, bold=True)
TITLE_FONT = pygame.font.SysFont('arial', 70, bold=True)
INSTRUCTION_FONT = pygame.font.SysFont('arial', 24)
BULLET_COUNT_FONT = pygame.font.SysFont('arial', 18, bold=True)
MENU_FONT = pygame.font.SysFont('arial', 28, bold=True)
SMALL_FONT = pygame.font.SysFont('arial', 16)
HUGE_FONT = pygame.font.SysFont('arial', 100, bold=True)

FPS = 60
VEL = 5
BULLETS_VEL = 10
MAX_BULLETS = 3
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space.jpg')), (WIDTH, HEIGHT))

screen_shake_amount = 0
screen_shake_decay = 0.85


def toggle_fullscreen():
    global FULLSCREEN, WIN
    FULLSCREEN = not FULLSCREEN
    init_display()


def render_game_surface():
    """Create a surface for the game that can be scaled in fullscreen"""
    return pygame.Surface((WIDTH, HEIGHT))


def display_surface(game_surface):
    """Display the game surface, scaled if in fullscreen"""
    if FULLSCREEN:
        screen_w, screen_h = WIN.get_size()
        scale_factor = min(screen_w / WIDTH, screen_h / HEIGHT)
        scaled_w = int(WIDTH * scale_factor)
        scaled_h = int(HEIGHT * scale_factor)
        scaled_surface = pygame.transform.scale(game_surface, (scaled_w, scaled_h))
        
        # Center the game
        x_offset = (screen_w - scaled_w) // 2
        y_offset = (screen_h - scaled_h) // 2
        
        WIN.fill(BLACK)
        WIN.blit(scaled_surface, (x_offset, y_offset))
    else:
        WIN.blit(game_surface, (0, 0))
    
    pygame.display.update()


class Star:
    def __init__(self, layer=1):
        self.layer = layer
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.reset_properties()
        
    def reset_properties(self):
        self.speed = (0.3 + random.random() * 1.0) * self.layer
        self.size = max(1, int(random.random() * 2 + self.layer * 0.5))
        self.brightness = random.randint(150, 255)
        self.twinkle_speed = random.random() * 0.15 + 0.05
        self.twinkle_offset = random.random() * math.pi * 2
        self.color_shift = random.choice([
            (0, 0, 0), (30, 0, 0), (0, 0, 30), (20, 20, 0), (0, 20, 20)
        ])
        
    def reset(self):
        self.x = WIDTH + random.randint(10, 50)
        self.y = random.randint(0, HEIGHT)
        self.reset_properties()
            
    def update(self):
        self.x -= self.speed
        if self.x < -5:
            self.reset()
            
    def draw(self, surface, time):
        twinkle = math.sin(time * self.twinkle_speed + self.twinkle_offset) * 0.4 + 0.6
        brightness = int(self.brightness * twinkle)
        r = min(255, brightness + self.color_shift[0])
        g = min(255, brightness + self.color_shift[1])
        b = min(255, brightness + self.color_shift[2])
        
        if self.size > 1 and twinkle > 0.8:
            glow_color = (r//3, g//3, b//3)
            pygame.draw.circle(surface, glow_color, (int(self.x), int(self.y)), self.size + 2)
        
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), self.size)


class ShootingStar:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.length = 0
        self.lifetime = 0
        
    def spawn(self):
        self.active = True
        self.x = random.randint(WIDTH//2, WIDTH)
        self.y = random.randint(0, HEIGHT//3)
        speed = random.randint(15, 25)
        angle = random.random() * 0.5 + 0.2
        self.vx = -speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.length = random.randint(30, 60)
        self.lifetime = 60
        
    def update(self):
        if self.active:
            self.x += self.vx
            self.y += self.vy
            self.lifetime -= 1
            if self.lifetime <= 0 or self.x < -50 or self.y > HEIGHT + 50:
                self.reset()
                
    def draw(self, surface):
        if self.active:
            alpha = self.lifetime / 60
            for i in range(self.length):
                t = i / self.length
                px = self.x - self.vx * t * 0.5
                py = self.y - self.vy * t * 0.5
                brightness = int(255 * (1 - t) * alpha)
                size = max(1, int(3 * (1 - t)))
                if brightness > 0:
                    pygame.draw.circle(surface, (brightness, brightness, brightness), 
                                      (int(px), int(py)), size)


class Particle:
    def __init__(self, x, y, color, velocity=None, size=3, lifetime=30, gravity=0, fade=True):
        self.x = x
        self.y = y
        self.color = color
        self.original_color = color
        if velocity:
            self.vx, self.vy = velocity
        else:
            angle = random.random() * math.pi * 2
            speed = random.random() * 3 + 1
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        self.size = size
        self.original_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.alive = True
        self.fade = fade
        self.rotation = random.random() * 360
        self.rotation_speed = random.random() * 10 - 5
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.99
        self.vy *= 0.99
        self.lifetime -= 1
        self.rotation += self.rotation_speed
        
        if self.fade:
            progress = self.lifetime / self.max_lifetime
            self.size = self.original_size * progress
        
        if self.lifetime <= 0:
            self.alive = False
            
    def draw(self, surface):
        if self.alive and self.size > 0.5:
            alpha = self.lifetime / self.max_lifetime if self.fade else 1
            r = min(255, int(self.color[0] * alpha))
            g = min(255, int(self.color[1] * alpha))
            b = min(255, int(self.color[2] * alpha))
            
            if self.size > 2:
                glow_r, glow_g, glow_b = r//3, g//3, b//3
                pygame.draw.circle(surface, (glow_r, glow_g, glow_b), 
                                 (int(self.x), int(self.y)), int(self.size * 2))
            
            pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), max(1, int(self.size)))


class Spark(Particle):
    def __init__(self, x, y, color, velocity=None):
        super().__init__(x, y, color, velocity, size=2, lifetime=random.randint(10, 25))
        self.trail = []
        self.max_trail = 5
        
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        super().update()
        
    def draw(self, surface):
        if self.alive:
            for i, (tx, ty) in enumerate(self.trail):
                alpha = (i + 1) / len(self.trail) * (self.lifetime / self.max_lifetime)
                r = min(255, int(self.color[0] * alpha))
                g = min(255, int(self.color[1] * alpha))
                b = min(255, int(self.color[2] * alpha))
                size = max(1, int(self.size * alpha))
                pygame.draw.circle(surface, (r, g, b), (int(tx), int(ty)), size)
            super().draw(surface)


class ThrusterFlame:
    def __init__(self, ship_rect, facing_left=True):
        self.ship = ship_rect
        self.facing_left = facing_left
        self.particles = []
        self.time = 0
        
    def update(self, is_moving=True):
        self.time += 1
        
        if self.time % 1 == 0:
            count = 3 if is_moving else 1
            for _ in range(count):
                if self.facing_left:
                    x = self.ship.x + self.ship.width + random.randint(0, 5)
                    vx = random.random() * 3 + 2
                else:
                    x = self.ship.x - random.randint(0, 5)
                    vx = -(random.random() * 3 + 2)
                
                y = self.ship.y + self.ship.height // 2 + random.randint(-8, 8)
                vy = random.random() * 1.5 - 0.75
                
                colors = [CYAN, ELECTRIC_BLUE, WHITE, NEON_BLUE, (150, 220, 255)]
                color = random.choice(colors)
                
                particle = Particle(x, y, color, velocity=(vx, vy), 
                                   size=random.randint(2, 5), lifetime=random.randint(8, 15))
                self.particles.append(particle)
        
        for particle in self.particles[:]:
            particle.update()
            if not particle.alive:
                self.particles.remove(particle)
                
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


class BulletTrail:
    def __init__(self, bullet, color):
        self.bullet = bullet
        self.color = color
        self.trail_points = []
        self.max_length = 12
        
    def update(self):
        self.trail_points.append((self.bullet.x + self.bullet.width//2, 
                                   self.bullet.y + self.bullet.height//2))
        if len(self.trail_points) > self.max_length:
            self.trail_points.pop(0)
            
    def draw(self, surface):
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                alpha = (i + 1) / len(self.trail_points)
                width = int(4 * alpha) + 1
                r = int(self.color[0] * alpha)
                g = int(self.color[1] * alpha)
                b = int(self.color[2] * alpha)
                pygame.draw.line(surface, (r, g, b), 
                               self.trail_points[i], 
                               self.trail_points[i + 1], width)
            
            if len(self.trail_points) > 2:
                glow_color = (self.color[0]//4, self.color[1]//4, self.color[2]//4)
                for i in range(len(self.trail_points) - 1):
                    pygame.draw.line(surface, glow_color,
                                   self.trail_points[i],
                                   self.trail_points[i + 1], 6)


class EnergyRing:
    def __init__(self, x, y, color, max_radius=100, speed=3):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 5
        self.max_radius = max_radius
        self.speed = speed
        self.alive = True
        
    def update(self):
        self.radius += self.speed
        if self.radius > self.max_radius:
            self.alive = False
            
    def draw(self, surface):
        if self.alive:
            alpha = 1 - (self.radius / self.max_radius)
            r = int(self.color[0] * alpha)
            g = int(self.color[1] * alpha)
            b = int(self.color[2] * alpha)
            width = max(1, int(3 * alpha))
            pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), 
                             int(self.radius), width)


particles = []
energy_rings = []
stars_layer1 = [Star(1) for _ in range(60)]
stars_layer2 = [Star(2) for _ in range(35)]
stars_layer3 = [Star(3) for _ in range(20)]
all_stars = stars_layer1 + stars_layer2 + stars_layer3
shooting_stars = [ShootingStar() for _ in range(3)]
game_time = 0


def create_explosion(x, y, color, count=25, speed_mult=1.0):
    global particles, energy_rings
    
    energy_rings.append(EnergyRing(x, y, color, max_radius=80, speed=4))
    energy_rings.append(EnergyRing(x, y, WHITE, max_radius=50, speed=6))
    
    for _ in range(count):
        angle = random.random() * math.pi * 2
        speed = (random.random() * 5 + 2) * speed_mult
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.randint(2, 6)
        lifetime = random.randint(25, 50)
        
        variation = random.randint(-40, 40)
        varied_color = (
            max(0, min(255, color[0] + variation)),
            max(0, min(255, color[1] + variation)),
            max(0, min(255, color[2] + variation))
        )
        
        particles.append(Particle(x, y, varied_color, velocity=(vx, vy), 
                                  size=size, lifetime=lifetime, gravity=0.08))
    
    for _ in range(10):
        angle = random.random() * math.pi * 2
        speed = random.random() * 8 + 3
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        particles.append(Spark(x, y, WHITE, velocity=(vx, vy)))


def create_hit_effect(x, y, color):
    global particles, screen_shake_amount, energy_rings
    screen_shake_amount = 12
    
    energy_rings.append(EnergyRing(x, y, color, max_radius=60, speed=5))
    
    create_explosion(x, y, color, count=20, speed_mult=0.9)
    
    for _ in range(8):
        angle = random.random() * math.pi * 2
        speed = random.random() * 6 + 2
        particles.append(Spark(x, y, WHITE, velocity=(math.cos(angle)*speed, math.sin(angle)*speed)))


def create_muzzle_flash(x, y, facing_left):
    global particles
    base_vx = 5 if not facing_left else -5
    
    for _ in range(12):
        vx = base_vx + random.random() * 4 - 2
        vy = random.random() * 3 - 1.5
        color = random.choice([WHITE, YELLOW, ORANGE, BRIGHT_YELLOW])
        particles.append(Particle(x, y, color, velocity=(vx, vy), size=random.randint(2, 4), lifetime=10))
    
    for _ in range(5):
        particles.append(Spark(x, y, WHITE, velocity=(base_vx * 1.5 + random.random()*2-1, random.random()*2-1)))


def create_victory_explosion(x, y, color):
    global particles, energy_rings
    
    for i in range(5):
        delay_radius = 30 + i * 40
        energy_rings.append(EnergyRing(x, y, color, max_radius=delay_radius + 60, speed=3 + i))
    
    for ring in range(4):
        for i in range(25):
            angle = (i / 25) * math.pi * 2 + ring * 0.3
            speed = 4 + ring * 2.5
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            ring_color = [color, CYAN, MAGENTA, WHITE][ring % 4]
            particles.append(Particle(x, y, ring_color, velocity=(vx, vy), 
                                      size=5, lifetime=60 + ring * 15))
    
    for _ in range(50):
        angle = random.random() * math.pi * 2
        speed = random.random() * 10 + 3
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        sparkle_color = random.choice([WHITE, CYAN, MAGENTA, YELLOW, color, NEON_PINK])
        particles.append(Particle(x, y, sparkle_color, velocity=(vx, vy), 
                                  size=random.randint(2, 7), lifetime=random.randint(50, 100)))
    
    for _ in range(20):
        particles.append(Spark(x, y, random.choice([WHITE, color]), 
                              velocity=(random.random()*16-8, random.random()*16-8)))


def draw_glow_rect(surface, color, rect, glow_size=5):
    for i in range(glow_size, 0, -1):
        alpha = 0.3 / i
        glow_r = int(color[0] * alpha)
        glow_g = int(color[1] * alpha)
        glow_b = int(color[2] * alpha)
        glow_rect = rect.inflate(i*3, i*3)
        pygame.draw.rect(surface, (glow_r, glow_g, glow_b), glow_rect, border_radius=3)
    
    pygame.draw.rect(surface, color, rect, border_radius=2)
    
    highlight = (min(255, color[0]+80), min(255, color[1]+80), min(255, color[2]+80))
    pygame.draw.line(surface, highlight, (rect.x+2, rect.y+1), (rect.x+rect.width-2, rect.y+1))


def draw_neon_text(surface, text, font, x, y, color, glow_intensity=3):
    for offset in range(glow_intensity, 0, -1):
        glow_alpha = 0.4 / offset
        glow_r = int(color[0] * glow_alpha)
        glow_g = int(color[1] * glow_alpha)
        glow_b = int(color[2] * glow_alpha)
        glow_text = font.render(text, True, (glow_r, glow_g, glow_b))
        for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset),
                       (-offset, -offset), (offset, offset), (-offset, offset), (offset, -offset)]:
            surface.blit(glow_text, (x + dx, y + dy))
    
    main_text = font.render(text, True, color)
    surface.blit(main_text, (x, y))


def draw_health_bar(surface, x, y, health, max_health, width, height, color):
    pygame.draw.rect(surface, (20, 20, 30), (x-3, y-3, width+6, height+6), border_radius=6)
    
    for i in range(3, 0, -1):
        glow_alpha = 0.2 / i
        glow_color = (int(color[0]*glow_alpha), int(color[1]*glow_alpha), int(color[2]*glow_alpha))
        pygame.draw.rect(surface, glow_color, (x-i*2, y-i*2, width+i*4, height+i*4), border_radius=6)
    
    pygame.draw.rect(surface, (40, 40, 50), (x, y, width, height), border_radius=4)
    
    health_width = int((health / max_health) * width)
    if health_width > 0:
        for i in range(height):
            progress = i / height
            brightness = 1.0 - progress * 0.4
            r = int(color[0] * brightness)
            g = int(color[1] * brightness)
            b = int(color[2] * brightness)
            pygame.draw.line(surface, (r, g, b), (x, y + i), (x + health_width, y + i))
        
        highlight = (min(255, color[0]+100), min(255, color[1]+100), min(255, color[2]+100))
        pygame.draw.line(surface, highlight, (x+1, y+1), (x + health_width-1, y+1), 2)
        
        pygame.draw.rect(surface, WHITE, (x + health_width - 3, y, 3, height), border_radius=1)
    
    pygame.draw.rect(surface, color, (x, y, width, height), 2, border_radius=4)


def draw_ammo_display(surface, x, y, current_ammo, max_ammo, color):
    for i in range(max_ammo):
        bullet_x = x + i * 18
        if i < current_ammo:
            for g in range(3, 0, -1):
                glow_color = (color[0]//4, color[1]//4, color[2]//4)
                pygame.draw.rect(surface, glow_color, (bullet_x-g, y-g, 12+g*2, 8+g*2), border_radius=3)
            pygame.draw.rect(surface, color, (bullet_x, y, 12, 8), border_radius=2)
            pygame.draw.rect(surface, WHITE, (bullet_x, y, 12, 3), border_radius=1)
        else:
            pygame.draw.rect(surface, (30, 30, 40), (bullet_x, y, 12, 8), border_radius=2)
            pygame.draw.rect(surface, (50, 50, 60), (bullet_x, y, 12, 8), 1, border_radius=2)


def draw_animated_background(surface, time):
    surface.fill((5, 5, 15))
    
    surface.blit(SPACE, (0, 0), special_flags=pygame.BLEND_ADD)
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 30, 60))
    surface.blit(overlay, (0, 0))
    
    for star in all_stars:
        star.update()
        star.draw(surface, time)
    
    if random.random() < 0.01:
        for ss in shooting_stars:
            if not ss.active:
                ss.spawn()
                break
    
    for ss in shooting_stars:
        ss.update()
        ss.draw(surface)


def draw_neon_border(surface, time):
    pulse = math.sin(time * 0.08) * 0.4 + 0.6
    wave_offset = time * 3
    
    for i in range(12, 0, -2):
        glow_intensity = pulse / (i * 0.5)
        glow_color = (0, int(180 * glow_intensity), int(255 * glow_intensity))
        glow_rect = BORDER.inflate(i*2, 0)
        pygame.draw.rect(surface, glow_color, glow_rect)
    
    gradient_surface = pygame.Surface((BORDER.width, HEIGHT), pygame.SRCALPHA)
    for y in range(HEIGHT):
        wave = math.sin((y + wave_offset) * 0.05) * 0.3 + 0.7
        brightness = int(200 * wave * pulse)
        color = (0, brightness, min(255, brightness + 50))
        pygame.draw.line(gradient_surface, color, (0, y), (BORDER.width, y))
    surface.blit(gradient_surface, (BORDER.x, 0))
    
    pygame.draw.rect(surface, WHITE, BORDER, 1)
    
    for y in range(0, HEIGHT, 30):
        spark_y = (y + int(wave_offset * 2)) % HEIGHT
        spark_brightness = int((math.sin(spark_y * 0.1 + time * 0.1) + 1) * 127)
        if spark_brightness > 200:
            pygame.draw.circle(surface, WHITE, (BORDER.centerx, spark_y), 2)


def draw_control_scheme_screen():
    global game_time
    game_time += 1
    
    game_surface = render_game_surface()
    draw_animated_background(game_surface, game_time)
    
    title_y = 50 + math.sin(game_time * 0.04) * 8
    draw_neon_text(game_surface, "SELECT CONTROLS", TITLE_FONT, 
                   WIDTH//2 - TITLE_FONT.size("SELECT CONTROLS")[0]//2, 
                   int(title_y), CYAN, glow_intensity=4)
    
    box_width, box_height = 380, 130
    box1_x = WIDTH//2 - box_width//2
    box1_y = 160
    
    box1_pulse = math.sin(game_time * 0.1) * 0.2 + 0.8
    for i in range(5, 0, -1):
        glow_color = (0, int(60 * box1_pulse / i), int(100 * box1_pulse / i))
        pygame.draw.rect(game_surface, glow_color, 
                        (box1_x - i*2, box1_y - i*2, box_width + i*4, box_height + i*4), 
                        border_radius=15)
    
    pygame.draw.rect(game_surface, (15, 30, 50), (box1_x, box1_y, box_width, box_height), border_radius=12)
    pygame.draw.rect(game_surface, NEON_BLUE, (box1_x, box1_y, box_width, box_height), 2, border_radius=12)
    
    draw_neon_text(game_surface, "Press 1: Arrow Keys", MENU_FONT,
                   box1_x + 30, box1_y + 20, NEON_BLUE)
    game_surface.blit(INSTRUCTION_FONT.render("Move: Arrow Keys", True, WHITE), (box1_x + 30, box1_y + 60))
    game_surface.blit(INSTRUCTION_FONT.render("Shoot: Right Ctrl", True, WHITE), (box1_x + 30, box1_y + 90))
    
    box2_y = 310
    box2_pulse = math.sin(game_time * 0.1 + 1) * 0.2 + 0.8
    for i in range(5, 0, -1):
        glow_color = (int(80 * box2_pulse / i), 0, int(60 * box2_pulse / i))
        pygame.draw.rect(game_surface, glow_color, 
                        (box1_x - i*2, box2_y - i*2, box_width + i*4, box_height + i*4), 
                        border_radius=15)
    
    pygame.draw.rect(game_surface, (40, 15, 50), (box1_x, box2_y, box_width, box_height), border_radius=12)
    pygame.draw.rect(game_surface, NEON_PINK, (box1_x, box2_y, box_width, box_height), 2, border_radius=12)
    
    draw_neon_text(game_surface, "Press 2: Mouse Control", MENU_FONT,
                   box1_x + 30, box2_y + 20, NEON_PINK)
    game_surface.blit(INSTRUCTION_FONT.render("Move: Mouse Position", True, WHITE), (box1_x + 30, box2_y + 60))
    game_surface.blit(INSTRUCTION_FONT.render("Shoot: Left Click", True, WHITE), (box1_x + 30, box2_y + 90))
    
    display_surface(game_surface)


def draw_start_screen(control_scheme):
    global game_time
    game_time += 1
    
    game_surface = render_game_surface()
    draw_animated_background(game_surface, game_time)
    
    title_y = 60 + math.sin(game_time * 0.04) * 10
    
    draw_neon_text(game_surface, "SPACE BATTLE", HUGE_FONT,
                   WIDTH//2 - HUGE_FONT.size("SPACE BATTLE")[0]//2,
                   int(title_y), CYAN, glow_intensity=5)
    
    subtitle_pulse = (math.sin(game_time * 0.1) + 1) / 2
    subtitle_color = (
        int(255 * subtitle_pulse + 100 * (1 - subtitle_pulse)),
        int(50 * subtitle_pulse + 100 * (1 - subtitle_pulse)),
        int(255 * (1 - subtitle_pulse) + 200 * subtitle_pulse)
    )
    draw_neon_text(game_surface, "NEON EDITION", MENU_FONT,
                   WIDTH//2 - MENU_FONT.size("NEON EDITION")[0]//2,
                   int(title_y) + 90, subtitle_color)
    
    blink = int((math.sin(game_time * 0.12) + 1) * 60) + 135
    restart_text = INSTRUCTION_FONT.render("R - Restart  |  C - Controls  |  F11 - Fullscreen  |  ESC - Quit", True, (blink, blink, blink))
    game_surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    box_x, box_y = WIDTH//2 - 200, 260
    pygame.draw.rect(game_surface, (20, 20, 35), (box_x, box_y, 400, 110), border_radius=12)
    pygame.draw.rect(game_surface, (60, 60, 90), (box_x, box_y, 400, 110), 2, border_radius=12)
    
    yellow_text = INSTRUCTION_FONT.render("Yellow: WASD + Left Ctrl", True, YELLOW)
    game_surface.blit(yellow_text, (WIDTH//2 - yellow_text.get_width()//2, box_y + 20))
    
    if control_scheme == 1:
        red_text = INSTRUCTION_FONT.render("Red: Arrows + Right Ctrl", True, RED)
    else:
        red_text = INSTRUCTION_FONT.render("Red: Mouse + Left Click", True, RED)
    game_surface.blit(red_text, (WIDTH//2 - red_text.get_width()//2, box_y + 55))
    
    change_text = SMALL_FONT.render("Press C to change controls", True, (120, 120, 140))
    game_surface.blit(change_text, (WIDTH//2 - change_text.get_width()//2, 390))
    
    ship_float_y = math.sin(game_time * 0.06) * 15
    ship_float_r = math.sin(game_time * 0.06 + math.pi) * 15
    
    ship_bob_y = math.sin(game_time * 0.15) * 3
    ship_bob_r = math.sin(game_time * 0.15 + 0.5) * 3
    
    game_surface.blit(YELLOW_SPACESHIP, (80, 180 + ship_float_y + ship_bob_y))
    game_surface.blit(RED_SPACESHIP, (WIDTH - 130, 180 + ship_float_r + ship_bob_r))
    
    for i in range(3):
        spark_x = 135 + random.randint(-2, 2)
        spark_y = 200 + ship_float_y + random.randint(-5, 5)
        pygame.draw.circle(game_surface, CYAN, (spark_x, int(spark_y)), random.randint(1, 3))
    
    for i in range(3):
        spark_x = WIDTH - 135 + random.randint(-2, 2)
        spark_y = 200 + ship_float_r + random.randint(-5, 5)
        pygame.draw.circle(game_surface, ORANGE, (spark_x, int(spark_y)), random.randint(1, 3))
    
    display_surface(game_surface)


def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, 
                yellow_thruster, red_thruster, bullet_trails, red_flash=0, yellow_flash=0):
    global game_time, screen_shake_amount, particles, energy_rings
    game_time += 1
    
    shake_x = int(random.uniform(-screen_shake_amount, screen_shake_amount)) if screen_shake_amount > 0.5 else 0
    shake_y = int(random.uniform(-screen_shake_amount, screen_shake_amount)) if screen_shake_amount > 0.5 else 0
    screen_shake_amount *= screen_shake_decay
    if screen_shake_amount < 0.5:
        screen_shake_amount = 0
    
    temp_surface = pygame.Surface((WIDTH, HEIGHT))
    
    draw_animated_background(temp_surface, game_time)
    
    draw_neon_border(temp_surface, game_time)
    
    for ring in energy_rings[:]:
        ring.update()
        if not ring.alive:
            energy_rings.remove(ring)
        else:
            ring.draw(temp_surface)
    
    for particle in particles[:]:
        particle.update()
        if not particle.alive:
            particles.remove(particle)
        else:
            particle.draw(temp_surface)
    
    yellow_thruster.ship = yellow
    red_thruster.ship = red
    yellow_thruster.update(True)
    yellow_thruster.draw(temp_surface)
    red_thruster.update(True)
    red_thruster.draw(temp_surface)
    
    for trail in bullet_trails:
        trail.update()
        trail.draw(temp_surface)
    
    if yellow_flash > 0:
        flash_intensity = yellow_flash / 10
        flash_surface = pygame.Surface((SPACESHIP_WIDTH + 10, SPACESHIP_HEIGHT + 10), pygame.SRCALPHA)
        flash_surface.fill((255, 255, 200, int(150 * flash_intensity)))
        temp_surface.blit(flash_surface, (yellow.x - 5, yellow.y - 5))
    temp_surface.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    
    if red_flash > 0:
        flash_intensity = red_flash / 10
        flash_surface = pygame.Surface((SPACESHIP_WIDTH + 10, SPACESHIP_HEIGHT + 10), pygame.SRCALPHA)
        flash_surface.fill((255, 200, 200, int(150 * flash_intensity)))
        temp_surface.blit(flash_surface, (red.x - 5, red.y - 5))
    temp_surface.blit(RED_SPACESHIP, (red.x, red.y))
    
    for bullet in yellow_bullets:
        draw_glow_rect(temp_surface, BRIGHT_YELLOW, bullet, glow_size=4)
    
    for bullet in red_bullets:
        draw_glow_rect(temp_surface, BRIGHT_RED, bullet, glow_size=4)
    
    draw_health_bar(temp_surface, 15, 15, yellow_health, 10, 160, 22, YELLOW)
    draw_neon_text(temp_surface, "YELLOW", SMALL_FONT, 15, 42, YELLOW)
    
    draw_health_bar(temp_surface, WIDTH - 175, 15, red_health, 10, 160, 22, RED)
    draw_neon_text(temp_surface, "RED", SMALL_FONT, WIDTH - 45, 42, RED)
    
    yellow_ammo = MAX_BULLETS - len(yellow_bullets)
    red_ammo = MAX_BULLETS - len(red_bullets)
    
    draw_ammo_display(temp_surface, 15, 65, yellow_ammo, MAX_BULLETS, YELLOW)
    draw_ammo_display(temp_surface, WIDTH - 69, 65, red_ammo, MAX_BULLETS, RED)
    
    game_surface = pygame.Surface((WIDTH, HEIGHT))
    game_surface.blit(temp_surface, (shake_x, shake_y))
    display_surface(game_surface)


def draw_winner(text, winner_color):
    global game_time, particles, energy_rings
    game_time += 1
    
    game_surface = render_game_surface()
    draw_animated_background(game_surface, game_time)
    draw_neon_border(game_surface, game_time)
    
    for ring in energy_rings[:]:
        ring.update()
        if not ring.alive:
            energy_rings.remove(ring)
        else:
            ring.draw(game_surface)
    
    for particle in particles[:]:
        particle.update()
        if not particle.alive:
            particles.remove(particle)
        else:
            particle.draw(game_surface)
    
    box_width, box_height = 550, 220
    box_x = WIDTH//2 - box_width//2
    box_y = HEIGHT//2 - box_height//2
    
    for i in range(8, 0, -1):
        glow_alpha = 0.15 / i
        glow_color = (int(winner_color[0]*glow_alpha), int(winner_color[1]*glow_alpha), int(winner_color[2]*glow_alpha))
        pygame.draw.rect(game_surface, glow_color, 
                        (box_x - i*3, box_y - i*3, box_width + i*6, box_height + i*6), 
                        border_radius=20)
    
    pygame.draw.rect(game_surface, (15, 15, 25), (box_x, box_y, box_width, box_height), border_radius=15)
    pygame.draw.rect(game_surface, winner_color, (box_x, box_y, box_width, box_height), 3, border_radius=15)
    
    text_pulse = math.sin(game_time * 0.1) * 0.1 + 0.9
    pulse_color = (
        int(winner_color[0] * text_pulse),
        int(winner_color[1] * text_pulse),
        int(winner_color[2] * text_pulse)
    )
    
    draw_neon_text(game_surface, text, WINNER_FONT,
                   WIDTH//2 - WINNER_FONT.size(text)[0]//2,
                   HEIGHT//2 - 50, pulse_color, glow_intensity=5)
    
    blink = int((math.sin(game_time * 0.12) + 1) * 60) + 135
    restart_text = INSTRUCTION_FONT.render("R - Restart  |  F11 - Fullscreen  |  ESC - Quit", True, (blink, blink, blink))
    game_surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    display_surface(game_surface)


def game_loop(control_scheme):
    global particles, screen_shake_amount, energy_rings
    
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    red_bullets = []
    yellow_bullets = []
    bullet_trails = []

    red_health = 10
    yellow_health = 10
    
    red_flash = 0
    yellow_flash = 0
    
    yellow_thruster = ThrusterFlame(yellow, facing_left=False)
    red_thruster = ThrusterFlame(red, facing_left=True)
    
    particles = []
    energy_rings = []

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        
        if red_flash > 0:
            red_flash -= 1
        if yellow_flash > 0:
            yellow_flash -= 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, control_scheme

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height//2 - 3, 14, 7)
                    yellow_bullets.append(bullet)
                    bullet_trails.append(BulletTrail(bullet, YELLOW))
                    create_muzzle_flash(bullet.x, bullet.y + 3, False)
                    if AUDIO_ENABLED:
                        BULLET_FIRE_SOUND.play()

                if control_scheme == 1:
                    if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                        bullet = pygame.Rect(red.x - 14, red.y + red.height//2 - 3, 14, 7)
                        red_bullets.append(bullet)
                        bullet_trails.append(BulletTrail(bullet, RED))
                        create_muzzle_flash(bullet.x + 14, bullet.y + 3, True)
                        if AUDIO_ENABLED:
                            BULLET_FIRE_SOUND.play()
                
                # Fullscreen toggle
                if event.key == pygame.K_F11 or event.key == pygame.K_f:
                    toggle_fullscreen()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if control_scheme == 2 and event.button == 1 and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(red.x - 14, red.y + red.height//2 - 3, 14, 7)
                    red_bullets.append(bullet)
                    bullet_trails.append(BulletTrail(bullet, RED))
                    create_muzzle_flash(bullet.x + 14, bullet.y + 3, True)
                    if AUDIO_ENABLED:
                        BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                red_flash = 12
                create_hit_effect(red.x + red.width//2, red.y + red.height//2, ORANGE)
                if AUDIO_ENABLED:
                    BULLET_HIT_SOUND.play()

            if event.type == YELLOW_HIT:
                yellow_health -= 1
                yellow_flash = 12
                create_hit_effect(yellow.x + yellow.width//2, yellow.y + yellow.height//2, YELLOW)
                if AUDIO_ENABLED:
                    BULLET_HIT_SOUND.play()

        winner_text = ""
        winner_color = WHITE
        if red_health <= 0:
            winner_text = "YELLOW WINS!"
            winner_color = YELLOW
            create_victory_explosion(red.x + red.width//2, red.y + red.height//2, RED)

        if yellow_health <= 0:
            winner_text = "RED WINS!"
            winner_color = RED
            create_victory_explosion(yellow.x + yellow.width//2, yellow.y + yellow.height//2, YELLOW)

        if winner_text != "":
            waiting = True
            while waiting:
                clock.tick(FPS)
                draw_winner(winner_text, winner_color)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False, control_scheme
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            return True, control_scheme
                        if event.key == pygame.K_c:
                            return "controls", control_scheme
                        if event.key == pygame.K_ESCAPE:
                            return False, control_scheme
                        if event.key == pygame.K_F11 or event.key == pygame.K_f:
                            toggle_fullscreen()
            break

        keys_pressed = pygame.key.get_pressed()
        yellow_handle_movement(keys_pressed, yellow)
        red_handle_movement(keys_pressed, red, control_scheme)

        for bullet in yellow_bullets[:]:
            bullet.x += BULLETS_VEL
            if red.colliderect(bullet):
                pygame.event.post(pygame.event.Event(RED_HIT))
                yellow_bullets.remove(bullet)
                bullet_trails = [t for t in bullet_trails if t.bullet != bullet]
            elif bullet.x > WIDTH:
                yellow_bullets.remove(bullet)
                bullet_trails = [t for t in bullet_trails if t.bullet != bullet]

        for bullet in red_bullets[:]:
            bullet.x -= BULLETS_VEL
            if yellow.colliderect(bullet):
                pygame.event.post(pygame.event.Event(YELLOW_HIT))
                red_bullets.remove(bullet)
                bullet_trails = [t for t in bullet_trails if t.bullet != bullet]
            elif bullet.x < 0:
                red_bullets.remove(bullet)
                bullet_trails = [t for t in bullet_trails if t.bullet != bullet]

        draw_window(red, yellow, red_bullets, yellow_bullets,
                    red_health, yellow_health, yellow_thruster, red_thruster,
                    bullet_trails, red_flash, yellow_flash)

    return True, control_scheme


def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0:
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15:
        yellow.y += VEL


def red_handle_movement(keys_pressed, red, control_scheme):
    if control_scheme == 1:
        if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:
            red.x -= VEL
        if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH:
            red.x += VEL
        if keys_pressed[pygame.K_UP] and red.y - VEL > 0:
            red.y -= VEL
        if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT - 15:
            red.y += VEL
    else:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Adjust mouse position if in fullscreen mode
        if FULLSCREEN:
            screen_w, screen_h = WIN.get_size()
            scale_factor = min(screen_w / WIDTH, screen_h / HEIGHT)
            scaled_w = int(WIDTH * scale_factor)
            scaled_h = int(HEIGHT * scale_factor)
            x_offset = (screen_w - scaled_w) // 2
            y_offset = (screen_h - scaled_h) // 2
            
            mouse_x = int((mouse_x - x_offset) / scale_factor)
            mouse_y = int((mouse_y - y_offset) / scale_factor)
        
        red_center_x = red.x + red.width // 2
        red_center_y = red.y + red.height // 2
        
        if mouse_x > BORDER.x + BORDER.width:
            if red_center_x < mouse_x - 10 and red.x + VEL + red.width < WIDTH:
                red.x += VEL
            elif red_center_x > mouse_x + 10 and red.x - VEL > BORDER.x + BORDER.width:
                red.x -= VEL
            
            if red_center_y < mouse_y - 10 and red.y + VEL + red.height < HEIGHT - 15:
                red.y += VEL
            elif red_center_y > mouse_y + 10 and red.y - VEL > 0:
                red.y -= VEL


def main():
    clock = pygame.time.Clock()
    control_scheme = 1
    
    selecting_controls = True
    while selecting_controls:
        clock.tick(FPS)
        draw_control_scheme_screen()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    control_scheme = 1
                    selecting_controls = False
                elif event.key == pygame.K_2:
                    control_scheme = 2
                    selecting_controls = False
                elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                    toggle_fullscreen()
    
    waiting_for_start = True
    while waiting_for_start:
        clock.tick(FPS)
        draw_start_screen(control_scheme)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting_for_start = False
                elif event.key == pygame.K_c:
                    selecting_controls = True
                    while selecting_controls:
                        clock.tick(FPS)
                        draw_control_scheme_screen()
                        
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_1:
                                    control_scheme = 1
                                    selecting_controls = False
                                elif event.key == pygame.K_2:
                                    control_scheme = 2
                                    selecting_controls = False
                                elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                                    toggle_fullscreen()
                elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                    toggle_fullscreen()
    
    running = True
    while running:
        result, control_scheme = game_loop(control_scheme)
        if result == "controls":
            selecting_controls = True
            while selecting_controls:
                clock.tick(FPS)
                draw_control_scheme_screen()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            control_scheme = 1
                            selecting_controls = False
                        elif event.key == pygame.K_2:
                            control_scheme = 2
                            selecting_controls = False
                        elif event.key == pygame.K_F11 or event.key == pygame.K_f:
                            toggle_fullscreen()
        elif not result:
            running = False

    pygame.quit()


if __name__ == '__main__':
    main()
