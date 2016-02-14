import zmq, threading, json, signal, sys
import AbsolutelyRankedWar

class Glob:
	keep_going = True

def sigint_handler(signal, frame):
	Glob.keep_going = False
	sys.exit(0)

def run(socks):
	poller = zmq.Poller()

	for sock in socks:
		poller.register(sock, flags=zmq.POLLIN)

	game = AbsolutelyRankedWar.AbsolutelyRankedWar()
	num_players_needed = 2
	num_players_connected = 0

	all_connected = False

	game_running = True
	while game_running and Glob.keep_going:
		events = dict(poller.poll())
		for i in xrange(len(socks)):
			if events.get(socks[i]) == zmq.POLLIN:
				msg = json.loads(socks[i].recv())
				if msg['type'] == 'connected':
					print msg['user_id'], 'connected'
					num_players_connected = num_players_connected + 1
					if num_players_connected == num_players_needed:
						all_connected = True
						for j in xrange(len(socks)):
							socks[j].send(game.get_init_msg(j))
				elif msg['type'] == 'move' and all_connected:
					print 'move received', 'from', msg['user_id'], 'on socket', i
					for sock in socks:
						print 'sending out move on', sock
						sock.send(json.dumps(msg))
				elif msg['type'] == 'quit':
					print 'received quit'
					exit()
				else:
					print 'received unknown message type'
					print msg

	for sock in socks:
		print 'closing socket', sock
		sock.close()


class GameServer:
	def __init__(self, ports):
		self.ctx = zmq.Context.instance()
		self.socks = []
		for port in ports:
			sock = self.ctx.socket(zmq.PAIR)
			sock.bind("tcp://0.0.0.0:" + str(port))
			print "listening on port", port
			self.socks.append(sock)

	def start(self):
		self.server = threading.Thread(target=run, args=(self.socks,))
		self.server.start()

def main():
	signal.signal(signal.SIGINT, sigint_handler)
	ports = [5001, 5002]
	server = GameServer(ports)
	run(server.socks)

if __name__ == '__main__':
	main()
