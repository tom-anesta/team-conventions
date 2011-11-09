'''
A set of constant values to be referenced elsewhere in the program. This
module does not import any others, so it is safe to import it anywhere.
'''

#for keys
LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"
PULL = "pull"
PUSH = "push"
SWITCH = "switch"
PAUSE = "pause"
QUIT = "quit"

#for shooting with magnets
NARROW = "narrow"
AREA = "area"

#for movement
MAX_HEIGHT = 55 #the max height that you can go up, the floor is around -15, it's a float value so it's misleading sometimes
GROUND_REPULSION_MULTIPLIER = 0.1

#paths
MODELS_PATH = "../lib/models/"
SFX_PATH = "../lib/sfx/"
PARAMS_PATH = "../params/"
TEXTURES_PATH = "../lib/textures/"

#for reading from text file
TEXT_DELIMITER = "%%%"
#codes for reading terrain from text file
TERRAIN_OUTER = "terrain_outer"#text used to designate that the text following it is the parameters for creating the background terrain
TERRAIN_OBJECT = "terrain_object"#text used to designate that the text following it is the parameters for creating a static terrain object within the terrain
#codes for reading enemies
BEGIN_WAVE = "BEGINWAVE"
END_WAVE = "ENDWAVE"
RUSH_ENEMY = "rush_enemy"
DRONE_ENEMY = "drone_enemy"

#collision groups, make sure are power of two
TERRAIN_RAY_MASK = 4
PLAYER_ENEMY_OBJECTS = 8



