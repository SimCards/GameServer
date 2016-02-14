import zmq
import json
import threading
import sys, os, signal, random


class Glob:
	keep_going = True
	player_id = -1
	deck = None

def sigint_handler(signal, frame):
	Glob.keep_going = False
	os.system("stty echo")
	sys.exit(0)

def print_recv(sock):
	poller = zmq.Poller()
	poller.register(sock, zmq.POLLIN)
	while Glob.keep_going:
		events = dict(poller.poll(timeout=1000));
		if events.get(sock) == zmq.POLLIN:
			msg = sock.recv()
			print msg
			msg = json.loads(msg)
			if msg['type'] == 'init':
				Glob.player_id = msg['player_id']
				Glob.deck = msg['deck']
			elif msg['type'] == 'move':
				pass
			else:
				print 'unkown message type'


def main():
	signal.signal(signal.SIGINT, sigint_handler)
	if len(sys.argv) == 2:
		ip = sys.argv[1]
	else:
		port = 5002
		ip = "127.0.0.1:" + str(port)
	addr = "tcp://" + ip
	user_id = 'dummy_python' + ip

	ctx = zmq.Context.instance()

	sock = ctx.socket(zmq.PAIR)
	sock.connect(addr)

	connected_msg = {'type':'connected', 'user_id':user_id}
	sock.send(json.dumps(connected_msg))

	prntr = threading.Thread(target=print_recv, args=(sock,))
	prntr.start()



	while True:
		# os.system("stty -echo")
		line = raw_input("")
		# os.system("stty echo")

		msg_dict = {'type':'move',
					'user_id':user_id,
					'player_id':Glob.player_id
					}
		sock.send(json.dumps(msg_dict))


	Glob.keep_going = False

if __name__ == '__main__':
	main()
