import math
import msvcrt
import time
import os

class Big3D:
    def __init__(self):
        self.x, self.y, self.z, self.angle, self.pitch = 1.5, 1.5, 0, 0, 0
        self.z_velocity = 0
        self.width, self.height = self.get_screen_size()
        # NPCs deleted as requested
        self.npcs = []
        self.map = [
            "##########",
            "#..AAA...#",
            "#..AAA...#",
            "#........#",
            "#.CCCC.BB#",
            "#.CCCC.BB#",
            "#........#",
            "#..EEE...#",
            "#..EEE...#",
            "##########"
        ]
        self.screen = None
        self.frame_count = 0
        self.textures = self.generate_textures()

    def get_screen_size(self):
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines - 1
        except:
            return 80, 24

    def generate_textures(self):
        import random
        textures = {}
        char_grad = " .-,=+*#%@"
        
        for wall_type in ['A', 'B', 'C', 'D', 'E', '#']:
            texture = []
            for y in range(32):
                row = []
                for x in range(32):
                    if wall_type == 'A':  # Red brick
                        char_val = 12 - 8 * ((y % 6 == 0) or ((x + 4 * (y // 6)) % 16 == 0)) + random.randint(0, 1)
                        color = 31 if ((y % 6 == 0) or ((x + 4 * (y // 6)) % 16 == 0)) else 91
                    elif wall_type == 'B':  # Green large brick
                        char_val = 8 - 4 * ((y % 31 == 0) or ((x + 4 * (y // 31)) % 16 == 0)) + random.randint(0, 1)
                        color = 32 if ((y % 31 == 0) or ((x + 4 * (y // 31)) % 16 == 0)) else 92
                    elif wall_type == 'C':  # Yellow stone
                        char_val = 8 - 4 * ((y % 8 == 0) or (x % 8 == 0)) + random.randint(0, 1)
                        color = 33 if ((y % 8 == 0) or (x % 8 == 0)) else 93
                    elif wall_type == 'D':  # Blue pattern
                        char_val = 10 - 6 * ((y % 4 == 0) or (x % 4 == 0)) + random.randint(0, 1)
                        color = 34 if ((y % 4 == 0) or (x % 4 == 0)) else 94
                    elif wall_type == 'E':  # Magenta cross pattern
                        char_val = 9 - 5 * ((y % 16 == 8) or (x % 16 == 8)) + random.randint(0, 1)
                        color = 35 if ((y % 16 == 8) or (x % 16 == 8)) else 95
                    else:  # Default wall
                        char_val = 7 - 3 * ((y % 2 == 0) and (x % 2 == 0)) + random.randint(0, 1)
                        color = 37
                    
                    char_val = max(0, min(9, char_val))
                    char = char_grad[char_val]
                    row.append((char, color))
                texture.append(row)
            textures[wall_type] = texture
        return textures

    def update_npcs(self):
        # No NPCs to update
        pass

    def cast_ray(self, angle):
        x, y = self.x, self.y
        dx, dy = math.sin(angle) * 0.01, math.cos(angle) * 0.01
        dist = 0
        hit_vertical = False
        while dist < 12:
            prev_x, prev_y = x, y
            x += dx
            y += dy
            dist += 0.01
            grid_x, grid_y = int(x), int(y)
            if grid_y < 0 or grid_y >= len(self.map) or grid_x < 0 or grid_x >= len(self.map[0]):
                return dist, '#', grid_x, grid_y, 0, hit_vertical
            cell = self.map[grid_y][grid_x]
            if cell != '.' and cell != ' ':
                # Calculate texture coordinate
                if abs(x - prev_x) > abs(y - prev_y):
                    tex_coord = int((y % 1) * 32)
                    hit_vertical = True
                else:
                    tex_coord = int((x % 1) * 32)
                    hit_vertical = False
                return dist, cell, grid_x, grid_y, tex_coord, hit_vertical
        return 12, '#', 0, 0, 0, False

    def render(self):
        self.frame_count += 1
        self.width, self.height = self.get_screen_size()
        fov = math.pi / 4.0
        screen = [[" " for _ in range(self.height)] for _ in range(self.width)]

        # Render walls and floor/ceiling
        for col in range(self.width):
            ray_angle = self.angle - fov / 2.0 + (col / self.width) * fov
            dist, wall_type, grid_x, grid_y, tex_coord, hit_vertical = self.cast_ray(ray_angle)
            dist = max(dist, 0.1)
            height = min(int(self.height * 0.8 / dist), self.height)
            horizon = self.height // 2 + int(self.z * 2 + self.pitch * self.height * 0.3)
            wall_start = horizon - height // 2
            wall_end = horizon + height // 2

            for row in range(self.height):
                if row < wall_start:
                    if row < self.height * 0.2:
                        ceiling_dist = (self.height * 0.2 - row) / (self.height * 0.2) * 8
                        ceiling_char = '#' if (col + row) % 3 == 0 else '-'
                        brightness = 0.3 / (ceiling_dist + 1)
                        intensity = "2;34" if brightness < 0.1 else "34"
                        screen[col][row] = f"\033[{intensity}m{ceiling_char}\033[0m"
                    else:
                        sky_char = '#' if (col + row) % 3 == 0 else '-'
                        sky_dist = (row - self.height * 0.2) / (self.height * 0.6) * 4
                        brightness = 0.2 / (sky_dist + 1)
                        intensity = "2;34" if brightness < 0.1 else "34"
                        screen[col][row] = f"\033[{intensity}m{sky_char}\033[0m"
                elif row > wall_end:
                    if row > self.height * 0.8:
                        screen[col][row] = '_'
                    else:
                        screen[col][row] = ','
                else:
                    screen[col][row] = self.get_textured_wall_char(col, row, dist, wall_type, tex_coord, hit_vertical, wall_start, wall_end, height)

        # No NPC billboard rendering

        frame = '\033[H'
        for row in range(self.height):
            frame += ''.join(screen[col][row] for col in range(self.width)) + '\n'
        frame += f"Pos: ({self.x:.1f},{self.y:.1f},{self.z:.1f}) Angle: {math.degrees(self.angle):.0f}° Pitch: {math.degrees(self.pitch):.0f}° | WASD=move SPACE=jump EQ=look↕ X=quit"
        print(frame, end='', flush=True)

    def get_textured_wall_char(self, col, row, dist, wall_type, tex_coord, hit_vertical, wall_start, wall_end, height):
        # Calculate texture Y coordinate
        wall_pos = (row - wall_start) / max(1, wall_end - wall_start)
        tex_y = int(wall_pos * 31) % 32
        tex_x = tex_coord % 32
        
        # Get texture character and color
        if wall_type in self.textures:
            char, color = self.textures[wall_type][tex_y][tex_x]
        else:
            char, color = '#', 37
        
        # Apply lighting (from C++ implementation)
        brightness = 5.0 / self.height * height  # Proportional to wall height
        brightness = brightness + 0.2  # Add base brightness for contrast
        if not hit_vertical:  # North/south walls are darker (Wolfenstein style)
            brightness *= 0.5
        else:
            brightness *= 1.0  # East/west walls are brighter
        
        # Distance-based lighting falloff
        brightness *= 0.8 / (dist + 0.5)
        
        # Adjust brightness
        if brightness > 0.8: intensity = f"1;{color}"
        elif brightness > 0.6: intensity = str(color)
        elif brightness > 0.4: intensity = f"2;{color}"
        else: intensity = "2;90"
        
        return f"\033[{intensity}m{char}\033[0m"

    def run(self):
        print('\033[2J\033[H')
        MOVE_SPEED = 0.04  # Slower movement
        ROTATE_SPEED = 0.06  # Slower rotation/sensitivity
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode().lower()
                if key == 'x': break
                elif key == 'w':
                    nx = self.x + math.sin(self.angle) * MOVE_SPEED
                    ny = self.y + math.cos(self.angle) * MOVE_SPEED
                    if self.map[int(ny)][int(nx)] == '.':
                        self.x, self.y = nx, ny
                elif key == 's':
                    nx = self.x - math.sin(self.angle) * MOVE_SPEED
                    ny = self.y - math.cos(self.angle) * MOVE_SPEED
                    if self.map[int(ny)][int(nx)] == '.':
                        self.x, self.y = nx, ny
                elif key == 'a': self.angle -= ROTATE_SPEED
                elif key == 'd': self.angle += ROTATE_SPEED
                elif key == ' ':
                    if self.z <= 0: self.z_velocity = 1.5
                elif key == 'e': self.pitch = max(-1.2, self.pitch - 0.2)
                elif key == 'q': self.pitch = min(1.2, self.pitch + 0.2)
            self.z += self.z_velocity
            self.z_velocity -= 0.3
            if self.z < 0:
                self.z = 0
                self.z_velocity = 0
            self.update_npcs()
            self.render()
            time.sleep(0.03)

if __name__ == "__main__":
    Big3D().run()