import pygame
import random
import math

pygame.init()

# Screen setup
width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Struggle of a Lowly Mage')

# Game states reflect the section of the code the user is in
class GameState:
    MAIN_SCREEN = 0
    BATTLE_SCREEN = 1
    GAME_OVER = 2
    VICTORY = 3

current_state = GameState.MAIN_SCREEN

# Inventory and abilities
class Player:
    def __init__(self):
        self.health = 100
        self.mana = 50
        self.max_health = 100
        self.max_mana = 50
        self.gold = 0
        self.health_potions = 3
        self.mana_potions = 2
        self.has_fireball = True
        self.last_attack_type = None  # Track last attack for enemy AI

player = Player()

# Enhanced Enemy classes with behaviors
class Enemy:
    def __init__(self, name, health, damage, image, attack_image, behavior_type):
        self.name = name
        self.health = health
        self.max_health = health
        self.damage = damage
        self.image = image
        self.attack_image = attack_image
        self.behavior_type = behavior_type  # 'aggressive', 'defensive', 'tactical', 'reckless'
        self.turns_since_last_attack = 0
    
    def decide_attack(self, player):
        # Decide attack strategy based on player state and enemy behavior
        self.turns_since_last_attack += 1
        
        # Common behavior patterns
        if self.behavior_type == 'aggressive':
            # Always attack, but stronger when player is weak
            if player.health < player.max_health * 0.3:
                return self.damage * 1.5  # Critical hit when player is low
            return self.damage
            
        elif self.behavior_type == 'defensive':
            # Sometimes defend (heal) if health is low
            if self.health < self.max_health * 0.4 and random.random() < 0.5:
                self.health = min(self.max_health, self.health + self.max_health * 0.3)
                return 0  # No damage this turn
            return self.damage
            
        elif self.behavior_type == 'tactical':
            # React to player's last move and state
            if player.last_attack_type == 'Fireball' and player.mana < 20:
                # Player used fireball and is low on mana - press advantage
                return self.damage * 1.2
            elif player.health < player.max_health * 0.5:
                # Player is below half health - finish them
                return self.damage * 1.3
            elif self.turns_since_last_attack > 2:
                # Been too defensive - time to strike
                return self.damage * 1.5
            else:
                # Default defensive stance
                return self.damage * 0.8
                
        elif self.behavior_type == 'reckless':
            # Random powerful attacks but sometimes misses
            if random.random() < 0.3:
                return 0  # Miss
            elif random.random() < 0.2:
                return self.damage * 2  # Big hit
            return self.damage
        
        return self.damage  # Default

# Load assets
def load_image(name, scale=None):
    try:
        img = pygame.image.load(name)
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except:
        print("Failed to load image:",name)
        return pygame.Surface((50, 50))  # Return blank surface if image fails to load

# Load images
title_image = load_image('gametitle.png')
buttonhovering_image = load_image('buttonhovering.png')
healthpotion_image = load_image('healthpotion.png', (32, 32))
manapotion_image = load_image('manapotion.png', (32, 32))
wizard_image = load_image('wizardstationary.png')
wizardattack_image = load_image('wizardattack.png')
wizardattacktwitch_image = load_image('wizardattacktwitch.png')
wizardfireball_image = load_image('wizardfireball.png')
arena_image = load_image('arena.png')
trees_image = load_image('trees.png')
bushes_image = load_image('bushes.png')
fire_image = load_image('fire.png')
goblin_image = load_image('goblin.png')
goblinattack_image = load_image('goblinattack.png')
knight_image = load_image('knight.png')
knightattack_image = load_image('knightattack.png')
golem_image = load_image('golem.png')
golemattack_image = load_image('golemattack.png')
dragon_image = load_image('dragon.png')
dragonattack_image = load_image('dragonattack.png')
staffwhack_image = load_image('staffwhack.png', (32, 32))

# Load sounds
def load_sound(name):
    try:
        return pygame.mixer.Sound(name)
    except:
        print("Failed to load sound:",name)
        return None

battle_audio = load_sound('battle.mp3')
lightning_audio = load_sound('blaster.mp3')
gameover_audio = load_sound('gameover.mp3')
buttonpress_audio = load_sound('pressbutton.wav')
titlemusic_audio = load_sound('title.mp3')
buttonselect_audio = load_sound('selectionsound.wav')

# Game setup
selection_horiz = 0
selection_vert = 0
max_selection_horiz = 1
max_selection_vert = 0

