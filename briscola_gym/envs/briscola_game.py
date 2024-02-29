import random

seed_dict = ['spade', 'bastoni', 'denari', 'coppe']

card_dict = {
    'asso': (12, 11),
    'tre': (11, 10),
    're': (10, 4),
    'cavallo': (9, 3),
    'fante': (8, 2),
    'due': (2, 0),
    'quattro': (4, 0),
    'cinque': (5, 0),
    'sei': (6, 0),
    'sette': (7, 0),
}

class Card(object):
    """docstring for Card"""
    def __init__(self, name, seed, is_briscola=False, card_id=None):
        super(Card, self).__init__()
        self._name = name
        self._seed = seed
        self._value = card_dict[name][0]
        self._score = card_dict[name][1]
        self._is_briscola = is_briscola
        self._card_id = card_id

    @property
    def name(self):
        return self._name

    @property
    def seed(self):
        return self._seed

    @property
    def value(self):
        return self._value
    
    @property
    def score(self):
        return self._score

    @property
    def card_id(self):
        return self._card_id
    
    def is_briscola(self):
        return self._is_briscola

    def set_briscola(self):
        self._is_briscola = True

    def __str__(self):
        if self._is_briscola:
            return self._name + ' di ' + self._seed + ' (briscola)'
        else:
            return self._name + ' di ' + self._seed

    def __repr__(self):
        return self.__str__()

class Deck(object):
    """docstring for Deck"""
    def __init__(self, briscola=None):
        super(Deck, self).__init__()
        # Generate list of cards (do not assign briscola now)
        self._card_dict = {}
        self.reset()
        # Set briscola seed if provided
        self._briscola_ref = None
        if briscola is not None:
            assert briscola in seed_dict
            self._briscola_seed = briscola
            self.set_briscola(set_from_top=False)

    @property
    def card_dict(self):
        return self._card_dict
    
    @property
    def briscola(self):
        return self._briscola_seed

    @property
    def briscola_ref(self):
        return self._briscola_ref

    @property
    def briscola_card(self):
        return self._briscola_card

    def reset(self):
        self._cards = []
        card_id = 1 # zero will be reserved for the Not-a-Card (NaC) token.
        for seed in seed_dict:
            for name, _ in card_dict.items():
                self._cards.append(Card(name, seed, card_id=card_id))
                self._card_dict[card_id] = Card(name, seed, card_id=card_id)
                card_id += 1
        self._card_dict[0] = 0
        random.shuffle(self._cards)
        self._briscola_card = None
        self._briscola_seed = None
        self._briscola_ref = None

    def set_briscola(self, set_from_top=True):
        # Extract the briscola from main deck (top card)
        if set_from_top:
            self._briscola_card = self._cards.pop()
            self._briscola_seed = self._briscola_card.seed
            self._briscola_ref = self._briscola_card
            # print('[Deck] Briscola di: ', self._briscola_seed)
            for card in self._cards:
                if card.seed == self._briscola_seed:
                    # print('[Deck] Making {} a briscola.'.format(card))
                    card.set_briscola()
        else:
            # Set briscola randomly
            self._briscola_seed = random.choice(seed_dict)
            briscole = []
            for i, card in enumerate(self._cards):
                if card.is_briscola():
                    briscole.append((i, card))
            got_briscola = False
            while not got_briscola:
                briscola_idx, self._briscola_card = random.choice(briscole)
                if self._briscola_card.is_briscola():
                    got_briscola = True
            self._briscola_seed = self._briscola_card.seed
            self._briscola_card = self._cards.pop(briscola_idx)
            for card in self._cards:
                if card.seed == self._briscola_seed:
                    card.set_briscola()

    def get_card_from_id(self, card_id):
        card = self._card_dict[card_id]
        if card.seed == self.briscola:
            card.set_briscola()
        return card

    def pop(self):
        if len(self._cards) == 0:
            # print('POPPING LAST BRISCOLA CARD: {}'.format(self._briscola_card))
            card = self._briscola_card
            self._briscola_card = None
            return card
        else:
            return self._cards.pop()

    def __len__(self):
        # Return the cards left plus the briscola
        total_cards = len(self._cards)
        if self._briscola_card is not None:
            return total_cards + 1
        else:
            return total_cards

    def __str__(self):
        if self._briscola_card is not None:
            out_str = 'briscola: ' + self._briscola_card.__str__() + '\n'
        else:
            out_str = ''
        for i, card in enumerate(self._cards):
            out_str += card.__str__()
            if i != len(self._cards) - 1:
                out_str += '\n'
        return out_str

    def __repr__(self):
        return self.__str()

