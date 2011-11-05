'''
A set of constant values to be referenced elsewhere in the program. This
module does not import any others, so it is safe to import it anywhere.
'''
import os

LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"
PULL = "pull"
PUSH = "push"
SWITCH = "switch"
PAUSE = "pause"
QUIT = "quit"

NARROW = "narrow"
AREA = "area"

MODELS_PATH = os.path.dirname(__file__)+"/../lib/models/"
SFX_PATH = os.path.dirname(__file__)+"/../lib/sfx/"
PARAMS_PATH = os.path.dirname(__file__)+"/../params/"
TEXTURES_PATH = os.path.dirname(__file__)+"/../lib/textures/"
TEXT_DELIMITER = "%%%"

TERRAIN_OUTER = "terrain_outer"#text used to designate that the text following it is the parameters for creating the background terrain
TERRAIN_OBJECT = "terrain_object"#text used to designate that the text following it is the parameters for creating a static terrain object within the terrain
