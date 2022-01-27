"""
Assignment 1: Meepo is You

=== CSC148 Winter 2021 ===
Department of Mathematical and Computational Sciences,
University of Toronto Mississauga

=== Module Description ===
This module contains the Game class and the main game application.

"""

from typing import Any, Type, Tuple, List, Sequence, Optional

import pygame

import actor
from settings import *
from stack import Stack


class Game:
    """
    Class representing the game.
    """
    size: Tuple[int, int]
    width: int
    height: int
    screen: Optional[pygame.Surface]
    x_tiles: int
    y_tiles: int
    tiles_number: Tuple[int, int]
    background: Optional[pygame.Surface]

    _actors: List[actor.Actor]
    _is: List[actor.Is]
    _running: bool
    _rules: List[str]
    _history: Stack

    player: Optional[actor.Actor]
    map_data: List[str]
    keys_pressed: Optional[Sequence[bool]]

    def __init__(self) -> None:
        """
        Initialize variables for this Class.
        """
        self.width, self.height = 0, 0
        self.size = (self.width, self.height)
        self.screen = None
        self.x_tiles, self.y_tiles = (0, 0)
        self.tiles_number = (self.x_tiles, self.y_tiles)
        self.background = None

        self._actors = []
        self._is = []
        self._running = True
        self._rules = []
        self._history = Stack()
        self.player = None
        self.map_data = []

        self.keys_pressed = []

    def load_map(self, path: str) -> None:
        """
        Reads a .txt file representing the map
        """
        with open(path, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.width = (len(self.map_data[0])) * TILESIZE
        self.height = len(self.map_data) * TILESIZE
        self.size = (self.width, self.height)
        self.x_tiles, self.y_tiles = len(self.map_data[0]), len(self.map_data)

        # center the window on the screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def new(self) -> None:
        """
        Initialize variables to be object on screen.
        """
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(
            "{}/backgroundBig.png".format(SPRITES_DIR)).convert_alpha()
        for col, tiles in enumerate(self.map_data):
            for row, tile in enumerate(tiles):
                if tile.isnumeric():
                    self._actors.append(
                        Game.get_character(CHARACTERS[tile])(row, col))
                elif tile in SUBJECTS:
                    self._actors.append(
                        actor.Subject(row, col, SUBJECTS[tile]))
                elif tile in ATTRIBUTES:
                    self._actors.append(
                        actor.Attribute(row, col, ATTRIBUTES[tile]))
                elif tile == 'I':
                    is_tile = actor.Is(row, col)
                    self._is.append(is_tile)
                    self._actors.append(is_tile)

    def get_actors(self) -> List[actor.Actor]:
        """
        Getter for the list of actors
        """
        return self._actors

    def get_running(self) -> bool:
        """
        Getter for _running
        """
        return self._running

    def get_rules(self) -> List[str]:
        """
        Getter for _rules
        """
        return self._rules

    def get_is(self) -> List[actor.Is]:
        """
        Getter for _rules
        """
        return self._is

    def _draw(self) -> None:
        """
        Draws the screen, grid, and objects/players on the screen
        """
        self.screen.blit(self.background,
                         (((0.5 * self.width) - (0.5 * 1920),
                           (0.5 * self.height) - (0.5 * 1080))))
        for actor_ in self._actors:
            rect = pygame.Rect(actor_.x * TILESIZE,
                               actor_.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(actor_.image, rect)

        # Blit the player at the end to make it above all other objects
        if self.player:
            rect = pygame.Rect(self.player.x * TILESIZE,
                               self.player.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(self.player.image, rect)

        pygame.display.flip()

    def _events(self) -> None:
        """
        Event handling of the game window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            # Allows us to make each press count as 1 movement.
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed = pygame.key.get_pressed()
                ctrl_held = self.keys_pressed[pygame.K_LCTRL]

                # handle undo button and player movement here
                if event.key == pygame.K_z and ctrl_held:  # Ctrl-Z
                    self._undo()
                else:
                    if self.player is not None:
                        assert isinstance(self.player, actor.Character)
                        save = self._copy()
                        if self.player.player_move(self) \
                                and not self.win_or_lose():
                            self._history.push(save)
        return

    def win_or_lose(self) -> bool:
        """
        Check if the game has won or lost
        Returns True if the game is won or lost; otherwise return False
        """
        assert isinstance(self.player, actor.Character)
        for ac in self._actors:
            if isinstance(ac, actor.Character) \
                    and ac.x == self.player.x and ac.y == self.player.y:
                if ac.is_win():
                    self.win()
                    return True
                elif ac.is_lose():
                    self.lose(self.player)
                    return True
        return False

    def run(self) -> None:
        """
        Run the Game until it ends or player quits.
        """
        while self._running:
            pygame.time.wait(1000 // FPS)
            self._events()
            self._update()
            self._draw()

    def set_player(self, actor_: Optional[actor.Actor]) -> None:
        """
        Takes an actor and sets that actor to be the player
        """
        self.player = actor_

    def remove_player(self, actor_: actor.Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """
        self._actors.remove(actor_)
        self.player = None

    def _update(self) -> None:
        """
        Check each "Is" tile to find what rules are added and which are removed
        if any, and handle them accordingly.
        """
        rules = []
        for ar in self._actors:
            if isinstance(ar, actor.Is):
                up = self.get_actor(ar.x - 1, ar.y)
                down = self.get_actor(ar.x + 1, ar.y)
                left = self.get_actor(ar.x, ar.y - 1)
                right = self.get_actor(ar.x, ar.y + 1)
                r1, r2 = ar.update(up, down, left, right)
                rules.append(r1)
                rules.append(r2)

        rules = self.edit_rules(rules)

        remove_rules = [r for r in self._rules if r not in rules]

        for rule2 in remove_rules:
            rule2 = rule2.split(" ")
            for character in self._actors:
                object = self.get_character(rule2[0])
                if object is not None:
                    if isinstance(character, object):
                        self.deforce_rule(character, rule2[1])

        for rule in rules:
            rule = rule.split(" ")
            for character in self._actors:
                object = self.get_character(rule[0])
                if object is not None:
                    if isinstance(character, object):
                        self.enforce_rule(character, rule[1])

        self._rules = rules

        return

    def deforce_rule(self, character: Optional[type], rule: str) -> None:
        """ Takes rules out of effect
        """
        if rule == 'isYou':
            self.player = None
        if rule == "isPush":
            character.unset_push()
        if rule == "isStop":
            character.unset_stop()
        if rule == "isVictory":
            character.unset_win()
        if rule == "isLose":
            character.unset_lose()
        return

    def enforce_rule(self, character: Optional[type], rule: str) -> None:
        """ Puts all the rules into effect
        """
        if rule == "isYou":
            self.player = character
            character.set_player()
            if self.player != character:
                self.player.unset_player()
                self.player = character
                character.set_player()
        if rule == "isPush":
            character.set_push()
        if rule == "isStop":
            character.set_stop()
        if rule == "isVictory":
            character.set_win()
        if rule == "isLose":
            character.set_lose()
        return

    @staticmethod
    def edit_rules(rules: List[str]) -> List[str]:
        """ Edits the current rules to fit game description """
        rules = [rule for rule in rules if rule != '']
        dix = {}

        for rule in rules:
            rule = rule.split(" ")
            if rule[0] in dix:
                dix[rule[0]].append(rule[1])
            else:
                dix[rule[0]] = [rule[1]]
        indexes = []
        for key in dix:
            if len(dix[key]) >= 2:
                for item in dix[key]:
                    indexes.append(rules.index(key + " " + item))

        while len(indexes) > 1:
            elem = max(indexes)
            indexes.remove(elem)
            rules.pop(elem)

        return rules

    @staticmethod
    def get_character(subject: str) -> Optional[Type[Any]]:
        """
        Takes a string, returns appropriate class representing that string
        """
        if subject == "Meepo":
            return actor.Meepo
        elif subject == "Wall":
            return actor.Wall
        elif subject == "Rock":
            return actor.Rock
        elif subject == "Flag":
            return actor.Flag
        elif subject == "Bush":
            return actor.Bush
        return None

    def _undo(self) -> None:
        """
        Returns the game to a previous state based on what is at the top of the
        _history stack.
        """
        game = self._history.pop()
        self._is = game.get_is()
        self.player = game.player
        self._actors = game.get_actors()
        self._rules = game.get_rules()
        self._running = game.get_running()
        self.keys_pressed = game.keys_pressed
        return

    def _copy(self) -> 'Game':
        """
        Copies relevant attributes of the game onto a new instance of Game.
        Return new instance of game
        """
        game_copy = Game()

        if self.player is not None:
            game_copy.player = self.player.copy()

        game_copy._rules = self._rules
        game_copy._running = self._running
        game_copy.keys_pressed = self.keys_pressed

        for ac in self._actors:
            game_copy._actors.append(ac.copy())

        for item in self._is:
            game_copy._is.append(item.copy())

        return game_copy

    def get_actor(self, x: int, y: int) -> Optional[actor.Actor]:
        """
        Return the actor at the position x,y. If the slot is empty, Return None
        """
        for ac in self._actors:
            if ac.x == x and ac.y == y:
                return ac
        return None

    def win(self) -> None:
        """
        End the game and print win message.
        """
        self._running = False
        print("Congratulations, you won!")

    def lose(self, char: actor.Character) -> None:
        """
        Lose the game and print lose message
        """
        self.remove_player(char)
        print("You lost! But you can have it undone if undo is done :)")


if __name__ == "__main__":
    game = Game()
    # load_map public function
    game.load_map(MAP_PATH)
    game.new()
    game.run()

    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['settings', 'stack', 'actor', 'pygame']
    # })
