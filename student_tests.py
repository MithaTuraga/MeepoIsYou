from actor import *
from game import *

# USE PYGAME VARIABLES INSTEAD
keys_pressed = [0] * 323

# Setting key constants because of issue on devices
pygame.K_RIGHT = 1
pygame.K_DOWN = 2
pygame.K_LEFT = 3
pygame.K_UP = 4
pygame.K_LCTRIL = 5
pygame.K_z = 6
RIGHT = pygame.K_RIGHT
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
UP = pygame.K_UP
CTRL = pygame.K_LCTRL
Z = pygame.K_z


def setup_map(map: str) -> 'Game':
    """Returns a game with map1"""
    game = Game()
    game.new()
    game.load_map(os.path.abspath(os.getcwd()) + '/maps/' + map)
    game.new()
    game._update()
    game.keys_pressed = keys_pressed
    return game


def set_keys(up, down, left, right, CTRL=0, Z=0):
    keys_pressed[pygame.K_UP] = up
    keys_pressed[pygame.K_DOWN] = down
    keys_pressed[pygame.K_LEFT] = left
    keys_pressed[pygame.K_RIGHT] = right
    if CTRL and Z:
        print("UNDO")

def test1_move_player_up():
    """
    Check if player is moved up correctly
    """
    game = setup_map("student_map1.txt")
    set_keys(1, 0, 0, 0)
    result = game.player.player_move(game)
    assert result is True
    assert game.player.y == 1


def test2_push_block():
    """
    Check if player pushes block correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
        [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][
            0]
    result = game.player.player_move(game)
    assert result is True
    assert game.player.x == 3
    assert wall.x == 4


def test3_create_rule_wall_is_push():
    """
    Check if player creates wall is push rule correctly
    """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 0, 1)
    wall = \
        [i for i in game._actors if isinstance(i, Block) and i.word == "Wall"][
            0]
    result = game.player.player_move(game)
    game._update()
    assert game._rules[0] == "Wall isPush"
    assert game.player.x == 3
    assert wall.x == 4


def test_4_follow_rule_wall_is_push():
    """
    Check if player follows rules correctly
    """
    game = setup_map("student_map3.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 3


def test_5_no_push():
    """
    Check if player is not able to push because of rule not existing
    """
    game = setup_map("student_map4.txt")
    set_keys(0, 0, 0, 1)
    wall_object = game._actors[game._actors.index(game.player) + 1]
    result = game.player.player_move(game)
    assert game.player.x == 2
    assert wall_object.x == 2


def test_6_no_player():
    """
    Checks to see if there is no player if the isYou rule is empty
    """
    game = setup_map("student_map6.txt")
    assert game.player is None


def test_7_two_rules():
    """
    Checks to see that the new rule entered is taken into consideration
    if there exists two rules that contradict """
    game = setup_map("student_map7.txt")
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    game._update()
    rock = [actor for actor in game._actors if isinstance(actor, Rock)][0]
    assert rock.is_push() is True
    assert rock.is_stop() is False


def test_8_bushes():
    """
    Checks to see that meepo doesn't go through the bushes """
    game = setup_map("student_map2.txt")
    set_keys(0, 0, 1, 0)
    game.player.player_move(game)
    set_keys(0, 0, 1, 0)
    result = game.player.player_move(game)
    assert result is False
    assert game.player.x == 1
    assert game.player.y == 1


def test_9_screen():
    """
    Checks to see that meepo doesn't go outside of the screen """
    game = setup_map("student_map8.txt")
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    set_keys(0, 0, 2, 0)
    result = game.player.player_move(game)
    assert result is True
    assert game.player.x == 0
    assert game.player.y == 2


def test_10_win():
    """
    Checks to see that the game closes down once meepo hits the victor subject
    in this case, the flag
    """
    game = setup_map("student_map9.txt")
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    game.win_or_lose()
    assert game._running is False


def test_11_lose():
    """
    Checks to see that the game is still running even tho the actor has lost
    """
    game = setup_map("student_map10.txt")
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    game.win_or_lose()
    assert game._running is True


def test_12_undo():
    """
    Checks to see if undo works after the player has lost
    """
    game = setup_map("student_map10.txt")
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    game._history.push(game._copy())
    save = game._history.pop()
    game._undo()
    assert game.player.x == 12
    assert game.player.y == 2
    assert game.get_running() is True


def test_13_colour():
    """
    Checks to see if the is block is changing colour
    """
    game = setup_map("student_map11.txt")
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    game._update()
    block = [actor for actor in game._actors if isinstance(actor, Is)][0]
    assert block.colour == "Dark Blue"
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    game._update()
    block = [actor for actor in game._actors if isinstance(actor, Is)][0]
    assert block.colour == 'Light Blue'
    set_keys(0, 0, 1, 0)
    game.player.player_move(game)
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    game._update()
    block = [actor for actor in game._actors if isinstance(actor, Is)][0]
    assert block.colour == 'Purple'


def test_14_players():
    """
    Checks to see if the player is being swiyched up once the IsYou rule
    changes
    """
    game = setup_map("student_map12.txt")
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    game._update()
    assert isinstance(game.player, Rock)
    set_keys(0, 0, 1, 0)
    game.player.player_move(game)
    set_keys(0, 0, 1, 0)
    game.player.player_move(game)
    set_keys(0, 0, 1, 0)
    game.player.player_move(game)
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    game._update()
    assert game.player is None

def test_15_undois():
    """Checks to see if the colour of the is block is being altered after undo
    """
    game = setup_map("student_map11.txt")
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(0, 1, 0, 0)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(0, 0, 0, 1)
    game.player.player_move(game)
    game._history.push(game._copy())
    set_keys(1, 0, 0, 0)
    game.player.player_move(game)
    game._history.push(game._copy())
    game._update()
    block = [actor for actor in game._actors if isinstance(actor, Is)][0]
    assert block.colour == 'Light Blue'
    game._history.pop()
    game._history.pop()
    game._undo()
    game._update()
    block = [actor for actor in game._actors if isinstance(actor, Is)][0]
    assert block.colour == 'Dark Blue'

def test_16_subject_is_attribute():
    """Checks to see if is block's colour is only updating if the format
    of the blocks are Subject isAttribute"""

    game = setup_map("student_map13.txt")
    block = [actor for actor in game._actors if isinstance(actor, Is)][0]
    assert block.colour == 'Purple'


if __name__ == "__main__":
    import pytest

    pytest.main(['student_tests.py'])
