#!/usr/bin/env python2.7


from collections import deque, namedtuple
import logging


SendAction = namedtuple('SendAction', 'destination payload')
ReceiveAction = namedtuple('ReceiveAction', 'sender payload')
PrintAction = namedtuple('PrintAction', 'payload')
MutexStartAction = namedtuple('MutexStartAction', '')
MutexEndAction = namedtuple('MutexEndAction', '')

Packet = namedtuple('Packet', 'sender destination payload timestamp')


class Process(object):
    def __init__(self, pid, actions, message_channel):
        self.pid = pid
        self.actions = actions
        self.message_channel = message_channel
        self.clock = 0

    @property
    def is_done(self):
        return len(self.actions) == 0

    def __repr__(self):
        return 'Process(pid={pid}, actions={actions})'.format(
            pid=self.pid, actions=self.actions)

    def execute_next(self):
        if self.is_done:
            return
        if self.handle_action(self.actions[0]):
            self.actions.popleft()

    def handle_action(self, action):
        if isinstance(action, SendAction):
            self.clock += 1
            packet = Packet(
                sender=self.pid,
                destination=action.destination,
                payload=action.payload,
                timestamp=self.clock)
            self.message_channel.append(packet)
            print 'sent {pid} {payload} {destination} {time}'.format(
                pid=self.pid, payload=packet.payload,
                destination=packet.destination, time=self.clock)
            return True

        elif isinstance(action, ReceiveAction):
            for i in reversed(xrange(len(self.message_channel))):
                packet = self.message_channel[i]
                if packet.sender != action.sender:
                    continue
                if packet.destination != self.pid:
                    continue
                if packet.payload != action.payload:
                    continue
                self.clock += 1
                self.clock = max(self.clock, packet.timestamp)
                print 'received {pid} {payload} {time}'.format(
                    pid=self.pid, payload=packet.payload, time=self.clock)
                del self.message_channel[i]
                return True
            else:
                return False

        elif isinstance(action, PrintAction):
            self.clock += 1
            print 'printed {pid} {payload} {time}'.format(
                pid=self.pid, payload=action.payload, time=self.clock)
            return True

        elif isinstance(action, MutexStartAction):
            raise NotImplementedError

        elif isinstance(action, MutexEndAction):
            raise NotImplementedError


def parse_input(infile, message_channel=None):
    process_name = None
    process_actions = deque()
    message_channel = deque() if message_channel is None else message_channel
    lines = (line.lower().strip() for line in infile if line.strip())
    for lineno, line in enumerate(lines, start=1):
        tokens = line.split()
        if line.startswith('begin process'):
            process_name = tokens[2]
        elif line.startswith('end process'):
            yield Process(process_name, process_actions, message_channel)
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
