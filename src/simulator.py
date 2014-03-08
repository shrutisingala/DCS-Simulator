#!/usr/bin/env python2.7


import collections
import logging


SendAction = collections.namedtuple('SendAction', 'destination packet_id')
ReceiveAction = collections.namedtuple('ReceiveAction', 'sender packet_id')
PrintAction = collections.namedtuple('PrintAction', 'payload')
MutexStartAction = collections.namedtuple('MutexStartAction', '')
MutexEndAction = collections.namedtuple('MutexEndAction', '')

Packet = collections.namedtuple('Packet', 'sender destination packet_id')


class Process(object):
    def __init__(self, name, actions, packet_pool):
        self.name = name
        self.actions = actions
        self.packet_pool = packet_pool
        self.clock = 1

    @property
    def is_done(self):
        return len(self.actions) == 0

    def __repr__(self):
        return 'Process(name={name}, actions={actions})'.format(
            name=self.name, actions=self.actions)

    def execute_next(self):
        if self.is_done:
            return
        if self.handle_action(self.actions[0]):
            self.clock += 1
            self.actions.popleft()

    def accepts_packet(self, packet, recv_action):
        if recv_action.packet_id != packet.packet_id:
            return False
        if self.name != packet.destination:
            return False
        if recv_action.sender != packet.sender:
            return False
        return True

    def handle_action(self, action):
        if isinstance(action, SendAction):
            packet = Packet(self.name, action.destination, action.packet_id)
            self.packet_pool.append(packet)
            return True
        elif isinstance(action, ReceiveAction):
            for i in reversed(xrange(len(self.packet_pool))):
                packet = self.packet_pool[i]
                if self.accepts_packet(packet, action):
                    del self.packet_pool[i]
                    return True
            return False
        elif isinstance(action, PrintAction):
            print 'printed {name} {message} {time}'.format(
                name=self.name, message=action.payload, time=self.clock)
            return True
        elif isinstance(action, MutexStartAction):
            raise NotImplementedError
        elif isinstance(action, MutexEndAction):
            raise NotImplementedError


def parse_input(infile, packet_pool=None):
    process_name = None
    process_actions = collections.deque()
    packet_pool = collections.deque() if packet_pool is None else packet_pool
    lines = (line.lower().strip() for line in infile if line.strip())
    for lineno, line in enumerate(lines, start=1):
        tokens = line.split()
        if line.startswith('begin process'):
            process_name = tokens[2]
        elif line.startswith('end process'):
            yield Process(process_name, process_actions, packet_pool)
            process_name = None
            process_actions = collections.deque()
        elif line.startswith('begin mutex'):
            process_actions.append(MutexStartAction())
        elif line.startswith('end mutex'):
            process_actions.append(MutexEndAction())
        elif line.startswith('send'):
            process_actions.append(SendAction(tokens[1], tokens[2]))
        elif line.startswith('recv'):
            process_actions.append(ReceiveAction(tokens[1], tokens[2]))
        elif line.startswith('print'):
            process_actions.append(PrintAction(tokens[1]))
        else:
            logging.warning(
                'ignoring unknown command: "{command}" '
                'on line {lineno} in file {filepath}'.format(
                    command=line, lineno=lineno, filepath=infile.name))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType())
    args = parser.parse_args()
    infile = args.infile

    try:
        packet_pool = collections.deque()
        processes = list(parse_input(infile, packet_pool))
        while not all(process.is_done for process in processes):
            for process in processes:
                process.execute_next()
    finally:
        infile.close()