# Define attacks and potions
attacks = [
    ('Staff Whack', staffwhack_image, 15, 0, 'physical'),
    ('Fireball', wizardfireball_image, 50, 25, 'magic')
]

potions = [
    ('Health Potion', healthpotion_image, 50, 'health'),
    ('Mana Potion', manapotion_image, 25, 'mana')
]

# Create enemies with behaviors
def create_enemies():
    enemies = []
    for _ in range(3):
        enemy_type = random.randint(1, 4)
        if enemy_type == 1:  # Goblin
            behavior = random.choice(['aggressive', 'reckless'])
            enemies.append(Enemy("Goblin", 50, 10, goblin_image, goblinattack_image, behavior))
        elif enemy_type == 2:  # Knight
            behavior = random.choice(['defensive', 'tactical'])
            enemies.append(Enemy("Knight", 100, 25, knight_image, knightattack_image, behavior))
        elif enemy_type == 3:  # Golem
            behavior = random.choice(['defensive', 'aggressive'])
            enemies.append(Enemy("Golem", 150, 50, golem_image, golemattack_image, behavior))
        elif enemy_type == 4:  # Dragon
            behavior = random.choice(['tactical', 'aggressive'])
            enemies.append(Enemy("Dragon", 200, 75, dragon_image, dragonattack_image, behavior))
    return enemies

enemies = []
current_enemy_index = 0

# Font setup
font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 18)

def draw_text(text, x, y, color=(255, 255, 255), font_obj=font):
    text_surface = font_obj.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_health_bar(x, y, current, max_val, width=100, height=10):
    ratio = current / max_val
    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, width * ratio, height))

def draw_mana_bar(x, y, current, max_val, width=100, height=10):
    ratio = current / max_val
    pygame.draw.rect(screen, (100, 100, 255), (x, y, width, height))
    pygame.draw.rect(screen, (0, 0, 255), (x, y, width * ratio, height))

def main_screen():
    global current_state, selection_horiz # Global lets variables in functions be changed elsewhere in the code
    
    screen.fill((135, 206, 235))
    screen.blit(title_image, (0, 0))
    
    # Draw buttons
    play_color = (255, 255, 0) if selection_horiz == 0 else (255, 255, 255)
    quit_color = (255, 255, 0) if selection_horiz == 1 else (255, 255, 255)
    
    draw_text("Play", 70, 305, play_color)
    draw_text("Quit", 270, 305, quit_color)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        ''' When the user chooses to press enter while selection horiz = 0, it will reflect them hovering
        over the option "play" in the title screen. If they select anything else (the only other option
        is quit, we don't have to specify which value selection horiz is in), the game will quit.'''

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                selection_horiz = (selection_horiz - 1) % 2
                if buttonselect_audio: buttonselect_audio.play()
            elif event.key == pygame.K_RIGHT:
                selection_horiz = (selection_horiz + 1) % 2
                if buttonselect_audio: buttonselect_audio.play()
            elif event.key == pygame.K_RETURN:
                if selection_horiz == 0:  # Play
                    if titlemusic_audio: titlemusic_audio.stop()
                    if battle_audio: battle_audio.play(-1)
                    current_state = GameState.BATTLE_SCREEN
                    global enemies, current_enemy_index
                    enemies = create_enemies()
                    current_enemy_index = 0
                else:  # Quit
                    return False
    
    return True

