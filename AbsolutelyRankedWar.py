import random
import json

class AbsolutelyRankedWar:
	def __init__(self):
		deck = range(0,52)
		# random.shuffle(deck)
		self.deck = deck;

	def get_init_msg(self, player_id):
		msg_dict = {}
		msg_dict['type'] = 'init'
		msg_dict['player_id'] = player_id
		msg_dict['deck'] = self.deck

		return json.dumps(msg_dict)
