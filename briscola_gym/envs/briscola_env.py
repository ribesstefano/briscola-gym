import gym
from gym import error, spaces, utils
from gym.utils import seeding
import gym_briscola.envs.briscola_game

import random
from gym_briscola.envs.briscola_game import Game

import numpy as np

# https://github.com/openai/gym/blob/master/docs/creating-environments.md
class BriscolaEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, num_players=2, init_game=False):
        super(BriscolaEnv, self).__init__()
        self.game = Game(num_players=num_players, init_game=init_game)
        if init_game:
            self.game_initialized = True
        else:
            self.game_initialized = False
        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(3)
        self.num_players = num_players
        self.player_id = 0
        self.num_played_cards = 0
        self.current_player = 0
        self.turn_cnt = 0
        # Example for using image as input:
        self.obs_shape = 3 * self.num_players + self.num_players + 3 + 1
        self.observation_space = spaces.Box(low=-np.ones((self.obs_shape,)),
            high=np.array([41] * self.obs_shape,), dtype=np.float16)
        # HEIGHT, WIDTH, N_CHANNELS = 1, 1, 1
        # self.observation_space = spaces.Box(low=0, high=255, shape=
        #                                 (HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8)

    def _next_observation(self, verbose=0):
        # Observations are custom objects:
        # Fields: (cards in hands, ..., briscola, field cards, ..., deck size, current player, winner player)
        hand_card_embeddings = np.zeros((self.num_players * 3,))

        for i, player in enumerate(self.game.players):
            hand = player.hand
            if hand.size > 0:
                hand_cards_id = []
                for j, card in enumerate(hand.cards):
                    hand_card_embeddings[i * 3 + j] = card.card_id
                if verbose >= 1:
                    print('Player {} hand cards: {}'.format(i, hand_card_embeddings[i*3:(i+1)*3]))

        field_card_embeddings = np.zeros((1 + self.num_players,))
        if self.game.deck.briscola_ref is not None:
            field_card_embeddings[0] = self.game.deck.briscola_ref.card_id
        field_cards = self.game.field.get_cards_and_ids()
        for card, player_id, team_id in field_cards:
            field_card_embeddings[player_id + 1] = card.card_id
        if verbose >= 1:
            print('Field_cards: ', field_card_embeddings[1:])

        # obs = np.concatenate((hand_card_embeddings, field_card_embeddings, np.array([len(self.game.deck)])))
        # obs = np.append(obs, [self.current_player, -1], axis=0)
        
        obs = np.concatenate([
                              hand_card_embeddings,
                              field_card_embeddings,
                              np.array([len(self.game.deck), self.current_player]),
                            ])
        
        return obs.astype(int)

    def reset(self):
        self.game.reset()
        self.game.init_game()
        self.game_initialized = True
        self.num_played_cards = 0
        # if not self.game_initialized:
        self.current_player = 0
        return self._next_observation()

    def _take_action(self, player_id, action):
        def get_card_id_from(a):
            if a < 1:
                card_id = 0
            elif a < 2:
                card_id = 1
            else:
                card_id = 2
            return card_id
        self.game.player_play_card(player_id, get_card_id_from(action))
        self.num_played_cards += 1

    def step(self, action, verbose=0):
        '''
        Return 
        '''
        if verbose > 0:
            print('-' * 80)
        resolve = False
        # reward, done, info can't be included
        reward = np.zeros((self.num_players,))
        if self.game.players_hand_size() > 0:
            done = False
            # Execute one time step within the environment
            self._take_action(self.current_player, action)
            
            # Update the playing player and resolve if all players played
            self.current_player = (self.current_player + 1) % self.game.num_players
            info = str(self.game.field)
            # Resolve if all players played a card
            if self.num_played_cards == self.num_players:
                field_score = self.game.field.get_score()
                team_scores = self.game.field.get_teams_scores()
                winner_player_id, winning_team_id = self.game.resolve_step(verbose=0)
                observation = self._next_observation() # We draw the cards in resolve_step

                winners_reward, losers_reward = field_score, 0 # -field_score
                # def reward_function():
                #     winners_reward = 0
                #     losers_reward = 0
                #     winning_cards_score = team_scores[winning_team_id]
                #     loser_cards_score = field_score - winning_cards_score
                #     if loser_cards_score == 0:
                #         # Even if they lost, the played cards had low values, so its a good
                #         # move overall
                #         losers_reward = 4
                #         if field_score == 0:
                #             winners_reward = 2
                #         else:
                #             winners_reward = field_score
                #     elif field_score - loser_cards_score > 0:
                #         # The loser team gave some points to the opponent one: fairly bad
                #         losers_reward = 0
                #         winners_reward = field_score * 1.1
                #     else:
                #         # The loser team gave a lot of points to the opponent one: very bad
                #         losers_reward = -1 * (loser_cards_score - field_score)
                #         winners_reward = field_score * 1.5
                #     return winners_reward, losers_reward
                # winners_reward, losers_reward = reward_function()

                for i in range(self.num_players):
                    if i % 2 == winning_team_id: # There are max two players per team
                        reward[i] = winners_reward
                    else:
                        reward[i] = losers_reward
                self.num_played_cards = 0
                self.current_player = winner_player_id
                observation[-1] = winner_player_id
                resolve = True
            else:
                observation = self._next_observation()
        else:
            done = True
            
            field_score = self.game.field.get_score()
            winners_reward, losers_reward = field_score, 0 # -field_score
            winning_team_id, winning_score = self.game.get_winner_team()
            for i in range(self.num_players):
                if i % 2 == winning_team_id: # There are max two players per team
                    reward[i] = winners_reward
                else:
                    reward[i] = losers_reward

            # for i in range(self.num_players):
            #     if i % 2 == winning_team_id: # There are max two players per team
            #         reward[i] = winning_score
            #     else:
            #         reward[i] = (120 - winning_score) * -1.5

            info = 'Game over.'
            observation = self._next_observation()
        if verbose > 0:
            print('Observation: ', observation)
            print('Reward {} by playing card {}'.format(reward, action))
        if resolve:
            if verbose > 0:
                print('-' * 80)
                print(' ' * 80)
                print(' ' * 80)
        return observation.astype(int), reward, done, info

    def render(self, mode='human'):
        print(self.game.teams_score)

    def close (self):
        pass