def battle_screen():
    global current_state, current_enemy_index, player
    
    # Check if all enemies are defeated
    if current_enemy_index >= len(enemies):
        current_state = GameState.VICTORY
        return True
    
    current_enemy = enemies[current_enemy_index]
    
    # Draw battle scene
    screen.blit(arena_image, (0, 0))
    screen.blit(trees_image, (0, 0))
    screen.blit(bushes_image, (0, 0))
    
    # Draw characters
    screen.blit(wizard_image, (50, 200))
    screen.blit(current_enemy.image, (250, 200))
    
    # Draw health bars
    draw_health_bar(50, 180, player.health, player.max_health)
    draw_mana_bar(50, 195, player.mana, player.max_mana)
    draw_health_bar(250, 180, current_enemy.health, current_enemy.max_health)
    
    # Draw stats
    draw_text("Health: " + str(player.health) + "/" + str(player.max_health), 50, 160)
    draw_text("Mana: " + str(player.mana) + "/" + str(player.max_mana), 50, 140)
    draw_text(current_enemy.name, 250, 160)
    draw_text("Health: " + str(current_enemy.health) + "/" + str(current_enemy.max_health), 250, 140)
    draw_text("Behavior: " + current_enemy.behavior_type, 250, 120, font_obj=small_font)
    
    # Player turn
    menu_type = 'attacks'  # 'attacks' or 'potions'
    selection = 0
    
    selecting = True
    turn_consumed = False  # Track whether the turn should be consumed
    
    while selecting:
        # Only clear the menu area (top 100 pixels) instead of the whole screen
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, 400, 100))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    menu_type = 'potions' if menu_type == 'attacks' else 'attacks' # The menus will switch from one to the other when the player presses the tab key
                    selection = 0 # The selection will be reverted to 0
                    if buttonselect_audio: buttonselect_audio.play()
                elif event.key == pygame.K_UP:
                    if menu_type == 'attacks':
                        selection = (selection - 1) % len(attacks) # Changes the selection value if the user goes up or down
                    else:
                        selection = (selection - 1) % len(potions)
                    if buttonselect_audio: buttonselect_audio.play()
                elif event.key == pygame.K_DOWN:
                    if menu_type == 'attacks':
                        selection = (selection + 1) % len(attacks)
                    else:
                        selection = (selection + 1) % len(potions)
                    if buttonselect_audio: buttonselect_audio.play()
                elif event.key == pygame.K_RETURN:
                    if menu_type == 'attacks':
                        name, img, damage, mana_cost, attack_type = attacks[selection] # If the player is in the attacks menu, the menu will show the info for the attacks
                        if player.mana >= mana_cost: # If the player has enough mana, the mana will be consumed if the user casts an ability
                            player.mana -= mana_cost
                            current_enemy.health -= damage # The enemy's health will be subtracted by the damage corresponding to the ability used
                            player.last_attack_type = name  # Track last attack
                            if lightning_audio: lightning_audio.play()
                            
                            # Show attack animation
                            screen.blit(wizardattack_image, (50, 200))
                            pygame.display.flip()
                            pygame.time.delay(300)
                            
                            turn_consumed = True
                            selecting = False
                    else:
                        name, img, amount, p_type = potions[selection] # The menu info will be changed to the potions menu if the menu isn't in attacks
                        if p_type == 'health' and player.health_potions > 0:
                            player.health = min(player.max_health, player.health + amount) # If the user uses a health potion, the amount of health potions they have will decrease and their health will go up
                            player.health_potions -= 1
                            # Potion use doesn't consume turn
                            selecting = False
                            # Redraw to show updated health
                            screen.blit(arena_image, (0, 0))
                            screen.blit(trees_image, (0, 0))
                            screen.blit(bushes_image, (0, 0))
                            screen.blit(wizard_image, (50, 200))
                            screen.blit(current_enemy.image, (250, 200))
                            draw_health_bar(50, 180, player.health, player.max_health)
                            draw_mana_bar(50, 195, player.mana, player.max_mana)
                            draw_health_bar(250, 180, current_enemy.health, current_enemy.max_health)
                            pygame.display.flip()
                        elif p_type == 'mana' and player.mana_potions > 0: # Same with health but now for mana potion
                            player.mana = min(player.max_mana, player.mana + amount)
                            player.mana_potions -= 1
                            # Potion use doesn't consume turn
                            selecting = False
                            # Redraw to show updated mana
                            screen.blit(arena_image, (0, 0))
                            screen.blit(trees_image, (0, 0))
                            screen.blit(bushes_image, (0, 0))
                            screen.blit(wizard_image, (50, 200))
                            screen.blit(current_enemy.image, (250, 200))
                            draw_health_bar(50, 180, player.health, player.max_health)
                            draw_mana_bar(50, 195, player.mana, player.max_mana)
                            draw_health_bar(250, 180, current_enemy.health, current_enemy.max_health)
                            pygame.display.flip()
        
        # Draw menu
        if menu_type == 'attacks':
            draw_text("Attacks (TAB to switch)", 10, 10)
            for i, (name, img, damage, cost, _) in enumerate(attacks):
                color = (255, 255, 0) if i == selection else (255, 255, 255)
                y_pos = 40 + i * 30
                draw_text(name + " (Cost: " + str(cost) + " MP)", 40, y_pos, color)
                screen.blit(img, (10, y_pos))
                
                if i == selection:
                    effectiveness = ""
                    # Some enemies are more susceptible to different abilities, this tells the user that
                    if "Goblin" in current_enemy.name and name == "Staff Whack":
                        effectiveness = " (Effective!)"
                    elif "Knight" in current_enemy.name and name == "Fireball":
                        effectiveness = " (Weak...)"
                    draw_text(effectiveness, 200, y_pos, (255, 200, 0))
        else:
            draw_text("Potions (TAB to switch)", 10, 10)
            for i, (name, img, amount, p_type) in enumerate(potions):
                color = (255, 255, 0) if i == selection else (255, 255, 255)
                y_pos = 40 + i * 30
                count = str(player.health_potions) if p_type == 'health' else str(player.mana_potions) # Checks if the user is hovering over the mana potion or the health potion in the potions menu
                draw_text(name + " (" + count + " left)", 40, y_pos, color)
                screen.blit(img, (10, y_pos))

                # Tells the user that they might want to use a health potion if their health is at a 3rd of max
                if i == selection:
                    hint = ""
                    if p_type == 'health' and player.health < player.max_health * 0.3:
                        hint = " (Recommended!)"
                    # Tells the user that they might want to use the mana potion if their mana is less than 20
                    elif p_type == 'mana' and player.mana < 20 and player.has_fireball:
                        hint = " (Recommended!)"
                    draw_text(hint, 200, y_pos, (0, 255, 255))
        
        pygame.display.flip()
    
    # Only proceed to enemy turn if an attack was used
    if turn_consumed:
        # Redraw the scene after selection is made
        screen.blit(arena_image, (0, 0))
        screen.blit(trees_image, (0, 0))
        screen.blit(bushes_image, (0, 0))
        screen.blit(wizard_image, (50, 200))
        screen.blit(current_enemy.image, (250, 200))
        draw_health_bar(50, 180, player.health, player.max_health)
        draw_mana_bar(50, 195, player.mana, player.max_mana)
        draw_health_bar(250, 180, current_enemy.health, current_enemy.max_health)
        pygame.display.flip()
        
        # Check if enemy is defeated
        if current_enemy.health <= 0:
            current_enemy_index += 1
            if current_enemy_index >= len(enemies):
                current_state = GameState.VICTORY
                return True
        
        # Enemy turn
        enemy_damage = current_enemy.decide_attack(player)
        if enemy_damage > 0:
            player.health -= enemy_damage
            # Show enemy attack animation
            screen.blit(current_enemy.attack_image, (250, 200))
            pygame.display.flip()
            pygame.time.delay(500)
            
            # Redraw normal enemy after attack
            screen.blit(current_enemy.image, (250, 200))
            draw_health_bar(50, 180, player.health, player.max_health)
            pygame.display.flip()
        
        # Check if player is defeated
        if player.health <= 0:
            current_state = GameState.GAME_OVER
            return True
    
    return True