class Hand(object):
    """docstring for Hand"""
    def __init__(self):
        super(Hand, self).__init__()
        # self._cards = {0: 0, 1: 0, 2: 0}
        self._cards = []
        self._size = 0

    @property
    def cards(self):
        return self._cards

    @property
    def size(self):
        return self._size

    def add_card(self, card):
        # for i, hand_card in enumerate(self._cards.items()):
        #     if hand_card == 0:
        #         self._cards[i] = card
        self._cards.append(card)
        self._size += 1

    def get_card(self, i):
        # ret_card = self._cards[i % self._size]
        # self._cards[i % self._size] = 0
        # self._size -= 1
        # return ret_card
        # 
        ret_card = self._cards.pop(i % self._size)
        self._size -= 1
        return ret_card

    def highest_card(self):
        high_card = self._cards[0]
        # for pos, card in self._cards.items():
        for card in self._cards:
            if card.score > high_card.score:
                high_card = card
        return high_card

    def reset(self):
        # self._cards = {0: None, 1: None, 2: None}
        self._cards = []
        self._size = 0

    def __getitem__(self, i):
        return self._cards[i]

    def __str__(self):
        out_str = ''
        # for card in self._cards.items():
        for card in self._cards:
            out_str += str(card) + ', '
        return out_str

    def __repr__(self):
        return self.__str()

class Player(object):
    """docstring for Player"""
    def __init__(self, deck, player_id=0, team_id=0):
        super(Player, self).__init__()
        self._deck = deck
        self._player_id = player_id
        self._team_id = team_id
        self._hand = Hand()
        self._score = 0

    @property
    def hand(self):
        return self._hand

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    @property
    def player_id(self):
        return self._player_id

    @property
    def team_id(self):
        return self._team_id

    def reset(self):
        self._hand.reset()

    def draw(self, deck):
        self._hand.add_card(deck.pop())

    def hand_size(self):
        return self._hand.size

    def play(self, i):
        return self._hand.get_card(i)

    def play(self, i, field):
        field.add_card(self._hand.get_card(i), self._player_id, self._team_id)

    def play_random(self):
        return self._hand.get_card(random.randint(0, self._hand.size - 1))

    def play_dummy_ai(self):
        pass

class Field(object):
    """docstring for Field"""
    def __init__(self):
        super(Field, self).__init__()
        self._cards = []
        self._score = 0
        self._winning_team_id = None

    @property
    def score(self):
        return self._score

    @property
    def cards(self):
        return self._cards
    
    def get_cards(self):
        cards = []
        for card in self._cards:
            card.append(self._cards[0])
        return cards

    def get_cards_and_ids(self):
        return self._cards

    def get_score(self):
        score = 0
        if self._cards != []:
            for card, _, _ in self._cards:
                score += card.score
        return score

    def add_card(self, card, player_id, team_id):
        self._cards.append((card, player_id, team_id))
        self._score += card.score

    def get_current_winner(self):
        winner_card, winner_player_id, winner_team_id = self._cards[0]
        for card, player_id, team_id in self._cards[1:]:
            if card.seed == winner_card.seed:
                if card.score > winner_card.score:
                    winner_card = card
                    winner_player_id = player_id
                    winner_team_id = team_id
            elif card.seed != winner_card.seed:
                if card.is_briscola():
                    winner_card = card
                    winner_player_id = player_id
                    winner_team_id = team_id
        return winner_player_id, winner_team_id

    def get_teams_scores(self):
        scores = {}
        for card, _, team_id in self._cards:
            scores[team_id] = 0
        for card, player_id, _ in self._cards:
            scores[team_id] += card.value
        return scores

    def get_players_scores(self):
        scores = {}
        for card, player_id, _ in self._cards:
            scores[player_id] = 0
        for card, player_id, _ in self._cards:
            scores[player_id] += card.value
        return scores

    def get_winner_and_score(self):
        winner_player_id, winner_team_id = self.get_current_winner()
        ret_score = self._score
        self._score = 0
        return winner_player_id, winner_team_id, ret_score

    def clear_field(self):
        self._cards = []

    def reset(self):
        self.clear_field()

    def __str__(self):
        out_str = ''
        for i, (card, player_id, team_id) in enumerate(self._cards):
            # out_str += '{}'.format(card)
            out_str += '{} giocata da giocatore {} in team {}'.format(card, player_id, team_id)
            if i != len(self._cards) - 1:
                out_str += '\n'
        return out_str

    def __repr__(self):
        return self.__str()

