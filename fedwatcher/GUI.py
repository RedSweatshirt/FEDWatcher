import tkinter
import tkinter.filedialog
from tkinter import messagebox as tkMessageBox
import os
import pandas as pd
import numpy as np
import tkinter.ttk as ttk
import datetime
from configparser import ConfigParser
from src.fedwatcher import Fedwatcher
import re
import datetime

class App():
	def __init__(self, window, window_title):
		# aesthetics -------
		self.window = window
		self.window.title(window_title)
		self.bg_color = "#424547"
		self.fg_color = "#E1ECF2"
		self.window.configure(bg=self.bg_color)
		self.button_color = "#7E8487"
		self.start_color = "#C9FFCB"
		self.stop_color = "#FF959D"
		self.button_width = 30

		# menu left -------
		# also explore menu bar ?
		# https://pythonspot.com/tk-menubar/
		self.menu_left = tkinter.Frame(self.window, width=80, bg=self.bg_color)
		self.menu_left_upper = tkinter.Frame(self.menu_left, width=80, height=80, bg=self.bg_color)
		self.menu_left_lower = tkinter.Frame(self.menu_left, width=80, bg=self.bg_color)

		self.menu_left_title = tkinter.Label(self.menu_left_upper,
		 text="FEDWatcher",
		 font=("Helvetica", 16), bg=self.bg_color, fg = self.fg_color)
		self.menu_left_title.grid(row=0,column=0)

		self.menu_left_upper.pack(side="top", fill="both", expand=True)
		self.menu_left_lower.pack(side="top", fill="both", expand=True)


		self.exp_name = tkinter.Label(self.menu_left_upper,
		 text="Exp. Name:", pady=5, bg=self.bg_color, width=10, fg = self.fg_color)
		self.exp_entry = tkinter.Entry(self.menu_left_upper, width=20)
		self.treatment_label = tkinter.Label(self.menu_left_upper,
		 text="Treatment:", pady=5, bg=self.bg_color, width=10, fg = self.fg_color)
		#self.treatment_entry = tkinter.Entry(self.menu_left_upper, width=20)
		#self.dose_label = tkinter.Label(self.menu_left_upper,
		# text="Dose:", pady=5, bg=self.bg_color, width=10)
		#self.dose_entry = tkinter.Entry(self.menu_left_upper, width=20)
		#self.comment_label = tkinter.Label(self.menu_left_upper,
		# text="Comment:", pady=5, bg=self.bg_color, width=10)
		#self.comment_entry = tkinter.Entry(self.menu_left_upper, width=20)


		# make the grid of entries
		self.exp_name.grid(row=1, column=0,sticky="ne")
		#self.treatment_label.grid(row=2,column=0,sticky="ne")
		#self.dose_label.grid(row=3, column=0, sticky="ne")
		#self.comment_label.grid(row=4,column=0,padx=1, sticky="ne")
		self.exp_entry.grid(row=1,column=1, sticky='ew',padx=1)
		#self.treatment_entry.grid(row=2,column=1, sticky='ew',padx=1)
		#self.dose_entry.grid(row=3,column=1, sticky='ew',padx=1)
		#self.comment_entry.grid(row=4,column=1, sticky='ew',padx=1)

		# insert and delete stuff -------
		#self.insert_button = tkinter.Button(self.menu_left_upper, text="Insert",
		#                                    command=self.insert_data,
		#                                    width=4, bg=self.button_color,
		#                                    highlightbackground="black")
		#self.delete_button = tkinter.Button(self.menu_left_upper, text='Delete',
        #                               command=self.delete_entry,
        #                               state=tkinter.DISABLED,
        #                               width=4, bg=self.button_color,
        #                               highlightbackground="black")
		# make an empty label for space
		self.spacer_label = tkinter.Label(self.menu_left_upper,
		 text="", pady=5, bg=self.bg_color, width=2)
		self.spacer_label.grid(row=0,column=2, pady=5)
		#self.insert_button.grid(row=4,column=3, pady=5)
		#self.delete_button.grid(row=4,column=4, sticky='nsew', pady=5)

		# right area ----------
		self.frame = tkinter.Frame(self.window, bg=self.bg_color)

		self.menu_right_title = tkinter.Label(self.frame,
		 text="Experiment Control", bg=self.bg_color, fg = self.fg_color,
		font=("Helvetica", 16))
		self.menu_right_title.pack()
	
		# Buttons -----
		self.create_project = tkinter.Button(self.frame,
		 text="Create Project",
		 command=self.create_new_project,
		 pady=20, bg=self.button_color,fg = self.fg_color, 
		highlightbackground="black",
		width = self.button_width)
		self.create_project.pack(pady=5)
		# load previous button
		self.load_previous = tkinter.Button(self.frame,
		 text="Load Project",
		 command=self.load_config,
		 pady=20, bg=self.button_color, fg = self.fg_color,
		highlightbackground="black",
		width = self.button_width)
		self.load_previous.pack(pady=5)
		# start experiment
		self.exp_button = tkinter.Button(self.frame,
		 text="Start Experiment",
		 command=self.start_experiment,
		 state=tkinter.DISABLED,
		 pady=20, bg=self.start_color, fg = self.fg_color, activebackground = "#00B306",
		highlightbackground="black",
		width = self.button_width)
		self.exp_button.pack(pady=5)
		# stop experiment
		self.exp_stop_button = tkinter.Button(self.frame,
		 text="Stop Experiment",
		 command=self.stop_experiment,
		 state=tkinter.DISABLED,
		 pady=20, bg=self.stop_color, fg = self.fg_color, activebackground='#E61523',
		highlightbackground="black",
		width = self.button_width)
		self.exp_stop_button.pack(pady=5)

		# on closing, ask before closing
		self.window.protocol("WM_DELETE_WINDOW", self.on_closing)


		self.menu_left.grid(row=0, column=0, sticky="nsew")
		self.frame.grid(row=0, column=1, sticky="nsew")
		#self.canvas_area.grid(row=1, column=1, sticky="nsew") 
		#self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

		# this gives priority to entry boxes
		# because of this, they will resize and fill space with the menu_left_upper
		self.menu_left_upper.grid_columnconfigure(1, weight=1)

		# Start FEDWatcher ---
		self.fw = Fedwatcher()


	def get_mac(self):
		# This is good for Raspberry PIs, not good for other OS !
		# possible interfaces ['wlan0', 'eth0']
		#try:
		path_to_mac = '/sys/class/net/'+ 'wlan0' +'/address'
		mac = open(path_to_mac).readline()
		mac = mac.replace("\n", "")
		#except:
		#	try:
				# interface wlp2s0 for debugging outside of Pi
		#		mac=open('/sys/class/net/wlp2s0/address').readline()
		#	except:
		#		mac = "00:00:00:00:00:00"
		# mac = mac[0:17]
		return mac


	# def insert_data(self):
	# 	"""
	# 	Insertion method.
	# 	"""
	# 	self.treeview.insert('', 'end',
	# 	                     values=(
	# 	                     	self.get_mac(),
	# 	                     	datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
	# 	                     	self.exp_entry.get(),
	# 	                     	self.treatment_entry.get(),
	# 	                        self.dose_entry.get(),
	# 	                        self.comment_entry.get()))
	# 	# enable button to delete
	# 	self.delete_button.configure(state=tkinter.NORMAL)

	# def delete_entry(self):
	# 	selected_items = self.treeview.selection()        
	# 	for selected_item in selected_items:          
	# 		self.treeview.delete(selected_item)

	# button callbacks ------
	def create_new_project(self):
		self.all_set = self.check_input()
		if self.all_set:
			# choose directories first
			self.rootdir = tkinter.filedialog.askdirectory(title="Choose Project Directory")
			self.exp_dir = os.path.join(self.rootdir, self.exp_entry.get())
			# create directory if needed
			if not os.path.isdir(self.exp_dir):
				print("Creating Experiment Directory within Project Directory")
				os.mkdir(self.exp_dir)
			# create the config
			self.create_config()
			self.exp_button.config(state="normal")
		return


	def load_config(self):
		# choose directories first
		self.exp_dir = tkinter.filedialog.askdirectory(title="Choose Previous Experiment Directory")
		#self.expdir = os.path.join(self.rootdir, self.exp_entry.get())
		# check for previous configs
		files = os.listdir(self.exp_dir)
		# get config files in exp folder
		configs = [file for file in files if "config" in file]
		if len(configs) > 0:
			print("Adding new session to previous experiment")
			# get the old experiment name from the folder structure
			exp_name = os.path.basename(os.path.dirname(self.exp_dir))
			self.exp_entry.delete(0, tkinter.END)
			self.exp_entry.insert(0, exp_name)
			# Create config
			self.create_config()
			# only now we enable the experiment button
			self.exp_button.config(state="normal")
			self.all_set = True 
		else:
			print("No previous configuration found. Create a new project")
			self.create_new_project()

	def start_experiment(self):
		self.exp_stop_button.config(state="normal") 
		if self.all_set:
			# self.save_data()
			self.fw.run(configpath=self.configpath)
		else:
			tkinter.messagebox.showinfo("Something went wrong",
			 "This will never happen (?)")


	def check_input(self):
		entry = self.exp_entry.get()
		accepted_patterns = re.compile(r'[a-zA-Z_0-9]')
		rejected = [char for char in entry if not accepted_patterns.match(char)]
		if len(rejected) > 0:
			tkinter.messagebox.showinfo("Name Not Accepted", "Please only use alphanumeric characters in your experiment name. No spaces or symbols.")
			return False
		else:
			return True



	def on_closing(self):
		if tkMessageBox.askyesno("Quit", "Do you want to quit?"):
			# this first stops fedwatcher, fedwatcher will handle data saving
			self.fw.close()
			self.window.destroy()

	def read_credentials(self):
		# This should read credentials for email and do something about it
		return

	def create_config(self):
		# Get session number
		self.session_n = self.make_session_n()
		# make proper config name
		self.configpath = os.path.join(self.exp_dir, "config_" + self.session_n + ".yaml")


		# Create config
		config = ConfigParser()
		config.read(self.configpath)
		config.add_section('fedwatcher')
		config.set('fedwatcher', 'exp_name', self.exp_entry.get())
		config.set('fedwatcher', 'root_dir', self.rootdir)
		config.set('fedwatcher', 'exp_dir', self.exp_dir)
		config.set('fedwatcher', 'session_num', self.session_n)
		config.set('fedwatcher', 'exp_start', datetime.datetime.now().replace(microsecond=0).isoformat())

		# TODO: add 
		# if check_input():
			# write
		# else:
			# throw error 
		with open(self.configpath, 'w') as f:
			config.write(f)
		return "Config was saved"

	def make_session_n(self):
		'''
		This function lists the configs in the directory and returns a proper session number as string
		This strig gets appended to the end of the config yaml to denote sessions
		'''
		files = os.listdir(self.exp_dir)
		# get config files in exp folder
		configs = [file for file in files if "config" in file]
		# if there's no config (new project)
		if len(configs) < 1:
			new_session = "00"
		else:
			# looking for two digits here
			pattern = re.compile(r'\d{2}')
			# find the stuff
			number_match = [pattern.findall(x) for x in configs]
			# transform to integer and do the math
			session_int = [int(x[0]) for x in number_match if len(x) > 0]
			session_max = max(session_int)
			new_session = str(session_max + 1).zfill(2)
		return new_session

	def stop_experiment(self):
		# TODO: add date of stopping the session
		# this stops fedwatcher but doesn't close ports
		self.fw.stop()
		print("Fedwatcher has been stopped!")
		return


def create_app(root):
	App(window = root, window_title = "Experiment GUI")

if __name__ == '__main__':
	# hard-coded current directory
	#os.chdir("/home/pi/homecage_quantification")
	root = tkinter.Tk()
	# widthxheight+300+300 pxposition from the leftcorner of the monitor
	root.geometry("800x350+300+300")
	# resize columns with window
	root.columnconfigure(0, weight=1, minsize=200)
	root.columnconfigure(1, weight=1, minsize=200)
	# set minimum height for row 0 and 2
	root.rowconfigure(0, minsize=50)
	root.rowconfigure(2, minsize=20)
	# set window min size
	root.minsize(520, 40)
	root.after(0, create_app, root)
	root.mainloop()
	
