#!/usr/bin/env python2.7


import collections
import logging


SendAction = collections.namedtuple('SendAction', 'destination message')
ReceiveAction = collections.namedtuple('ReceiveAction', 'sender message')
PrintAction = collections.namedtuple('PrintAction', 'payload')
MutexStartAction = collections.namedtuple('MutexStartAction', '')
MutexEndAction = collections.namedtuple('MutexEndAction', '')


class Process(object):
    def __init__(self, name, actions, event_queue):
        self.name = name
        self.actions = actions
        self.event_queue = event_queue
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
        action = self.actions.popleft()
        self.handle_action(action)

    def handle_action(self, action):
        self.clock += 1
        if isinstance(action, SendAction):
            raise NotImplementedError
        elif isinstance(action, ReceiveAction):
            raise NotImplementedError
        elif isinstance(action, PrintAction):
            print 'printed {name} {message} {time}'.format(
                name=self.name, message=action.payload, time=self.clock)
        elif isinstance(action, MutexStartAction):
            raise NotImplementedError
        elif isinstance(action, MutexEndAction):
            raise NotImplementedError


def parse_input(infile, event_queue=None):
    process_name = None
    process_actions = collections.deque()
    event_queue = collections.deque() if event_queue is None else event_queue
    lines = (line.lower().strip() for line in infile)
    for lineno, line in enumerate(lines, start=1):
        tokens = line.split()
        if line.startswith('begin process'):
            process_name = tokens[2]
        elif line.startswith('end process'):
            yield Process(process_name, process_actions, event_queue)
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
        event_queue = collections.deque()
        processes = list(parse_input(infile, event_queue))
        while not all(process.is_done for process in processes):
            for process in processes:
                process.execute_next()
    finally:
        infile.close()
