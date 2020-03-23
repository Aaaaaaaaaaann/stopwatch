#!/bin/env python3.8

import tkinter as tk
import datetime
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

days_of_week = {0: 'Mon',
                1: 'Tue',
                2: 'Wed',
                3: 'Thu',
                4: 'Fri',
                5: 'Sat',
                6: 'Sun'}


class Stopwatch:
    def __init__(self, master):
        self.date = None
        self.task = None
        self.working_time = datetime.datetime.strptime('00:00:00', '%H:%M:%S').strftime('%H:%M:%S')
        self.start_time = None
        self.stop_time = None
        self.pauses = 0
        self.pause_duration = 0
        self.day_of_week = None
        self.current_process = None
        self.last_called_func = None

        self.master = master
        self.task_label = tk.Label(master, font=('', 12), bg='#ffe3ed', fg='#A64A6A', text='Task:')
        self.task_entry = tk.Text(master, font=('', 12, 'bold'), bg='#ffe3ed', fg='#A64A6A', width=20, height=2)
        self.time_label = tk.Label(master, font=('', 36), bg='#ffe3ed', fg='#A64A6A', text=f'{self.working_time}')
        self.start_button = tk.Button(master, image=PLAY, command=self.start_event, bg='#ffe3ed', activebackground='#fff0f5')
        self.pause_button = tk.Button(master, image=PAUSE, command=self.pause_event, bg='#ffe3ed', activebackground='#fff0f5')
        self.stop_button = tk.Button(master, image=STOP, command=self.stop, bg='#ffe3ed', activebackground='#fff0f5')

        self.task_label.grid(row=0, column=0, columnspan=1, padx=10, pady=10)
        self.task_entry.grid(row=0, column=1, columnspan=5, padx=10, pady=25)
        self.time_label.grid(row=1, column=0, columnspan=6, padx=10, pady=10)
        self.start_button.grid(row=4, column=1, pady=15)
        self.pause_button.grid(row=4, column=2, pady=15)
        self.stop_button.grid(row=4, column=3, pady=15)

        self.start_button.configure(state='normal')
        self.pause_button.configure(state='disabled')
        self.stop_button.configure(state='disabled')

    def start_event(self):
        if self.current_process:
            root.after_cancel(self.current_process)
            self.pauses += 1
        if not self.start_time:
            self.start_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.last_called_func = sys._current_frames().values()
        self.start_button.configure(state=tk.DISABLED)
        self.pause_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.NORMAL)
        self.start_action()

    def start_action(self):
        self.current_process = root.after(1000, self.start_action)
        time_parts = [int(i) for i in str(self.working_time).split(':')]
        seconds = time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
        seconds += 1
        self.working_time = datetime.datetime.strptime(f'{seconds // 60 // 60}:{seconds // 60 % 60}:{seconds % 60}', '%H:%M:%S').strftime('%H:%M:%S')
        self.time_label.configure(text=f'{self.working_time}')

    def pause_event(self):
        self.last_called_func = sys._current_frames().values()
        self.start_button.configure(state=tk.NORMAL)
        self.pause_button.configure(state=tk.DISABLED)
        self.start_button.configure(state=tk.NORMAL)
        self.pause_action()

    def pause_action(self):
        root.after_cancel(self.current_process)
        self.current_process = root.after(1000, self.pause_action)
        self.pause_duration += 1

    def stop(self):
        root.after_cancel(self.current_process)
        self.stop_time = datetime.datetime.now().strftime('%H:%M:%S')
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        if 'pause' in str(self.last_called_func):
            self.pauses += 1
        if self.pause_duration:
            self.pause_duration = datetime.datetime.strptime(f'{self.pause_duration // 60 // 60}:{self.pause_duration // 60 % 60}:{self.pause_duration % 60}', '%H:%M:%S').strftime('%H:%M:%S')
        self.task = self.task_entry.get('1.0', tk.END)
        self.day_of_week = days_of_week[datetime.date.today().weekday()]
        self.pause_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.DISABLED)
        self.start_button.configure(state=tk.NORMAL)
        self.add_entry_to_db()
        self.__init__(master=None)

    def add_entry_to_db(self):
        connection = psycopg2.connect(dbname=os.getenv('DBNAME'), user=os.getenv('NAME'), host=os.getenv('HOST'), password=os.getenv('PASSWORD'))
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO tasks (date, task, working_time, start_time, stop_time, pauses, pause_duration, day_of_week)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s);''',
                       (self.date, self.task, self.working_time, self.start_time, self.stop_time, self.pauses, self.pause_duration, self.day_of_week))
        connection.commit()
        cursor.close()
        connection.close()


root = tk.Tk()

PLAY = tk.PhotoImage(file='/home/anna/Documents/projects/timer/icons/play.png').subsample(18, 18)
PAUSE = tk.PhotoImage(file='/home/anna/Documents/projects/timer/icons/pause.png').subsample(18, 18)
STOP = tk.PhotoImage(file='/home/anna/Documents/projects/timer/icons/stop.png').subsample(18, 18)

app = Stopwatch(root)
root.title('Stopwatch')
root.configure(bg='#ffe3ed')
root.resizable(False, False)
root.mainloop()
