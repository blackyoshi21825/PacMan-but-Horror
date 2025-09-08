import math
import msvcrt
import time
import os

class Big3D:
    def __init__(self):
        self.x, self.y, self.z, self.angle, self.pitch = 8, 8, 0, 0, 0
        self.z_velocity = 0
        self.width, self.height = self.get_screen_size()
        
        # NPCs: [x, y, angle, move_timer]
        self.npcs = [
            [3, 3, 0, 0],
            [12, 5, math.pi, 0],
            [6, 12, math.pi/2, 0]
        ]

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
        self.frame_count = 0
    
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
        npc_hit = None
        
        while dist < 12:
            x += dx
            y += dy
            dist += 0.01
            
            # Check NPC collision first
            for npc in self.npcs:
                npc_dist = math.sqrt((x - npc[0])**2 + (y - npc[1])**2)
                if npc_dist < 0.3:
                    return dist, 'N', int(npc[0]), int(npc[1])
            
            grid_x, grid_y = int(x), int(y)
            if grid_y < 0 or grid_y >= len(self.map) or grid_x < 0 or grid_x >= len(self.map[0]):
                return dist, '#', grid_x, grid_y
            cell = self.map[grid_y][grid_x]
            if cell != '.' and cell != ' ':
                return dist, cell, grid_x, grid_y
        return 12, '#', 0, 0
    
    def get_wall_char(self, col, row, dist, wall_type, grid_x, grid_y, wall_start, wall_end):
        # Special handling for NPCs - single character
        if wall_type == 'N':
            # Use a single character that looks human-like
            char = '@' if (self.frame_count//20) % 2 == 0 else '&'
            return f"\033[38;5;208m{char}\033[0m"
        
        # Regular wall rendering
        brightness = 0.8 / (dist + 0.5)
        shadow_factor = abs(math.sin((grid_x - self.x) * 0.5) * math.cos((grid_y - self.y) * 0.3))
        light_angle = math.atan2(grid_y - self.y, grid_x - self.x) - self.angle
        light_intensity = (math.cos(light_angle) + 1) * 0.5
        
        seed = (col * 17 + row * 23 + grid_x * 31 + grid_y * 37 + 
                int(shadow_factor * 127) + int(light_intensity * 83)) % 9973
        
        all_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%&*+-=.,;:!?~`'|\"^<>_"
        char = all_chars[seed % len(all_chars)]
        
        colors = {'A': '31', 'B': '32', 'C': '33', 'D': '34', 'E': '35', '#': '37'}
        base_color = colors.get(wall_type, '37')
        
        if brightness > 0.8: intensity = f"1;{base_color}"
        elif brightness > 0.6: intensity = base_color
        elif brightness > 0.4: intensity = f"2;{base_color}"
        else: intensity = f"2;90"
        
        return f"\033[{intensity}m{char}\033[0m"
    
    def update_npcs(self):
        for npc in self.npcs:
            npc[3] += 1
            if npc[3] > 60:  # Move every 60 frames
                npc[3] = 0
                # Try to move forward
                nx = npc[0] + math.cos(npc[2]) * 0.5
                ny = npc[1] + math.sin(npc[2]) * 0.5
                
                # Check if new position is valid
                if (0 < nx < len(self.map[0])-1 and 0 < ny < len(self.map)-1 and 
                    self.map[int(ny)][int(nx)] == '.'):
                    npc[0], npc[1] = nx, ny
                else:
                    # Turn randomly if blocked
                    npc[2] += (hash(str(npc)) % 3 - 1) * 0.8
    
    def render(self):
        self.frame_count += 1
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
                    if row < self.height * 0.2: 
                        # Ceiling
                        ceiling_dist = (self.height * 0.2 - row) / (self.height * 0.2) * 8
                        ceiling_char = '#' if (col + row) % 3 == 0 else '-'
                        brightness = 0.3 / (ceiling_dist + 1)
                        intensity = "2;34" if brightness < 0.1 else "34"
                        column.append(f"\033[{intensity}m{ceiling_char}\033[0m")
                    else:
                        # Sky with same pattern as ceiling
                        sky_char = '#' if (col + row) % 3 == 0 else '-'
                        sky_dist = (row - self.height * 0.2) / (self.height * 0.6) * 4
                        brightness = 0.2 / (sky_dist + 1)
                        intensity = "2;34" if brightness < 0.1 else "34"
                        column.append(f"\033[{intensity}m{sky_char}\033[0m")
                elif row > wall_end:
                    if row > self.height * 0.8: column.append('_')
                    else: column.append(',')
                else:
                    column.append(self.get_wall_char(col, row, dist, wall_type, grid_x, grid_y, wall_start, wall_end))
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
                    nx = self.x + math.cos(self.angle) * 0.2
                    ny = self.y + math.sin(self.angle) * 0.2
                    if self.map[int(ny)][int(nx)] == '.': 
                        self.x, self.y = nx, ny
                elif key == 's':
                    nx = self.x - math.cos(self.angle) * 0.2
                    ny = self.y - math.sin(self.angle) * 0.2
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
            
            self.update_npcs()
            self.render()
            
            time.sleep(0.03)

Big3D().run()