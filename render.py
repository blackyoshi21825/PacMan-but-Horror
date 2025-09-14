import math
import msvcrt
import time
import os
import ctypes
from ctypes import wintypes

class Big3D:
    def __init__(self):
        self.x, self.y, self.z, self.angle, self.pitch = 1.5, 1.5, 0, 0, 0
        self.z_velocity = 0
        self.width, self.height = self.get_screen_size()
        self.enemies = []
        self.mouse_sensitivity = 0.003
        self.hp = 100
        self.damage_timer = 0
        self.game_over = False
        self.game_won = False
        self.health_pickups = []
        self.start_time = time.time()
        self.gate_open = False
        self.gate_x, self.gate_y = 18.5, 20.5
        self.init_mouse()
        self.map = [
            "######################",
            "#..AAA......AAA.....##",
            "#..AAA......AAA.....##",
            "#...................##",
            "#.CCCC.BB....CCCC.BB##",
            "#.CCCC.BB....CCCC.BB##",
            "#...................##",
            "#..EEE......EEE.....##",
            "#..EEE......EEE.....##",
            "#...................##",
            "##.................###",
            "##.AAAA.......AAAA.###",
            "##.AAAA.......AAAA.###",
            "##.................###",
            "##.BBB.CCC.DDD.EEE.###",
            "##.BBB.CCC.DDD.EEE.###",
            "##.................###",
            "##.................###",
            "##.AAA.BBB.CCC.DDD.###",
            "##.AAA.BBB.CCC.DDD.###",
            "##.................###",
            "######################"
        ]
        self.screen = None
        self.frame_count = 0
        self.textures = self.generate_textures()
        self.sprites = self.generate_sprites()
        self.depth_map = [[0 for _ in range(self.height)] for _ in range(self.width)]
        self.path_map = [[0 for _ in range(len(self.map[0]))] for _ in range(len(self.map))]
        
        # Scary lighting system
        self.light_global = 0.005  # Much darker
        self.light_falloff = 1.0
        self.light_flashlight = 0.8
        self.battery = 1.0
        self.torch_enabled = True
        self.torch_flicker = 1.0
        self.flashlight_coeff = self.calculate_flashlight_coeff()
        
        self.init_enemies()
        self.init_health_pickups()

    def init_mouse(self):
        try:
            user32 = ctypes.windll.user32
            point = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(point))
            self.last_x, self.last_y = point.x, point.y
        except:
            self.last_x, self.last_y = 0, 0

    def handle_mouse(self):
        try:
            user32 = ctypes.windll.user32
            point = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(point))
            
            dx = point.x - self.last_x
            dy = point.y - self.last_y
            
            if abs(dx) > 0 or abs(dy) > 0:
                self.angle += dx * self.mouse_sensitivity
                self.pitch = max(-1.2, min(1.2, self.pitch - dy * self.mouse_sensitivity * 0.3))
                self.last_x, self.last_y = point.x, point.y
        except:
            pass

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
        
        # Brick color variations: red, maroon, brown
        brick_colors = [31, 91, 33]  # red, bright red, brown/yellow
        mortar_colors = [90, 37, 33]  # dark gray, white, brown
        
        for wall_type in ['A', 'B', 'C', 'D', 'E', '#']:
            texture = []
            for y in range(32):
                row = []
                for x in range(32):
                    # Brick pattern detection
                    is_mortar = (y % 6 == 0) or ((x + 4 * (y // 6)) % 16 == 0)
                    char_val = 12 - 8 * is_mortar + random.randint(0, 1)
                    
                    if is_mortar:
                        # Mortar lines - use gray/white colors
                        color = random.choice(mortar_colors)
                    else:
                        # Brick areas - use varied brick colors
                        color = random.choice(brick_colors)
                    
                    char_val = max(0, min(9, char_val))
                    char = char_grad[char_val]
                    row.append((char, color))
                texture.append(row)
            textures[wall_type] = texture
        return textures

    def generate_sprites(self):
        sprites = {}
        char_grad = " .-,=+*#%@"
        
        # Generate four Pac-Man ghosts with different colors
        ghost_colors = [91, 95, 96, 93]  # Red, Magenta, Cyan, Yellow
        
        for ghost_type in range(4):
            sprite = []
            for y in range(32):
                row = []
                for x in range(32):
                    dist = (x - 16) ** 2 + (y - 16) ** 2
                    char, color, alpha = ' ', 0, 0
                    
                    # Ghost body
                    if dist < 225 or (y > 16 and x > 1 and x < 31 and y < 32 - x % 4):
                        char = char_grad[6]
                        color = ghost_colors[ghost_type]
                        alpha = 1
                    
                    # Eyes
                    eye_dist1 = (x - 11) ** 2 + (y - 12) ** 2
                    eye_dist2 = (x - 21) ** 2 + (y - 12) ** 2
                    if eye_dist1 < 16 or eye_dist2 < 16:
                        char = char_grad[8]
                        color = 97  # White
                        alpha = 1
                    if eye_dist1 < 2 or eye_dist2 < 2:
                        char = char_grad[9]
                        color = 30  # Black
                        alpha = 1
                    
                    row.append((char, color, alpha))
                sprite.append(row)
            sprites[ghost_type] = sprite
        
        # Generate health pickup sprite (green pill)
        sprite = []
        for y in range(32):
            row = []
            for x in range(32):
                dist = (x - 16) ** 2 + (y - 16) ** 2
                char, color, alpha = ' ', 0, 0
                
                # Pill shape - oval
                if dist < 180 and abs(x - 16) < 12:
                    char = char_grad[7]
                    color = 92  # Bright green
                    alpha = 1
                # Highlight
                if dist < 100 and abs(x - 16) < 8:
                    char = char_grad[8]
                    color = 97  # White highlight
                    alpha = 1
                
                row.append((char, color, alpha))
            sprite.append(row)
        sprites['health'] = sprite
        
        # Generate gate sprite (golden door)
        sprite = []
        for y in range(32):
            row = []
            for x in range(32):
                char, color, alpha = ' ', 0, 0
                
                # Door frame
                if x < 4 or x > 28 or y > 28:
                    char = char_grad[8]
                    color = 93  # Yellow/gold
                    alpha = 1
                # Door panels
                elif 8 < x < 24 and 4 < y < 28:
                    char = char_grad[6]
                    color = 93  # Yellow/gold
                    alpha = 1
                # Door handle
                elif 20 < x < 24 and 14 < y < 18:
                    char = char_grad[9]
                    color = 97  # White
                    alpha = 1
                
                row.append((char, color, alpha))
            sprite.append(row)
        sprites['gate'] = sprite
        return sprites

    def init_enemies(self):
        # Add four ghosts like in Pac-Man
        ghost_positions = [(2.5, 2.5), (7.5, 2.5), (2.5, 7.5), (7.5, 7.5)]
        
        for i in range(4):
            x, y = ghost_positions[i]
            enemy = {
                'x': x, 'y': y, 'z': 0,
                'vx': 0, 'vy': 0, 'vz': 0,
                'type': i, 'enabled': True
            }
            self.enemies.append(enemy)
    
    def init_health_pickups(self):
        # Place health pickups at specific locations
        pickup_positions = [(3.5, 3.5), (10.5, 3.5), (3.5, 10.5), (10.5, 10.5)]
        for x, y in pickup_positions:
            if self.map[int(y)][int(x)] == '.':
                self.health_pickups.append({'x': x, 'y': y, 'active': True})
                print(f"Health pickup at {x}, {y}")

    def update_pathfinding(self):
        # Clear path map
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                self.path_map[x][y] = 0
        
        # Set player position to highest value
        px, py = int(self.x), int(self.y)
        if 0 <= px < len(self.map) and 0 <= py < len(self.map[0]):
            self.path_map[px][py] = len(self.map)
        
        # Propagate values outward from player
        for i in range(len(self.map), 0, -1):
            for x in range(1, len(self.map) - 1):
                for y in range(1, len(self.map[0]) - 1):
                    if self.path_map[x][y] == i:
                        # Set neighboring empty tiles to i-1
                        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                            nx, ny = x + dx, y + dy
                            if (self.path_map[nx][ny] == 0 and 
                                self.map[nx][ny] == '.'):
                                self.path_map[nx][ny] = i - 1

    def update_enemies(self):
        import random
        import math
        
        self.update_pathfinding()
        
        for enemy in self.enemies:
            if not enemy['enabled']:
                continue
            
            # Pathfinding AI - move toward highest nearby value
            max_rating = 0
            best_dir = 0
            
            for direction in range(8):
                angle = direction * math.pi / 4
                nx = enemy['x'] + 1.4 * math.cos(angle)
                ny = enemy['y'] + 1.4 * math.sin(angle)
                
                if (0 <= int(nx) < len(self.map) and 
                    0 <= int(ny) < len(self.map[0]) and
                    self.map[int(nx)][int(ny)] == '.'):
                    rating = self.path_map[int(nx)][int(ny)]
                    
                    # Add ghost personality quirks
                    if enemy['type'] == 3 and random.randint(0, 7) == 0:  # Yellow ghost randomness
                        rating += random.randint(0, 2)
                    
                    if rating > max_rating:
                        max_rating = rating
                        best_dir = direction
            
            # Move in best direction
            if max_rating > 0:
                nx = math.cos(best_dir * math.pi / 4)
                ny = math.sin(best_dir * math.pi / 4)
                enemy['vx'] += 0.001 * nx
                enemy['vy'] += 0.001 * ny
            
            # Random movement occasionally
            if random.randint(0, 15) == 0:
                enemy['vx'] += 0.01 * (random.randint(0, 2) - 1)
                enemy['vy'] += 0.01 * (random.randint(0, 2) - 1)
            
            # Update position with collision
            new_x = enemy['x'] + enemy['vx']
            new_y = enemy['y'] + enemy['vy']
            
            if (0 < new_x < len(self.map[0]) - 1 and 
                0 < new_y < len(self.map) - 1 and
                self.map[int(new_y)][int(new_x)] == '.'):
                enemy['x'] = new_x
                enemy['y'] = new_y
            else:
                enemy['vx'] = -enemy['vx']
                enemy['vy'] = -enemy['vy']
            
            # Apply friction
            enemy['vx'] *= 0.97
            enemy['vy'] *= 0.97

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

        # Initialize depth map
        self.depth_map = [[12.0 for _ in range(self.height)] for _ in range(self.width)]
        
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
                        ceiling_char = '#' if (col + row) % 3 == 0 else '-'
                        brightness = 0
                        if self.torch_enabled:
                            flashlight_idx = col + row * self.width
                            if flashlight_idx < len(self.flashlight_coeff):
                                brightness = self.battery * self.light_flashlight * self.flashlight_coeff[flashlight_idx] * 0.1
                        brightness = max(0, min(90, brightness))
                        if brightness > 20: intensity = "34"
                        elif brightness > 5: intensity = "2;34"
                        else: intensity = "2;30"
                        screen[col][row] = f"\033[{intensity}m{ceiling_char}\033[0m"
                    else:
                        sky_char = '#' if (col + row) % 3 == 0 else '-'
                        brightness = 0
                        if self.torch_enabled:
                            flashlight_idx = col + row * self.width
                            if flashlight_idx < len(self.flashlight_coeff):
                                brightness = self.battery * self.light_flashlight * self.flashlight_coeff[flashlight_idx] * 0.1
                        brightness = max(0, min(90, brightness))
                        if brightness > 20: intensity = "34"
                        elif brightness > 5: intensity = "2;34"
                        else: intensity = "2;30"
                        screen[col][row] = f"\033[{intensity}m{sky_char}\033[0m"
                elif row > wall_end:
                    floor_char = '_' if row > self.height * 0.8 else ','
                    brightness = 0
                    if self.torch_enabled:
                        flashlight_idx = col + row * self.width
                        if flashlight_idx < len(self.flashlight_coeff):
                            brightness = self.battery * self.light_flashlight * self.flashlight_coeff[flashlight_idx] * 0.1
                    brightness = max(0, min(90, brightness))
                    if brightness > 20: intensity = "37"
                    elif brightness > 5: intensity = "2;37"
                    else: intensity = "2;30"
                    screen[col][row] = f"\033[{intensity}m{floor_char}\033[0m"
                else:
                    screen[col][row] = self.get_textured_wall_char(col, row, dist, wall_type, tex_coord, hit_vertical, wall_start, wall_end, height)
                
                # Update depth map for sprite rendering
                if wall_start <= row <= wall_end:
                    self.depth_map[col][row] = dist

        # Render sprites (enemies, health pickups, and gate)
        self.draw_enemies(screen, fov)
        self.draw_health_pickups(screen, fov)
        self.draw_gate(screen, fov)
        
        # Draw minimap
        self.draw_minimap(screen)
        
        # Apply damage effect - turn all characters red
        if self.damage_timer > 0:
            for col in range(self.width):
                for row in range(self.height):
                    if '\033[' in screen[col][row]:
                        char = screen[col][row].split('m')[1][0] if len(screen[col][row].split('m')) > 1 else screen[col][row][-1]
                        screen[col][row] = f"\033[91m{char}\033[0m"
                    else:
                        screen[col][row] = f"\033[91m{screen[col][row]}\033[0m"
        
        # Draw game over overlay - bigger text
        if self.game_over:
            center_x, center_y = self.width // 2, self.height // 2
            game_over_lines = [
                "  ####    ###   #   # #####    ####  #   # ##### ####  ",
                " #       #   #  ## ## #       #    #  # #  #     #   # ",
                " #  ###  #####  # # # #####   #    #  # #  ##### ####  ",
                " #    #  #   #  #   # #       #    #   #   #     #   # ",
                "  ####   #   #  #   # #####    ####    #   ##### #   # "
            ]
            for line_idx, line in enumerate(game_over_lines):
                y = center_y - 2 + line_idx
                if 0 <= y < self.height:
                    for char_idx, char in enumerate(line):
                        x = center_x - len(line) // 2 + char_idx
                        if 0 <= x < self.width:
                            screen[x][y] = f"\033[1;91m{char}\033[0m"
        
        # Draw win overlay
        if self.game_won:
            center_x, center_y = self.width // 2, self.height // 2
            win_lines = [
                " #   #  ####  #   #   #   #  ####  #   # # ",
                " #   # #    # #   #   #   # #    # ##  # # ",
                " #   # #    # #   #   # # # #    # # # # # ",
                " # # # #    # #   #   # # # #    # #  ## # ",
                "  # #   ####   ###     # #   ####  #   # # "
            ]
            for line_idx, line in enumerate(win_lines):
                y = center_y - 2 + line_idx
                if 0 <= y < self.height:
                    for char_idx, char in enumerate(line):
                        x = center_x - len(line) // 2 + char_idx
                        if 0 <= x < self.width:
                            screen[x][y] = f"\033[1;97m{char}\033[0m"

        frame = '\033[H'
        for row in range(self.height):
            frame += ''.join(screen[col][row] for col in range(self.width)) + '\n'
        elapsed = time.time() - self.start_time
        gate_status = "OPEN" if self.gate_open else f"Opens in {max(0, 120-int(elapsed))}s"
        frame += f"HP: {self.hp} | Time: {int(elapsed)}s | Gate: {gate_status} | Battery: {int(self.battery*100)}% | WASD=move SPACE=jump EQ=look↕ F=flashlight X=quit"
        print(frame, end='', flush=True)

    def calculate_flashlight_coeff(self):
        """Pre-calculate torch brightness coefficients"""
        coeff = []
        for y in range(self.height):
            for x in range(self.width):
                lghtx = 4.0 * (x - self.width/2) / self.width  # Tighter beam
                lghty = 4.0 * (y - self.height/2) / self.height
                lght = math.exp(-lghtx*lghtx) * math.exp(-lghty*lghty)
                coeff.append(600.0 * lght * (1 + 0.3 * ((abs(y)%2) + (abs(x)%2))))
        return coeff

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
        
        # Flashlight-only lighting system
        brightness = 0
        
        # Only add flashlight if enabled
        if self.torch_enabled:
            flashlight_idx = col + row * self.width
            if flashlight_idx < len(self.flashlight_coeff):
                brightness = self.battery * self.light_flashlight * self.flashlight_coeff[flashlight_idx] * height / self.height * self.torch_flicker
                # Wall normal lighting (vertical walls brighter)
                if hit_vertical:
                    brightness *= 1.0
                else:
                    brightness *= 0.7
        
        # Apply brightness to character
        brightness = max(0, min(90, brightness))
        
        # Scarier color intensity - much darker thresholds
        if brightness > 40: intensity = f"1;{color}"
        elif brightness > 15: intensity = str(color)
        elif brightness > 3: intensity = f"2;{color}"
        else: intensity = "2;30"  # Almost black
        
        return f"\033[{intensity}m{char}\033[0m"

    def draw_enemies(self, screen, fov):
        for enemy in self.enemies:
            if not enemy['enabled']:
                continue
            
            # Calculate relative position to player
            dx = enemy['x'] - self.x
            dy = enemy['y'] - self.y
            
            # Calculate angle to enemy relative to player's view
            enemy_angle = math.atan2(dx, dy)
            angle_diff = enemy_angle - self.angle
            
            # Normalize angle difference to [-pi, pi]
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Check if enemy is in field of view
            if abs(angle_diff) > fov / 2:
                continue
            
            # Calculate distance and screen position
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 0.1:
                continue
            
            # Calculate screen column
            screen_x = int(self.width / 2 + (angle_diff / fov) * self.width)
            if screen_x < 0 or screen_x >= self.width:
                continue
            
            # Calculate sprite size based on distance
            sprite_size = max(1, int(self.height * 0.5 / distance))
            if sprite_size > 64:  # Limit max size
                continue
            
            # Calculate vertical position
            horizon = self.height // 2 + int(self.z * 2 + self.pitch * self.height * 0.3)
            sprite_y = horizon - sprite_size // 2
            
            # Draw sprite
            self.draw_sprite(screen, screen_x, sprite_y, sprite_size, enemy['type'], distance)

    def draw_sprite(self, screen, center_x, center_y, size, sprite_type, distance):
        if sprite_type not in self.sprites:
            return
        
        sprite = self.sprites[sprite_type]
        
        for y in range(size):
            for x in range(size):
                screen_x = center_x - size // 2 + x
                screen_y = center_y + y
                
                # Check bounds
                if (screen_x < 0 or screen_x >= self.width or 
                    screen_y < 0 or screen_y >= self.height):
                    continue
                
                # Check depth (sprite behind wall?)
                if self.depth_map[screen_x][screen_y] < distance:
                    continue
                
                # Get sprite pixel
                sprite_x = int((x / size) * 32)
                sprite_y = int((y / size) * 32)
                char, color, alpha = sprite[sprite_y][sprite_x]
                
                if alpha > 0:  # Only draw if not transparent
                    # Only visible with flashlight
                    brightness = 0
                    if self.torch_enabled:
                        flashlight_idx = screen_x + screen_y * self.width
                        if flashlight_idx < len(self.flashlight_coeff):
                            brightness = self.battery * self.light_flashlight * self.flashlight_coeff[flashlight_idx] / (distance + 0.5)
                    
                    if brightness > 0.3:
                        if brightness > 0.8:
                            intensity = f"1;{color}"
                        elif brightness > 0.4:
                            intensity = str(color)
                        else:
                            intensity = f"2;{color}"
                        
                        screen[screen_x][screen_y] = f"\033[{intensity}m{char}\033[0m"
                        # Update depth map
                        self.depth_map[screen_x][screen_y] = distance

    def draw_minimap(self, screen):
        # Draw minimap in top-left corner
        map_size = len(self.map)
        for x in range(min(map_size, self.width)):
            for y in range(min(map_size, self.height)):
                if x < len(self.map) and y < len(self.map[0]):
                    if self.map[y][x] != '.':
                        screen[x][y] = '\033[37m#\033[0m'  # White walls
                    else:
                        screen[x][y] = '\033[30m \033[0m'  # Black empty space
        
        # Draw player
        px, py = int(self.x), int(self.y)
        if 0 <= px < self.width and 0 <= py < self.height:
            screen[px][py] = '\033[97m@\033[0m'  # Bright white player
        
        # Draw ghosts
        ghost_colors = ['91', '95', '96', '93']  # Red, Magenta, Cyan, Yellow
        for enemy in self.enemies:
            if enemy['enabled']:
                ex, ey = int(enemy['x']), int(enemy['y'])
                if 0 <= ex < self.width and 0 <= ey < self.height:
                    color = ghost_colors[enemy['type']]
                    screen[ex][ey] = f'\033[{color}m*\033[0m'
        
        # Draw health pickups on minimap (after ghosts)
        for pickup in self.health_pickups:
            if pickup['active']:
                px, py = int(pickup['x']), int(pickup['y'])
                if 0 <= px < self.width and 0 <= py < self.height:
                    screen[px][py] = '\033[92m+\033[0m'  # Green plus
        
        # Draw gate on minimap
        if self.gate_open:
            gx, gy = int(self.gate_x), int(self.gate_y)
            if 0 <= gx < self.width and 0 <= gy < self.height:
                screen[gx][gy] = '\033[93mG\033[0m'  # Yellow gate
        


    def check_enemy_collision(self):
        for enemy in self.enemies:
            if not enemy['enabled']:
                continue
            dx = enemy['x'] - self.x
            dy = enemy['y'] - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 0.5 and self.hp > 0:
                self.hp = max(0, self.hp - 1)
                self.damage_timer = 32
                if self.hp <= 0:
                    self.game_over = True
    
    def draw_health_pickups(self, screen, fov):
        for pickup in self.health_pickups:
            if not pickup['active']:
                continue
            
            # Calculate relative position to player
            dx = pickup['x'] - self.x
            dy = pickup['y'] - self.y
            
            # Calculate angle to pickup relative to player's view
            pickup_angle = math.atan2(dx, dy)
            angle_diff = pickup_angle - self.angle
            
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Check if pickup is in field of view
            if abs(angle_diff) > fov / 2:
                continue
            
            # Calculate distance and screen position
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 0.1:
                continue
            
            # Calculate screen column
            screen_x = int(self.width / 2 + (angle_diff / fov) * self.width)
            if screen_x < 0 or screen_x >= self.width:
                continue
            
            # Calculate sprite size based on distance
            sprite_size = max(1, int(self.height * 0.3 / distance))
            if sprite_size > 32:
                continue
            
            # Calculate vertical position
            horizon = self.height // 2 + int(self.z * 2 + self.pitch * self.height * 0.3)
            sprite_y = horizon - sprite_size // 2
            
            # Draw health pickup sprite
            self.draw_pickup_sprite(screen, screen_x, sprite_y, sprite_size, distance)
    
    def draw_pickup_sprite(self, screen, center_x, center_y, size, distance):
        sprite = self.sprites['health']
        
        for y in range(size):
            for x in range(size):
                screen_x = center_x - size // 2 + x
                screen_y = center_y + y
                
                # Check bounds
                if (screen_x < 0 or screen_x >= self.width or 
                    screen_y < 0 or screen_y >= self.height):
                    continue
                
                # Check depth
                if self.depth_map[screen_x][screen_y] < distance:
                    continue
                
                # Get sprite pixel
                sprite_x = int((x / size) * 32)
                sprite_y = int((y / size) * 32)
                char, color, alpha = sprite[sprite_y][sprite_x]
                
                if alpha > 0:
                    brightness = 0
                    if self.torch_enabled:
                        flashlight_idx = screen_x + screen_y * self.width
                        if flashlight_idx < len(self.flashlight_coeff):
                            brightness = self.battery * self.light_flashlight * self.flashlight_coeff[flashlight_idx] / (distance + 0.5)
                    
                    if brightness > 0.2:
                        if brightness > 0.6:
                            intensity = f"1;{color}"
                        else:
                            intensity = str(color)
                        
                        screen[screen_x][screen_y] = f"\033[{intensity}m{char}\033[0m"
                        self.depth_map[screen_x][screen_y] = distance
    
    def check_health_pickup(self):
        for pickup in self.health_pickups:
            if not pickup['active']:
                continue
            dx = pickup['x'] - self.x
            dy = pickup['y'] - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 0.7:
                pickup['active'] = False
                self.hp = min(100, self.hp + 20)

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
                    if self.map[int(ny)][int(nx)] in ['.', 'G']:
                        self.x, self.y = nx, ny
                elif key == 's':
                    nx = self.x - math.sin(self.angle) * MOVE_SPEED
                    ny = self.y - math.cos(self.angle) * MOVE_SPEED
                    if self.map[int(ny)][int(nx)] in ['.', 'G']:
                        self.x, self.y = nx, ny
                elif key == 'a': self.angle -= ROTATE_SPEED
                elif key == 'd': self.angle += ROTATE_SPEED
                elif key == ' ':
                    if self.z <= 0: self.z_velocity = 1.5
                elif key == 'e': self.pitch = max(-1.2, self.pitch - 0.2)
                elif key == 'q': self.pitch = min(1.2, self.pitch + 0.2)
                elif key == 'f': self.torch_enabled = not self.torch_enabled  # Toggle torch
            self.z += self.z_velocity
            self.z_velocity -= 0.3
            if self.z < 0:
                self.z = 0
                self.z_velocity = 0
            
            # Battery drain and scary torch flicker
            if self.torch_enabled:
                self.battery *= 0.9995  # Faster drain
                import random
                # More dramatic flickering
                if random.random() < 0.1:  # Occasional dramatic flicker
                    self.torch_flicker = 0.1 + 0.3 * random.random()
                else:
                    self.torch_flicker = 0.6 + 0.4 * random.random()
            
            if self.damage_timer > 0:
                self.damage_timer -= 1
            
            self.handle_mouse()
            self.update_enemies()
            self.check_enemy_collision()
            # Check if gate should open (after 2 minutes)
            if not self.gate_open and time.time() - self.start_time > 120:
                self.gate_open = True
            
            self.check_health_pickup()
            self.check_gate_collision()
            self.render()
            time.sleep(0.03)
    
    def draw_gate(self, screen, fov):
        if not self.gate_open:
            return
        
        # Calculate relative position to player
        dx = self.gate_x - self.x
        dy = self.gate_y - self.y
        
        # Calculate angle to gate relative to player's view
        gate_angle = math.atan2(dx, dy)
        angle_diff = gate_angle - self.angle
        
        # Normalize angle difference
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Check if gate is in field of view
        if abs(angle_diff) > fov / 2:
            return
        
        # Calculate distance and screen position
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 0.1:
            return
        
        # Calculate screen column
        screen_x = int(self.width / 2 + (angle_diff / fov) * self.width)
        if screen_x < 0 or screen_x >= self.width:
            return
        
        # Calculate sprite size based on distance
        sprite_size = max(1, int(self.height * 0.6 / distance))
        if sprite_size > 64:
            return
        
        # Calculate vertical position
        horizon = self.height // 2 + int(self.z * 2 + self.pitch * self.height * 0.3)
        sprite_y = horizon - sprite_size // 2
        
        # Draw gate sprite
        self.draw_gate_sprite(screen, screen_x, sprite_y, sprite_size, distance)
    
    def draw_gate_sprite(self, screen, center_x, center_y, size, distance):
        sprite = self.sprites['gate']
        
        for y in range(size):
            for x in range(size):
                screen_x = center_x - size // 2 + x
                screen_y = center_y + y
                
                # Check bounds
                if (screen_x < 0 or screen_x >= self.width or 
                    screen_y < 0 or screen_y >= self.height):
                    continue
                
                # Check depth
                if self.depth_map[screen_x][screen_y] < distance:
                    continue
                
                # Get sprite pixel
                sprite_x = int((x / size) * 32)
                sprite_y = int((y / size) * 32)
                char, color, alpha = sprite[sprite_y][sprite_x]
                
                if alpha > 0:
                    brightness = 0
                    if self.torch_enabled:
                        flashlight_idx = screen_x + screen_y * self.width
                        if flashlight_idx < len(self.flashlight_coeff):
                            brightness = self.battery * self.light_flashlight * self.flashlight_coeff[flashlight_idx] / (distance + 0.5)
                    
                    if brightness > 0.2:
                        if brightness > 0.6:
                            intensity = f"1;{color}"
                        else:
                            intensity = str(color)
                        
                        screen[screen_x][screen_y] = f"\033[{intensity}m{char}\033[0m"
                        self.depth_map[screen_x][screen_y] = distance
    
    def check_gate_collision(self):
        if not self.gate_open:
            return
        dx = self.gate_x - self.x
        dy = self.gate_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 1.0:
            self.game_won = True

if __name__ == "__main__":
    Big3D().run()