class Game(object):
    """docstring for Game"""
    def __init__(self, num_players=2, num_players_per_team=2, init_game=True):
        super(Game, self).__init__()
        assert num_players % 2 == 0, 'The number of players must be an even number.'
        self._num_players = num_players
        self._deck = Deck()
        self._field = Field()
        self._players = []
        self._teams_score = {}
        for i in range(num_players):
            self._players.append(Player(self._deck, player_id=i, team_id=(i % num_players_per_team)))
        if num_players == 2:
            num_teams = 2
        else:
            num_teams = num_players // 2
        for i in range(num_teams):
            self._teams_score[i] = 0
        if init_game:
            self.init_game()
            self._game_started = True
        else:
            self._game_started = False
        self._last_winner_id = 0
        self._last_winner_team_id = 0
        self._turn_cnt = 0

    @property
    def last_winner_id(self):
        return self._last_winner_id

    @property
    def last_winner_team_id(self):
        return self._last_winner_team_id

    @property
    def num_players(self):
        return self._num_players

    @property
    def deck(self):
        return self._deck

    @property
    def field(self):
        return self._field

    @property
    def players(self):
        return self._players

    @property
    def teams_score(self):
        return self._teams_score

    def init_game(self):
        for _ in range(3):
            for player in self._players:
                player.draw(self._deck)
        self._deck.set_briscola()
        for player in self._players:
            for card in player.hand:
                if card.seed == self._deck.briscola:
                    card.set_briscola()
        self._last_winner_id = 0
        self._game_started = True

    def reset(self):
        for player in self._players:
            player.reset()
        self._turn_cnt = 0
        self._field.reset()
        self._deck.reset()
        if self._num_players == 2:
            num_teams = 2
        else:
            num_teams = self._num_players // 2
        for i in range(num_teams):
            self._teams_score[i] = 0

    def player_play_card(self, player_id, card_index):
        self._players[player_id].play(card_index, self._field)

    def players_hand_size(self):
        hand_size = 0
        for player in self._players:
            hand_size += player.hand_size()
        return hand_size

    def resolve_step(self, verbose=0):
        self._turn_cnt += 1
        if verbose == 1:
            print(self._field)
        winner_player_id, winner_team_id, score = self._field.get_winner_and_score()
        if verbose:
            print(f'Vince giocatore {winner_player_id} con {score} punti (briscola: {self.deck.briscola})')
        self._last_winner_id = winner_player_id
        self._last_winner_team_id = winner_team_id
        self._teams_score[winner_team_id] += score
        if len(self._deck) > 0:
            for i in range(self._num_players):
                self._players[(winner_player_id + i) % self._num_players].draw(self._deck)
        self._field.clear_field()
        return winner_player_id, winner_team_id

    def random_step(self, debug=False):
        for i in range(self._num_players):
            player = self._players[(self._last_winner_id + i) % self._num_players]
            if not debug:
                self._field.add_card(player.play_random(), player.player_id, player.team_id)
            else:
                if i == 0:
                    print('Gioca per primo il giocatore {} team {}'.format(self._last_winner_id, self._players[self._last_winner_id].team_id))
                else:
                    print('Gioca il giocatore {} team {}'.format((self._last_winner_id + i) % self._num_players, self._players[(self._last_winner_id + i) % self._num_players].team_id))
                if (self._last_winner_id + i) % self._num_players == 0:
                    hand = player.hand
                    index = int(input('Scegli una carta:\n0: {}\n1: {}\n2: {}\n'.format(hand[0], hand[1], hand[2])))
                    player.play(index, self._field)
                else:
                    self._field.add_card(player.play_random(), player.player_id, player.team_id)
        # print('{}'.format(self._field))

    def step(self):
        # self.random_step()
        self.resolve_step()

    def get_winner_team(self):
        winning_score = 0
        winning_team = 0
        for team_id, score in self._teams_score.items():
            if score > winning_score:
                winning_score = score
                winning_team = team_id
        return winning_team, winning_score

    def simulate_random_game(self):
        while self.players_hand_size() > 0:
            self.step()
            # print('-' * 80)
        winning_team, winning_score = self.get_winner_team()
        print('Vince il team {} con {} punti.'.format(winning_team, winning_score))


def main():
    for _ in range(1):
        game = Game(num_players=2)
        print('Briscola di: {}'.format(game.deck.briscola))
        game.simulate_random_game()
    

if __name__ == '__main__':
    main()