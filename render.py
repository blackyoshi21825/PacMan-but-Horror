import math
import msvcrt
import time
import os

class Big3D:
    def __init__(self):
        self.x, self.y, self.z, self.angle, self.pitch = 8, 8, 0, 0, 0
        self.z_velocity = 0
        self.width, self.height = self.get_screen_size()

        self.map = [
            "################",
            "#..............#",
            "#..AAA.....BBB.#",
            "#..AAA.....BBB.#",
            "#..............#",
            "#....CCCC......#",
            "#....CCCC......#",
            "#..............#",
            "#..DDDDDDDDDD..#",
            "#..............#",
            "#.....EEE......#",
            "#.....EEE......#",
            "#..............#",
            "#..............#",
            "#..............#",
            "################"
        ]
        self.screen = None
    
    def get_screen_size(self):
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines - 1
        except:
            return 80, 24
        
    def cast_ray(self, angle):
        x, y = self.x, self.y
        dx, dy = math.cos(angle) * 0.01, math.sin(angle) * 0.01
        dist = 0
        while dist < 12:
            x += dx
            y += dy
            dist += 0.01
            grid_x, grid_y = int(x), int(y)
            if grid_y < 0 or grid_y >= len(self.map) or grid_x < 0 or grid_x >= len(self.map[0]):
                return dist, '#', grid_x, grid_y
            cell = self.map[grid_y][grid_x]
            if cell != '.' and cell != ' ':
                return dist, cell, grid_x, grid_y
        return 12, '#', 0, 0
    
    def get_wall_char(self, col, row, dist, wall_type, grid_x, grid_y):
        brightness = 0.8 / (dist + 0.5)
        
        shadow_factor = abs(math.sin((grid_x - self.x) * 0.5) * math.cos((grid_y - self.y) * 0.3))
        light_angle = math.atan2(grid_y - self.y, grid_x - self.x) - self.angle
        light_intensity = (math.cos(light_angle) + 1) * 0.5
        
        seed = (col * 17 + row * 23 + grid_x * 31 + grid_y * 37 + 
                int(shadow_factor * 127) + int(light_intensity * 83)) % 9973
        
        all_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*+-=.,;:!?~`'|\"^<>_"
        
        return all_chars[seed % len(all_chars)]
    
    def render(self):

        self.width, self.height = self.get_screen_size()

        screen = []
        fov_scale = 0.06 * (80 / self.width)
        
        for col in range(self.width):
            ray_angle = self.angle + (col - self.width//2) * fov_scale
            dist, wall_type, grid_x, grid_y = self.cast_ray(ray_angle)
            
            dist = max(dist, 0.1)
            height = min(int(self.height * 0.8 / dist), self.height)

            horizon = self.height//2 + int(self.z * 2 + self.pitch * self.height * 0.3)
            wall_start = horizon - height//2
            wall_end = horizon + height//2
            
            column = []
            for row in range(self.height):
                if row < wall_start:
                    if row < self.height * 0.2: column.append(' ')
                    else: column.append('.')
                elif row > wall_end:
                    if row > self.height * 0.8: column.append('_')
                    else: column.append(',')
                else:
                    column.append(self.get_wall_char(col, row, dist, wall_type, grid_x, grid_y))
            screen.append(column)

        frame = '\033[H'
        for row in range(self.height):
            frame += ''.join(screen[col][row] for col in range(self.width)) + '\n'
        frame += f"Pos: ({self.x:.1f},{self.y:.1f},{self.z:.1f}) Angle: {math.degrees(self.angle):.0f}° Pitch: {math.degrees(self.pitch):.0f}° | WASD=move SPACE=jump EQ=look↕ X=quit"
        print(frame, end='', flush=True)

    
    def run(self):
        print('\033[2J\033[H')
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode().lower()
                if key == 'x': break
                elif key == 'w':
                    nx = self.x + math.cos(self.angle) * 0.4
                    ny = self.y + math.sin(self.angle) * 0.4
                    if self.map[int(ny)][int(nx)] == '.': 
                        self.x, self.y = nx, ny
                elif key == 's':
                    nx = self.x - math.cos(self.angle) * 0.4
                    ny = self.y - math.sin(self.angle) * 0.4
                    if self.map[int(ny)][int(nx)] == '.': 
                        self.x, self.y = nx, ny
                elif key == 'a': self.angle -= 0.25
                elif key == 'd': self.angle += 0.25
                elif key == ' ': 
                    if self.z <= 0: self.z_velocity = 1.5
                elif key == 'e': self.pitch = max(-1.2, self.pitch - 0.2)
                elif key == 'q': self.pitch = min(1.2, self.pitch + 0.2)
            

            self.z += self.z_velocity
            self.z_velocity -= 0.3
            if self.z < 0:
                self.z = 0
                self.z_velocity = 0
            
            self.render()
            
            time.sleep(0.03)

Big3D().run()