'''When the user's health drops to or below 0, they will have lost the game, and will trigger this function.
The screen will be filled with black and the text GAME OVER and Press any key to continue will appear in
red. After this, the game state will be changed to main screen, and in doing so, the user will be sent
back to the main screen. The health and mana of the player is also reverted to max.'''

def game_over_screen():
    global current_state
    
    screen.fill((0, 0, 0))
    draw_text("GAME OVER", 150, 180, (255, 0, 0))
    draw_text("Press any key to continue", 120, 220)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            current_state = GameState.MAIN_SCREEN
            if battle_audio: battle_audio.stop()
            if titlemusic_audio: titlemusic_audio.play(-1)
            # Reset player
            player.health = player.max_health
            player.mana = player.max_mana
    
    return True

'''When the user defeats all the enemies in the game, this function will trigger. Instead of GAME OVER
in red, the black screen will show bright green text with the word VICTORY! The rest of the code is the
same as the game over function, though.'''

def victory_screen():
    global current_state
    
    screen.fill((0, 0, 0))
    draw_text("VICTORY!", 150, 180, (0, 255, 0))
    draw_text("Press any key to continue", 120, 220)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            current_state = GameState.MAIN_SCREEN
            if battle_audio: battle_audio.stop()
            if titlemusic_audio: titlemusic_audio.play(-1)
            # Reset player
            player.health = player.max_health
            player.mana = player.max_mana
    
    return True

# Main game loop
running = True
if titlemusic_audio: titlemusic_audio.play(-1)

while running:
    if current_state == GameState.MAIN_SCREEN:
        running = main_screen()
    elif current_state == GameState.BATTLE_SCREEN:
        running = battle_screen()
    elif current_state == GameState.GAME_OVER:
        running = game_over_screen()
    elif current_state == GameState.VICTORY:
        running = victory_screen()
    
    pygame.display.flip()

pygame.quit()