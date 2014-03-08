#!/usr/bin/env python2.7


from collections import deque, namedtuple
import logging


SendAction = namedtuple('SendAction', 'destination packet_id')
ReceiveAction = namedtuple('ReceiveAction', 'sender packet_id')
PrintAction = namedtuple('PrintAction', 'payload')
MutexStartAction = namedtuple('MutexStartAction', '')
MutexEndAction = namedtuple('MutexEndAction', '')

Packet = namedtuple('Packet', 'sender destination packet_id timestamp')


class Process(object):
    def __init__(self, name, actions, packet_pool):
        self.name = name
        self.actions = actions
        self.packet_pool = packet_pool
        self.clock = 0

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
            self.actions.popleft()

    def handle_action(self, action):
        if isinstance(action, SendAction):
            self.clock += 1
            self.packet_pool.append(Packet(
                sender=self.name,
                destination=action.destination,
                packet_id=action.packet_id,
                timestamp=self.clock))
            return True

        elif isinstance(action, ReceiveAction):
            for i in reversed(xrange(len(self.packet_pool))):
                packet = self.packet_pool[i]
                if packet.sender != action.sender:
                    continue
                if packet.destination != self.name:
                    continue
                if packet.packet_id != action.packet_id:
                    continue
                self.clock += 1
                self.clock = max(self.clock, packet.timestamp)
                del self.packet_pool[i]
                return True
            else:
                return False

        elif isinstance(action, PrintAction):
            self.clock += 1
            print 'printed {name} {message} {time}'.format(
                name=self.name, message=action.payload, time=self.clock)
            return True

        elif isinstance(action, MutexStartAction):
            raise NotImplementedError

        elif isinstance(action, MutexEndAction):
            raise NotImplementedError


def parse_input(infile, packet_pool=None):
    process_name = None
    process_actions = deque()
    packet_pool = deque() if packet_pool is None else packet_pool
    lines = (line.lower().strip() for line in infile if line.strip())
    for lineno, line in enumerate(lines, start=1):
        tokens = line.split()
        if line.startswith('begin process'):
            process_name = tokens[2]
        elif line.startswith('end process'):
            yield Process(process_name, process_actions, packet_pool)
            process_name = None
            process_actions = deque()
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
        processes = list(parse_input(infile))
        while not all(process.is_done for process in processes):
            for process in processes:
                process.execute_next()
    finally:
        infile.close()
