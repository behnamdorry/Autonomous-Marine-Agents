import pygame
import random
import math
import time

pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
GAME_W = int(W * 0.7)
MAP_W = W - GAME_W
GS = 40
FPS = 60
SCAN = 3
SHARE = SCAN * 2
NET_R = 40

DEEP = (0, 0, 80)
OCEAN = (0, 50, 150)
LITE = (100, 200, 255)
YEL = (255, 255, 50)
RED = (255, 50, 50)
BLA = (0, 0, 0)
GRA = (100, 100, 100)
WHI = (255, 255, 255)

def emojis():
    def fish(c):
        s = pygame.Surface((20, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(s, c, (0, 0, 16, 12))
        pygame.draw.polygon(s, c, [(16, 6), (20, 3), (20, 9)])
        pygame.draw.circle(s, (0, 0, 0), (4, 4), 1)
        return s
    def boat():
        s = pygame.Surface((24, 12), pygame.SRCALPHA)
        pygame.draw.polygon(s, RED, [(0, 12), (12, 0), (24, 12)])
        pygame.draw.rect(s, LITE, (10, 3, 8, 4))
        return s
    def sub():
        s = pygame.Surface((24, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(s, YEL, (0, 0, 24, 12))
        pygame.draw.rect(s, LITE, (18, 3, 4, 6))
        pygame.draw.circle(s, (0, 0, 0), (4, 6), 2)
        return s
    return {'fish_red': fish((255, 50, 50)), 'fish_yel': fish(YEL),
            'fish_blu': fish((50, 150, 255)), 'fish_ora': fish((255, 165, 0)),
            'sub': sub(), 'boat': boat()}

EMOJI = emojis()

class FishSchool:
    def __init__(self, x, y):
        self.cx, self.cy = x, y
        self.n = random.randint(3, 5)
        self.sp = random.uniform(0.8, 1.2)
        self.dir = random.uniform(0, 2 * math.pi)
        self.t = 0
        self.f = [{'x': x + random.uniform(-20, 20), 'y': y + random.uniform(-20, 20),
                   'dx': 0, 'dy': 0} for _ in range(self.n)]
    def move(self):
        self.t -= 1
        if self.t <= 0:
            self.dir = random.uniform(0, 2 * math.pi)
            self.t = random.randint(60, 180)
        self.cx += math.cos(self.dir) * self.sp
        self.cy += math.sin(self.dir) * self.sp
        self.cx = max(50, min(GAME_W - 50, self.cx))
        self.cy = max(50, min(H - 50, self.cy))
        for fish in self.f:
            dx = self.cx - fish['x']; dy = self.cy - fish['y']
            d = max(1, math.hypot(dx, dy))
            fish['dx'] += dx / d * 0.3
            fish['dy'] += dy / d * 0.3
            for o in self.f:
                if o is fish: continue
                dx = fish['x'] - o['x']; dy = fish['y'] - o['y']
                d = max(1, math.hypot(dx, dy))
                if d < 25:
                    fish['dx'] += dx / d * 0.5
                    fish['dy'] += dy / d * 0.5
            fish['x'] += fish['dx']; fish['y'] += fish['dy']
            fish['dx'] *= 0.8; fish['dy'] *= 0.8
            if math.hypot(fish['x'] - self.cx, fish['y'] - self.cy) > 40:
                fish['x'] = self.cx + random.uniform(-20, 20)
                fish['y'] = self.cy + random.uniform(-20, 20)
    def pos(self): return [(f['x'], f['y']) for f in self.f]
    def draw(self, surf):
        for f in self.f:
            surf.blit(EMOJI['fish_ora'], (f['x'] - 10, f['y'] - 6))

class Sub:
    def __init__(self, x, y, name, fk):
        self.x, self.y, self.name = x, y, name
        self.fkey = fk
        self.img = EMOJI['sub']
        self.sp = 2
        self.map = {}
        self.oth = {}
        self.dir = random.uniform(0, 2 * math.pi)
        self.t = 0
    def move(self):
        self.t -= 1
        if self.t <= 0:
            self.dir = random.uniform(0, 2 * math.pi)
            self.t = random.randint(60, 180)
        nx = self.x + math.cos(self.dir) * self.sp
        ny = self.y + math.sin(self.dir) * self.sp
        if 20 <= nx <= GAME_W - 20: self.x = nx
        if 20 <= ny <= H - 20: self.y = ny
    def scan_fish(self, schools):
        gx = int(self.x // GS); gy = int(self.y // GS)
        for s in schools:
            for fx, fy in s.pos():
                fgx = int(fx // GS); fgy = int(fy // GS)
                if math.hypot(gx - fgx, gy - fgy) <= SCAN:
                    key = (fgx, fgy)
                    if key not in self.map:
                        self.map[key] = {'x': fx, 'y': fy, 'dkey': self.fkey,
                                         't': time.time(), 'sh': False}
    def scan_sub(self, subs):
        for sub in subs:
            if sub is self: continue
            dist = math.hypot(self.x - sub.x, self.y - sub.y)
            if dist <= SHARE * GS:
                self.oth[sub.name] = (sub.x, sub.y)
                self.share_data(sub)
    def share_data(self, o):
        for k, v in o.map.items():
            if k not in self.map:
                self.map[k] = v.copy(); self.map[k]['sh'] = True
            elif not self.map[k]['sh'] and v['sh']:
                self.map[k]['sh'] = True
        for k, v in self.map.items():
            if k not in o.map:
                o.map[k] = v.copy(); o.map[k]['sh'] = True
            elif not o.map[k]['sh'] and v['sh']:
                o.map[k]['sh'] = True
        self.oth.update(o.oth); o.oth.update(self.oth)
    def draw(self, surf):
        sh = pygame.Surface((SHARE * GS * 2, SHARE * GS * 2), pygame.SRCALPHA)
        pygame.draw.circle(sh, (255, 255, 255, 40),
                          (SHARE * GS, SHARE * GS), SHARE * GS, 2)
        surf.blit(sh, (self.x - SHARE * GS, self.y - SHARE * GS))
        rot = pygame.transform.rotate(self.img, -math.degrees(self.dir))
        surf.blit(rot, rot.get_rect(center=(self.x, self.y)))
        sc = pygame.Surface((GS * (SCAN * 2 + 1), GS * (SCAN * 2 + 1)), pygame.SRCALPHA)
        pygame.draw.circle(sc, (255, 255, 0, 30),
                          (GS * SCAN, GS * SCAN), GS * SCAN)
        gx = (int(self.x // GS) - SCAN) * GS
        gy = (int(self.y // GS) - SCAN) * GS
        surf.blit(sc, (gx, gy))

class FishingBoat:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.img = EMOJI['boat']
        self.sp = 4
        self.caught = 0
        self.target = None
    def move(self, shared_map):
        if not shared_map:
            self.target = None
            return
        # اگر به هدف رسیدیم آن را از لیست اشتراکی حذف کنیم
        if self.target:
            dx = self.target['x'] - self.x
            dy = self.target['y'] - self.y
            if math.hypot(dx, dy) < 10:
                key = (int(self.target['x'] // GS), int(self.target['y'] // GS))
                if key in shared_map:
                    del shared_map[key]
                self.target = None
        # انتخاب «اولین» (قدیمی‌ترین) ماهی اشتراکی باقی‌مانده
        if not self.target:
            self.target = min(shared_map.values(), key=lambda f: f['t'], default=None)
        if self.target:
            dx = self.target['x'] - self.x
            dy = self.target['y'] - self.y
            dist = max(1, math.hypot(dx, dy))
            self.x += (dx / dist) * self.sp
            self.y += (dy / dist) * self.sp
    def hunt(self, schools):
        for school in schools:
            for fish in school.f[:]:
                if math.hypot(fish['x'] - self.x, fish['y'] - self.y) < NET_R:
                    school.f.remove(fish)
                    self.caught += 1
    def draw(self, surf):
        angle = math.degrees(math.atan2(self.target['y'] - self.y,
                                       self.target['x'] - self.x)) if self.target else 0
        rot = pygame.transform.rotate(self.img, -angle)
        surf.blit(rot, rot.get_rect(center=(self.x, self.y)))
        # دایره تور
        net = pygame.Surface((NET_R * 2, NET_R * 2), pygame.SRCALPHA)
        pygame.draw.circle(net, (255, 0, 0, 40), (NET_R, NET_R), NET_R, 2)
        surf.blit(net, (self.x - NET_R, self.y - NET_R))
        # آمار
        f = pygame.font.Font(None, 24)
        surf.blit(f.render(f"Caught: {self.caught}", True, (255, 0, 0)), (self.x - 20, self.y - 25))

class Game:
    def __init__(self):
        self.sc = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption("Sub & Fishing Boat Sim")
        self.cl = pygame.time.Clock()
        self.run = True
        self.schools = [FishSchool(random.randint(100, GAME_W - 100),
                                   random.randint(100, H - 100)) for _ in range(10)]
        self.subs = [Sub(100, 100, "S1", 'fish_yel'),
                     Sub(GAME_W - 100, H - 100, "S2", 'fish_yel'),
                     Sub(GAME_W // 2, H // 2, "S3", 'fish_yel')]
        self.boat = FishingBoat(GAME_W // 4, H // 4)
        self.gmap = {}
    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                self.run = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
    def update(self):
        for s in self.schools: s.move()
        for b in self.subs:
            b.move()
            b.scan_fish(self.schools)
            b.scan_sub([s for s in self.subs if s is not b])
        shared_only = {k: v for k, v in self.gmap.items() if v.get('sh', False)}
        self.boat.move(shared_only)
        self.boat.hunt(self.schools)
        self.gmap = {}
        for b in self.subs: self.gmap.update(b.map)
        t = time.time()
        for k in list(self.gmap.keys()):
            if t - self.gmap[k]['t'] > 15: del self.gmap[k]
    def draw_left(self):
        s = pygame.Surface((GAME_W, H))
        s.fill(DEEP)
        for x in range(0, GAME_W, GS): pygame.draw.line(s, OCEAN, (x, 0), (x, H))
        for y in range(0, H, GS): pygame.draw.line(s, OCEAN, (0, y), (GAME_W, y))
        for sc in self.schools: sc.draw(s)
        for b in self.subs: b.draw(s)
        self.boat.draw(s)
        f = pygame.font.Font(None, 36)
        s.blit(f.render("Live Ocean View", True, WHI), (20, 20))
        return s
    def draw_right(self):
        s = pygame.Surface((MAP_W, H))
        s.fill(BLA)
        f1 = pygame.font.Font(None, 36); f2 = pygame.font.Font(None, 20)
        s.blit(f1.render("Global Fish Map", True, WHI), (20, 20))
        scale = min(0.6, (MAP_W - 100) / GAME_W)
        ox, oy = 30, 80
        for x in range(GAME_W // GS):
            for y in range(H // GS):
                r = pygame.Rect(ox + x * GS * scale, oy + y * GS * scale,
                                GS * scale, GS * scale)
                pygame.draw.rect(s, GRA, r, 1)
        dd = sd = 0
        for v in self.gmap.values():
            mx = ox + (v['x'] / GS) * GS * scale
            my = oy + (v['y'] / GS) * GS * scale
            col = EMOJI['fish_ora'] if v['sh'] else EMOJI[v['dkey']]
            sd += v['sh']; dd += not v['sh']
            s.blit(pygame.transform.scale(col, (10, 6)), (mx - 5, my - 3))
        for b in self.subs:
            mx = ox + (b.x / GS) * GS * scale
            my = oy + (b.y / GS) * GS * scale
            pic = pygame.transform.scale(b.img, (16, 8))
            pic = pygame.transform.rotate(pic, -math.degrees(b.dir))
            s.blit(pic, pic.get_rect(center=(mx, my)))
        mx = ox + (self.boat.x / GS) * GS * scale
        my = oy + (self.boat.y / GS) * GS * scale
        pic = pygame.transform.scale(EMOJI['boat'], (16, 8))
        angle = math.degrees(math.atan2(self.boat.target['y'] - self.boat.y,
                                       self.boat.target['x'] - self.boat.x)) if self.boat.target else 0
        pic = pygame.transform.rotate(pic, -angle)
        s.blit(pic, pic.get_rect(center=(mx, my)))
        txt = [f"Direct: {dd}", f"Shared: {sd}", f"Schools: {len(self.schools)}",
               f"Subs: {len(self.subs)}", f"Boat Caught: {self.boat.caught}",
               "", "Legend:", "🟡 Subs", "🟠 Shared", "🔴 Boat", "", "F11: Full", "ESC: Exit"]
        for i, l in enumerate(txt):
            s.blit(f2.render(l, True, WHI), (20, H - 280 + i * 20))
        return s
    def loop(self):
        while self.run:
            self.events()
            self.update()
            self.sc.blit(self.draw_left(), (0, 0))
            self.sc.blit(self.draw_right(), (GAME_W, 0))
            pygame.draw.line(self.sc, WHI, (GAME_W, 0), (GAME_W, H), 2)
            pygame.display.flip()
            self.cl.tick(FPS)
        pygame.quit()

Game().loop()