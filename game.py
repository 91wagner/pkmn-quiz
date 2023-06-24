from ctypes import alignment
from glob import glob
from socketserver import ThreadingUDPServer
from tkinter import *
import math
import time
#import pypokedex
import threading
from os.path import exists
from os import remove


import poke_gen1 as pg1
import poke_gen2 as pg2
import poke_gen3 as pg3
import poke_gen4 as pg4
import poke_gen5 as pg5
import poke_gen6 as pg6
import poke_gen7 as pg7
import poke_gen8 as pg8
import poke_gen9 as pg9

from localization import *

class Game:
    # class variables
    total_gen_number = 9
    
    # databases
    gen_name_all = [pg.gen_name_all for pg in [pg1, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9]]
    gen_name_eng = [pg.gen_name_eng for pg in [pg1, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9]]
    gen_name_ger = [pg.gen_name_ger for pg in [pg1, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9]]
    gen_id_all = [pg.gen_id_all for pg in [pg1, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9]]
    gen_id_eng = [pg.gen_id_eng for pg in [pg1, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9]]
    gen_id_ger = [pg.gen_id_ger for pg in [pg1, pg2, pg3, pg4, pg5, pg6, pg7, pg8, pg9]]

    # colors
    gen_colors = ["black", "blue", "red", "green", "orange", "purple", "brown", "cyan", "violet"]
    timer_label_color = "gray70"

    # filenames
    highscore_location = "highscore.txt"
    settings_location = "settings.txt"

    # constructor
    def __init__(self):    
        
        self.maxtime = 0 
        """starting time in seconds"""
        self.time_needed = 0
        """current time needed in 0.1s"""
        
        self.current_game_id = 0
        self.gen_number = 1
        self.gens_active = [1]
        for i in range(1,Game.total_gen_number):
            self.gens_active.append(0)
        self.language = loc.getLanguage("ger")

        self.progress = [] # for save-state, will be filled during LoadProgress and used/reset during BuildList
        self.loaded_progress = False

        self.in_order_mode = 0
        self.previous_completed = True
        """Only for in-order-mode and language "all" needed"""
        

        self.current_gens_name_all =  Game.gen_name_all[0]
        self.current_gens_name_eng =  Game.gen_name_eng[0]
        self.current_gens_name_ger =  Game.gen_name_ger[0]
        self.current_gens_id_all = Game.gen_id_all[0]
        self.current_gens_id_eng = Game.gen_id_eng[0]
        self.current_gens_id_ger = Game.gen_id_ger[0]

        self.current_gens_name = self.current_gens_name_all
        self.current_gens_id = self.current_gens_id_all


        self.window = Tk()
        self.running = False
        self.paused = False
        self.pause_time = 0 
        """time at which game was paused, in 0.1s"""
        self.success = False
        self.given_up = False
        self.out_of_time = False
        self.turning_off = False
        self.settings_open = False
        self.found_answers = 0
        # self.found_answers_all = [0]*(loc.number_languages-1)

        self.settings_text = StringVar(value=self.language.settings)

        self.pause_block = Label(text=self.language.paused, width=52, height=13, font=("Arial",30,"bold"))
        self.loading_block = Label(text=self.language.loading, width=52, height=13, font=("Arial",30,"bold"), background="LightSkyBlue1")
 
        self.xwindow = 1250
        self.ywindow = 650
        self.xwindowsmall = 1250
        self.ywindowsmall = 650
        self.xwindowbig = 1800
        self.ywindowbig = 1000
        self.windowbig = False
        self.window.title(f"Sporcle: Pokemon Gen {1}")
        self.window.config(bg="LightSkyBlue1")


        self.number_texts = {}
        self.pokemon_texts = {}
        self.pokemon_texts_pos = {}


        self.progress_label = Label(text=f"0 / {len(self.current_gens_id)}", width=7, font=("Arial", 25, 'bold'), anchor="e", background=Game.timer_label_color)
        self.progress_label.pack()
        self.progress_label.place(x=420, y=5)


        self.timer_label = Label(text=f"{self.maxtime//60}:{self.maxtime%60}", font=("Arial", 25, "bold"), width=5, justify="right", background=Game.timer_label_color)
        self.timer_label.pack()
        self.timer_label.place(x=575, y=5)


        self.highscore_values = []
        self.highscore_times = []
        self.highscore_in_order_mode = [0 for i in range(0,pow(2,Game.total_gen_number))]

        # read in highscores from file
        for i in range(0,loc.number_languages):
            self.highscore_values.append([0 for i in range(0,pow(2,Game.total_gen_number))])
            self.highscore_times.append([100000000 for i in range(0,pow(2,Game.total_gen_number))])

        if exists(Game.highscore_location):
            with open(Game.highscore_location, mode="rb") as file:
                d = file.read()
                lines = d.decode().split("\n")
                for ilang in range(0,loc.number_languages):
                    self.highscore_values[ilang] = [int(i) for i in lines[2*ilang].split()]
                    self.highscore_times[ilang] = [int(i) for i in lines[2*ilang+1].split()]
                self.highscore_in_order_mode = [int(i) for i in lines[2*loc.number_languages].split()]

        self.highscore_label = Label(text=self.language.highscore + ": ", bg="LightSkyBlue1")
        self.highscore_label.pack()
        self.highscore_label.place(x=5, y=49)
        
        self.input_field = Entry(font=("Arial", 25), width=15, validate="all", background="white")

        self.input_function = self.input_field.register(self.StartCheckInput)
        self.input_field.config(validatecommand=(self.input_function, '%P'))
        self.input_field.pack()
        self.input_field.place(x=120, y=5)
        self.input_field["state"] = "disabled"
     
        self.giveup_button = Button(text=self.language.giveup, width=10, height=1, font=("Arial",15,"bold"), command=self.GiveupButton)
        self.giveup_button.pack()
        self.giveup_button.place(x=self.xwindow-270, y=5)

        self.start_button = Button(text=self.language.start, width=8, height=1, font=("Arial",15,"bold"), command=self.StartButton)
        self.start_button.pack()
        self.start_button.place(x=5, y=5)


        self.exit_button = Button(text=self.language.exit, width=10, height=1, font=("Arial",15,"bold"), command=self.ExitButton)
        self.exit_button.pack()
        self.exit_button.place(x=self.xwindow-135, y=5)

        self.language_label = Label(text=self.language.name, width=12, height=1, font=("Arial",12,"bold"))
        self.language_label.pack()
        self.language_label.place(x=self.xwindow-560, y=25)

        self.gen_label = Label(text=f"Gen 1", width=12, height=1, font=("Arial",12,"bold"))
        self.gen_label.pack()
        self.gen_label.place(x=self.xwindow-560, y=5)

        self.input_field.bind('<Control-BackSpace>', self.DeleteInput)

        self.settings_button = Button(textvariable=self.settings_text, command=self.SettingsButton, width=12, height=1, font=("Arial",15,"bold"))
        self.settings_button.pack()
        self.settings_button.place(x=self.xwindow-429, y=5)

        # read old settings
        if exists(Game.settings_location):
            with open(Game.settings_location, mode="rb") as file:
                print("Read old settings file")
                d = file.read()
                lines = d.decode().split("\n")
                self.gen_number = int(lines[0])
                self.gens_active = []
                for i in range(0,len(lines[1])):
                    self.gens_active.append(ord(lines[1][i]) - ord("0"))
                self.in_order_mode = int(lines[2])
                self.language = loc.getLanguage(lines[3])
                self.LoadGen(self.gens_active.copy())
                if lines[4] == "0":
                    self.windowbig = False
                else:
                    self.windowbig = True
        else:
            self.GenButton(self.gen_number)

        self.LoadProgress()

        self.UpdateWindowSize()
        self.LanguageButton() # use self.language.tag
        self.AddLoadingBlock()
        if self.loaded_progress:
            self.UpdateTimer(self.pause_time//10)
        else:
            self.UpdateTimer(self.maxtime)
        self.UpdateProgress()
        self.UpdateHighscore() 
        # print("Current game ID: ", self.current_game_id)
        self.BuildList()
        self.RemoveLoadingBlock()

        if len(self.progress) != 0:
            self.progress = []
            self.StartButton() # start
            self.StartButton() # pause
            self.loaded_progress = False
            

        self.window.mainloop()

    def UpdateWindowSize(self):
        if self.windowbig:
            self.xwindow = self.xwindowbig
            self.ywindow = self.ywindowbig
            self.pause_block["width"] = 75
            self.pause_block["height"] = 21
            self.loading_block["width"] = 75
            self.loading_block["height"] = 21
        else:
            self.xwindow = self.xwindowsmall
            self.ywindow = self.ywindowsmall
            self.pause_block["width"] = 52
            self.pause_block["height"] = 13
            self.loading_block["width"] = 52
            self.loading_block["height"] = 13
        self.window.minsize(width=self.xwindow, height=self.ywindow)

    # binary number with 1 at position i if gen i is enabled, 0 otherwise
    def CalculateCurrentGameID(self):
        self.current_game_id = 0
        for i in range(0,Game.total_gen_number):
            if self.gens_active[i] == 1:
                self.current_game_id += pow(2, i)
        return self.current_game_id

    # options window
    def SettingsButton(self):

        if self.settings_open or self.running:
            return
        
        self.settings_open = True
        self.settings_window = Toplevel(self.window, padx=20, pady=5)
        self.settings_window.geometry("340x480")

        self.settings_window.title(self.language.settings)

        igens = []
        def EmptyCombinations():
            for igen in igens:
                igen.set(0)

        # gen settings
        Label(self.settings_window, text=self.language.choose_gen+":", width=20, height=1, anchor="nw").grid(column=0, row=0, columnspan=6, sticky="w")
        gen_radio_var = IntVar(self.settings_window, self.gen_number)
        for i in range(0,Game.total_gen_number+1):
            gentext = f"Gen {i}"
            if i == 0:
                gentext = self.language.combination
                Radiobutton(self.settings_window, text=gentext, value=i, variable=gen_radio_var).grid(column=3, row=0, columnspan=2, sticky="e")
            else:
                Radiobutton(self.settings_window, text=gentext, value=i, variable=gen_radio_var, command=EmptyCombinations).grid(column=(i-1)%5, row=1+(i-1)//5)

        def ChangeRadiobutton():
            gen_radio_var.set(0)
        # multiple gens
        Label(self.settings_window, text=self.language.multiple_gen, width=40, height=2, anchor="w", justify="left").grid(column=0, row=3, columnspan=6, sticky="w", pady=(15,0))
        for i in range(1,Game.total_gen_number+2):
            gentext = f"Gen {i}"
            if i == Game.total_gen_number+1:
                gentext = self.language.all
            igen = IntVar()
            igens.append(igen)
            if self.gen_number == 0 and i != Game.total_gen_number+1 and self.gens_active[i-1]:
                igen.set(1)
            Checkbutton(self.settings_window, text=gentext, variable=igen, command=ChangeRadiobutton).grid(column=(i-1)%5, row=4+(i-1)//5, sticky="w")

        # in order mode
        Label(self.settings_window, text=self.language.in_order_text+":", width=40, height=2, anchor="w", justify="left").grid(column=0, row=6, columnspan=6, sticky="w", pady=(30,0))
        in_order_var = IntVar(self.settings_window, self.in_order_mode)
        Checkbutton(self.settings_window, height=1,  text="", width=1, variable=in_order_var).grid(column=1, row=6, columnspan=1, sticky="se")

        # language settings
        Label(self.settings_window, text=self.language.language_text+":", width=20, height=1, anchor="nw").grid(column=0, row=7, columnspan=6, sticky="w", pady=(30,0))
        language_radio_var = IntVar(self.settings_window, self.language.index)
        for i in range(0,loc.number_languages):
            Radiobutton(self.settings_window, text=loc.getLanguageFromIndex(i).name, value=i, variable=language_radio_var).grid(column=2*i, row=8, columnspan=2, sticky="w")

        # confirm button
        def ConfirmSettings():
            self.settings_window.destroy()
            self.in_order_mode = in_order_var.get()
            # print("In order mode: ", in_order_var.get())
            self.AddLoadingBlock()
            if gen_radio_var.get() > 0:
                self.GenButton(gen_radio_var.get())
            else:
                first = True
                for i in range(0,Game.total_gen_number):
                    igenval = igens[i].get()
                    if igenval == 1 or igens[Game.total_gen_number].get() == 1:
                        if first:
                            self.GenButton(i+1)
                            first = False
                        else:
                            self.GenButton(i+1,True)
                        self.gens_active[i] = 1
                    else:
                        self.gens_active[i] = 0
                    self.gen_number = 0
                if first:
                    # no gens selected, but combination was chosen
                    # enter secret game mode:
                    self.current_gens_id_all = {8357 : "Joltik"}
                    self.current_gens_id_eng = {8357 : "Joltik"}
                    self.current_gens_id_ger = {8357 : "Wattzapf"}
                    self.current_gens_name_all = {"joltik" : [(8357, "Joltik")]}
                    self.current_gens_name_eng = {"joltik" : [(8357, "Joltik")]}
                    self.current_gens_name_ger = {"wattzapf" : [(8357, "Wattzapf")]}
                    self.maxtime = 333*60+33
            self.LanguageButton(loc.getLanguageFromIndex(language_radio_var.get()).tag)
            self.start_button["text"] = self.language.start
            
            self.UpdateHighscore()
            self.UpdateTimer(self.maxtime)
            if len(self.progress) != 0:
                self.UpdateTimer(self.pause_time)
            self.UpdateProgress()
            self.BuildList()
            self.RemoveLoadingBlock()
            self.settings_open = False

        self.confirm_button = Button(self.settings_window, text=self.language.confirm, command=ConfirmSettings, width=15, height=2)
        self.confirm_button.grid(column=0, row=10, columnspan=3, pady=(20,0))

        # cancel button
        def CancelSettings():
            self.settings_window.destroy()
            self.settings_open = False

        cancel_button = Button(self.settings_window, text=self.language.cancel, command=CancelSettings, width=15, height=2)
        cancel_button.grid(column=3, row=10, columnspan=3, pady=(20,0))
        self.settings_window.protocol("WM_DELETE_WINDOW", CancelSettings)

        # display credits
        Label(self.settings_window, text=self.language.credits+":", width=8, height=1,  font=('Arial', 14), anchor="w", justify="left").grid(column=0, row=11, columnspan=6, sticky="w", pady=(15,0))
        Label(self.settings_window, text=self.language.credits_text, width=40, height=2, anchor="w", justify="left").grid(column=0, row=12, columnspan=6, sticky="w")

    def DeleteInput(self, event):
        self.input_field.delete(0,END)


    def GenButton(self, new_gen, add=False):
        if self.running:
            return
        self.found_answers = 0

        if add:
            self.gen_number = 0
            self.gens_active[new_gen-1] = 1
            self.gen_label["text"] += f"{new_gen}"
            self.window.title(f"Sporcle: Pokemon Gen X")
            self.current_gens_name_all = {**self.current_gens_name_all,**Game.gen_name_all[new_gen-1]}
            self.current_gens_name_eng = {**self.current_gens_name_eng,**Game.gen_name_eng[new_gen-1]}
            self.current_gens_name_ger = {**self.current_gens_name_ger,**Game.gen_name_ger[new_gen-1]}
            self.current_gens_id_all = {**self.current_gens_id_all,**Game.gen_id_all[new_gen-1]}
            self.current_gens_id_eng = {**self.current_gens_id_eng,**Game.gen_id_eng[new_gen-1]}
            self.current_gens_id_ger = {**self.current_gens_id_ger,**Game.gen_id_ger[new_gen-1]}
        else:
            self.gen_number = new_gen
            for i in range(0,Game.total_gen_number):
                if i+1 == new_gen:
                    self.gens_active[i] = 1
                else:
                    self.gens_active[i] = 0
                self.gen_label["text"] = f"Gen {new_gen}"
                self.window.title(f"Sporcle: Pokemon Gen {new_gen}")
            self.current_gens_name_all = Game.gen_name_all[new_gen-1]
            self.current_gens_name_eng = Game.gen_name_eng[new_gen-1]
            self.current_gens_name_ger = Game.gen_name_ger[new_gen-1]
            self.current_gens_id_all = Game.gen_id_all[new_gen-1]
            self.current_gens_id_eng = Game.gen_id_eng[new_gen-1]
            self.current_gens_id_ger = Game.gen_id_ger[new_gen-1]
        


        if not add:
            self.maxtime = 0
        match new_gen:
            case 1:
                self.maxtime += 20*60
            case 2:
                self.maxtime += 15*60
            case 3:
                self.maxtime += 20*60
            case 4:
                self.maxtime += 15*60
            case 5:
                self.maxtime += 20*60
            case 6:
                self.maxtime += 15*60
            case 7:
                self.maxtime += 15*60
            case 8:
                self.maxtime += 15*60
            case 9: 
                self.maxtime += 20*60
            case _:
                print("ERROR: given generation not supported")


    def LanguageButton(self, lang=""):

        if self.running:
            return

        if lang != "":
            self.language = loc.getLanguage(lang)
        else:
            lang = self.language.tag
        
        if lang == "ger":
            self.current_gens_name = self.current_gens_name_ger
            self.current_gens_id = self.current_gens_id_ger
        elif lang == "eng":
            self.current_gens_name = self.current_gens_name_eng
            self.current_gens_id = self.current_gens_id_eng
        else:
            self.current_gens_name = self.current_gens_name_all
            self.current_gens_id = self.current_gens_id_all

        self.language_label["text"] = self.language.name
        self.exit_button["text"] = self.language.exit
        self.giveup_button["text"] = self.language.giveup
        self.pause_block["text"] = self.language.paused
        self.loading_block["text"] = self.language.loading
        self.settings_text.set(self.language.settings)
        if not self.success and not self.given_up and not self.out_of_time:
            self.start_button["text"] = self.language.start
        else:
            self.start_button["text"] = self.language.restart

        if self.in_order_mode:
            self.language_label["text"] += " \U00002192"



    # exit the GUI
    def ExitButton(self):
        if self.running and not self.given_up and not self.success: # save current status
            self.SaveProgress()
        self.turning_off = True
        self.SaveHighscores()
        self.SaveOldSettings()
        time.sleep(0.2)
        self.window.destroy()
        

    def AddPauseBlock(self):
        if not self.paused:
            self.pause_block.lift()
            self.pause_block.place(x=0,y=70)

    def RemovePauseBlock(self):
        if self.paused:
            self.pause_block.place_forget()
    
    
    def AddLoadingBlock(self):
        self.loading_block.lift()
        self.loading_block.place(x=0,y=50)

    def RemoveLoadingBlock(self):
        self.loading_block.place_forget()

    def StartButton(self):

        if self.settings_open:
            return

        # start game
        if not self.running and not self.paused:
            self.running = True
            self.paused = False
            self.start_button["text"] = self.language.pause
            self.exit_button["text"] = self.language.save
            if not self.loaded_progress:
                self.found_answers = 0
                self.time_needed = 0 # time in 0.1s
            self.input_field["state"] = "normal"
            self.input_field.focus()
            self.timer_label.config(background=Game.timer_label_color)
            self.progress_label.config(background=Game.timer_label_color)
            
            # restart game
            if self.given_up or self.success or self.out_of_time:
                self.success = False 
                self.given_up = False
                self.out_of_time = False
                self.previous_completed = True
                self.input_field.delete(0, END)
                self.progress_label["text"] = f"0 / {len(self.current_gens_id)}"
                for pokemontext in self.pokemon_texts.values():
                    pokemontext["fg"] = "black"
                    pokemontext["text"] = ""
                    pokemontext["bg"] = "white"
            
            if not self.loaded_progress:    
                self.TimerClock(self.maxtime*10)
            return

        # pause game
        if self.running and not self.paused:
            self.AddPauseBlock()
            self.paused = True
            self.input_field["state"] = "disabled"
            self.start_button["text"] = self.language.continu
            return
        
        # continue game
        if self.running and self.paused:
            self.RemovePauseBlock()
            self.paused = False        
            self.RemovePauseBlock()
            self.start_button["text"] = self.language.pause
            self.input_field["state"] = "normal"
            self.input_field.focus()
            self.TimerClock(self.pause_time)
            return
    
    def TimerClock(self, i):
        """ 'i' is the current game time in 0.1s"""

        if i == 600: # <=60 seconds in yellow
            self.timer_label.config(foreground="yellow")
        if i == 100: # <=10 seconds in red
            self.timer_label.config(foreground="red")
        self.UpdateTimer(i//10) # display timer in seconds -> integer division
        if i == 0:
            self.out_of_time = True
        if self.success or self.turning_off or self.given_up or self.out_of_time:
            self.EndGame()
            return
        self.time_needed += 1
        self.pause_time = i
        if self.paused:
            return
        else:
            self.window.after(100, lambda: self.TimerClock(i-1)) # update ever 100ms = 0.1s


    def UpdateTimer(self, i):
        """ 'i' is time in seconds!"""
        minutes = '{:02}'.format(i//60)
        seconds = '{:02}'.format(i%60)
        self.timer_label["text"] = (f"{minutes}:{seconds}")
        self.timer_label.update()


    def EndGame(self):

        self.timer_label.config(foreground="black")
        # if not self.given_up and not self.success:
        #     self.out_of_time = True

        if self.given_up or self.out_of_time:
            self.timer_label.config(background="red")
            
        if self.out_of_time:
            self.timer_label["text"] = ("00:00")
            self.GiveupButton()
        
        if self.success:
            self.timer_label.config(background="green")
            self.progress_label.config(background="green")
            all_green = True
            if self.language.tag == "all":
                # check if all texts are green
                for dexnumber, pokemontext in self.pokemon_texts.items():            
                    if pokemontext["foreground"] != "green":
                        all_green = False
                        break
                if all_green:
                    self.found_answers = 9999
        self.input_field["state"] = "disabled"
        self.running = False
        self.RemovePauseBlock()
        self.paused = False
        
        self.exit_button["text"] = self.language.exit
        self.UpdateHighscore(self.found_answers, self.time_needed//10) # time in seconds

        self.start_button["text"] = self.language.restart
        self.window.update()


    # give up
    def GiveupButton(self):
        if self.settings_open:
            return
        self.RemovePauseBlock()
        self.given_up = True
        self.success = False 
        self.running = False 
        self.paused = False

        if self.current_game_id == 0:
            # secret mode doesn't display the answer
            self.pokemon_texts[8357]["text"] = self.language.nice_try
        else:
            for dexnumber, pokemontext in self.pokemon_texts.items():
                if pokemontext["text"] == "":
                    pokemontext["fg"] = "red"
                    pokemontext["text"] = self.current_gens_id[dexnumber]
        
        self.exit_button["text"] = self.language.exit
    

    def CheckInput(self, text):

        if self.running:
            try:
                pokemons = self.current_gens_name[text.lower()]
            except KeyError:
                pass
            else:
                for pokemon in pokemons:
                    dexnumber = pokemon[0]
                    pokemon_text = self.pokemon_texts[dexnumber]

                    isAll = (self.language.tag == "all")
                    if self.in_order_mode != 0: # is in-order-mode
                        success = False
                        if isAll:
                            if self.previous_completed and self.pokemon_texts_pos[dexnumber] == self.found_answers:
                                success = True
                            if (not self.previous_completed) and self.pokemon_texts_pos[dexnumber] == self.found_answers-1:
                                success = True
                        else:
                            if self.pokemon_texts_pos[dexnumber] == self.found_answers:
                                success = True
                        
                        if not success:
                            if self.pokemon_texts_pos[dexnumber] < self.found_answers:
                                self.Flash(self.input_field, "red")
                                self.Flash(pokemon_text, "red", 1000)
                            else:
                                self.Flash(self.input_field, "yellow")
                                self.Flash(pokemon_text, "red", 1000, "yellow")
                            continue

                    if pokemon_text["text"] == "":
                        pokemon_text["text"] = pokemon[1]
                        self.found_answers += 1
                        self.UpdateProgress()
                        if isAll and self.current_gens_id_eng[dexnumber] == self.current_gens_id_ger[dexnumber]:
                            pokemon_text["fg"] = "green"
                            self.previous_completed = True
                            if self.found_answers == len(self.current_gens_id):
                                self.success = True
                        else:
                            self.previous_completed = False
                        self.Flash(self.input_field, "green")
                        self.Flash(pokemon_text, "green")
                        self.ClearInput()

                        if self.found_answers == len(self.current_gens_id):
                            if not isAll:
                                self.success = True
                            else:
                                if pokemon_text["fg"] == "green":
                                    self.success = True

                                
                    else:
                        if isAll and pokemon_text["fg"] != "green" and pokemon_text["text"] != pokemon[1]:
                            pokemon_text["fg"] = "green"
                            self.Flash(self.input_field, "green")
                            self.Flash(pokemon_text, "green")
                            self.previous_completed = True
                            if self.found_answers == len(self.current_gens_id):
                                self.success = True

                            self.ClearInput()
                        else:
                            self.Flash(self.input_field, "yellow")
                            self.Flash(pokemon_text, "yellow")
                            self.previous_completed = False

        return True        

    def StartCheckInput(self, text):
        self.window.after(1, lambda: self.CheckInput(text.lower()))
        return True


    def ClearInput(self):
        self.input_field.config(validate="none")
        self.input_field.delete(0, END)
        self.input_field.update()
        self.input_field.config(validate="all")


    def Flash(self, object, color="red", t=200, oldcolor="white"):
        """'object': object that should flash
        'color': color to flash to
        't': time it should flash to color
        'oldcolor': color to change after the flash"""
        object.config(background=color)
        self.window.after(t, lambda: object.config(background=oldcolor))


    def UpdateHighscore(self, newscore=0, newtime=0):
        """'newscore': score to update the highscore with (default (0): only update display\n
        'newtime': new highscore time in seconds! (default (0): only update display)"""

        self.CalculateCurrentGameID()
        # if just update without saving new values, simply read existing highscores
        current_language_index = self.language.index
        if newscore == 0 and newtime == 0:
            newscore = self.highscore_values[current_language_index][self.current_game_id]
            newtime = self.highscore_times[current_language_index][self.current_game_id]

        # true if full points -> display best time instead of points
        maxpoints = (newscore == len(self.current_gens_id) or newscore == 9999)
        
        if maxpoints and self.success and self.in_order_mode != 0:
            self.highscore_in_order_mode[self.current_game_id] = 1

        if newscore >= self.highscore_values[current_language_index][self.current_game_id]:
            self.highscore_values[current_language_index][self.current_game_id] = newscore
            if maxpoints:
                if self.highscore_times[current_language_index][self.current_game_id] > newtime:
                    self.highscore_times[current_language_index][self.current_game_id] = newtime
                if self.language.tag == "all":
                    for ilang in range(0,loc.number_languages):
                        if loc.getLanguageFromIndex(ilang).tag == "all": 
                            continue 
                        if self.highscore_times[ilang][self.current_game_id] > newtime:
                            self.highscore_times[ilang][self.current_game_id] = newtime

                

        # create the string with the Game ID and the highscores
        highscore_text = self.language.game
        highscore_text += f" ID:  {'{:03}'.format(self.current_game_id)}                {self.language.highscores}:  "
        highscore_suffix = ""
        #                        D          E               G         B               world
        language_unicodes = ("\U0001F1E9\U0001F1EA  ", "\U0001F1EC\U0001F1E7  ", "\U0001F310  ")
        Nemblems = 0
        for ilang in range(0,loc.number_languages):
            if  (self.highscore_values[ilang][self.current_game_id] == len(self.current_gens_id)) or self.highscore_times[ilang][self.current_game_id] < 100000000:
                highscore_text += f"{'{:02}'.format(self.highscore_times[ilang][self.current_game_id]//60)}:{'{:02}'.format(self.highscore_times[ilang][self.current_game_id]%60)} ({loc.getLanguageFromIndex(ilang).name})    "
                highscore_suffix += language_unicodes[ilang]
                Nemblems += 1
            else:
                highscore_text += f"{self.highscore_values[ilang][self.current_game_id]} / {len(self.current_gens_id)} ({loc.getLanguageFromIndex(ilang).name})    "
    
        if self.highscore_values[loc.number_languages-1][self.current_game_id] == 9999:
            highscore_suffix += "\U00002606  " # star
            Nemblems +=1
        if self.highscore_in_order_mode[self.current_game_id] == 1:
            highscore_suffix += "\U00002192  " # right arrow
            Nemblems +=1
        if Nemblems == loc.number_languages+2:
            highscore_suffix +="\U0001F44D" # thumb up
    
        self.highscore_label["text"] = highscore_text + highscore_suffix

    def GetGenNumber(self, dexnumber):
        if dexnumber <= 151:
            return 1
        elif dexnumber <= 251:
            return 2
        elif dexnumber <= 386:
            return 3
        elif dexnumber <= 493:
            return 4
        elif dexnumber <= 649:
            return 5
        elif dexnumber <= 721:
            return 6
        elif dexnumber <= 809:
            return 7
        elif dexnumber <= 905:
            return 8
        elif dexnumber <= 1015:
            return 9
        else:
            return 1

    def BuildList(self):
        for dexnumber, texts in self.number_texts.items():
            texts.destroy()
        self.number_texts.clear()
        for dexnumber, texts in self.pokemon_texts.items():
            texts.destroy()
        self.pokemon_texts.clear()
        self.pokemon_texts_pos.clear()

        #lines_per_column = 26
        start_yvalue = 70
        total_number_pokemon = len(self.current_gens_id)

        fontsizes = [12, 9, 7, 6, 5, 4, 4]
        fontsizeoffsets = [6, 4, 5, 4, 3, 2, 2]
        numbers_columns = [7, 9, 10, 12, 15, 17, 18]
        number_widths = [54, 42, 38, 33, 28, 25, 24]
        number_width_offsets = [18, 18, 18, 11, 12, 9, 8]
        if total_number_pokemon > 816:
            sizeindex = 6  
        elif total_number_pokemon > 660:
            sizeindex = 5
        elif total_number_pokemon > 528:
            sizeindex = 4
        elif total_number_pokemon > 390:
            sizeindex = 3
        elif total_number_pokemon > 252:
            sizeindex = 2
        elif total_number_pokemon > 168:
            sizeindex = 1
        else:
            sizeindex = 0

        number_columns = numbers_columns[sizeindex]
        fontsize = fontsizes[sizeindex] + (fontsizeoffsets[sizeindex] if self.windowbig else 0)
        number_width = number_widths[sizeindex] + (number_width_offsets[sizeindex] if self.windowbig else 0)

        lines_per_column = math.ceil(len(self.current_gens_id) / number_columns)
        width_of_column = (self.xwindow) / number_columns
        height_of_rows = (self.ywindow - 80) / lines_per_column

        i=0
        for dexnumber, pokemonname in self.current_gens_id.items():
            
            number = '{:03}'.format(dexnumber)
            newnumberlabel = Label(text=f"#{number}", width=4, height=1, font=('Arial', fontsize, 'bold'), foreground=Game.gen_colors[self.GetGenNumber(dexnumber)-1])
            self.number_texts[dexnumber] = newnumberlabel
            newnumberlabel.place(x=5+width_of_column*(i//lines_per_column), y=start_yvalue+height_of_rows*(i%lines_per_column))
            
            newtextlabel = Label(text="", width=13, height=1, font=('Arial', fontsize), anchor="w",background="white")
            self.pokemon_texts[dexnumber] = newtextlabel
            newtextlabel.place(x=number_width+width_of_column*(i//lines_per_column), y=start_yvalue+height_of_rows*(i%lines_per_column))

            self.pokemon_texts_pos[dexnumber] = i
            i+=1
        
        if len(self.progress) != 0: # load progress of last time
            if len(self.progress) != len(self.current_gens_id.keys()):
                assert("ERROR: save state does not match with current game ID...")

            lall = (self.language.tag == "all")
            for i, dexnumber in enumerate(self.current_gens_id.keys()):
                if self.progress[i] == 0:
                    continue
                #else:
                if self.progress[i] > 1: # all, either English (2) or both done (3)
                    self.pokemon_texts[dexnumber]["text"] = self.current_gens_id_eng[dexnumber]
                    if self.progress[i] == 3: # all, both done 
                        self.pokemon_texts[dexnumber]["fg"] = "green"
                elif self.progress[i] == 1:
                    if lall:
                        self.pokemon_texts[dexnumber]["text"] = self.current_gens_id_ger[dexnumber]
                    else:
                        self.pokemon_texts[dexnumber]["text"] = self.current_gens_id[dexnumber]


                 
    def UpdateProgress(self):
        self.progress_label["text"] = f"{self.found_answers} / {len(self.current_gens_id)}" 


    def SaveHighscores(self):
        with open(Game.highscore_location, mode="wb") as file:
            output = ""
            for ilang in range(0,loc.number_languages):
                for i in range(0, len(self.highscore_values[ilang])):
                    output += str(self.highscore_values[ilang][i]) + " "
                output += "\n"
                for i in range(0, len(self.highscore_times[ilang])):
                    output += str(self.highscore_times[ilang][i]) + " "
                output += "\n"
            for i in range(0, len(self.highscore_in_order_mode)):
                output += str(self.highscore_in_order_mode[i]) + " "
            output += "\n"
            
            file.write(output.encode())

    def SaveOldSettings(self):
        with open(Game.settings_location, mode="wb") as file:
            output = ""
            if self.current_game_id == 0:
                output += "1\n1"
                output += "0"*(Game.total_gen_number-1)
            else:
                output += str(self.gen_number)
                output += "\n"
                for i in self.gens_active:
                    output += str(i) 
            output += "\n"
            output += str(self.in_order_mode)
            output += "\n"
            output += self.language.tag
            output += "\n"
            if self.windowbig:
                output += "1"
            else:
                output += "0"
            file.write(output.encode())

    def LoadGen(self, gennumbers):
        first = True
        for i in range(0,Game.total_gen_number):
            igenval = gennumbers[i]
            if igenval == 1:
                if first:
                    self.GenButton(i+1)
                    first = False
                else:
                    self.GenButton(i+1,True)
            
    def SaveProgress(self):
        output = f"{self.language.tag}\n"
        output += f"{self.CalculateCurrentGameID()}\n"
        output += f"{self.found_answers}\n"
        output += f"{self.pause_time}\n"

        for dexnumber, pokemontext in self.pokemon_texts.items():
            if pokemontext["text"] == "":
                output += "0 "
            else: # something was found
                if self.language.tag != "all":
                    output += "1 "
                else: # "all"
                    if pokemontext["fg"] == "green": # found both names
                        output += "3 "
                    else: # not both
                        if pokemontext["text"] in self.current_gens_id_ger.values(): # only german
                            output += "1 "
                        elif pokemontext["text"] in self.current_gens_id_eng.values(): # only english
                            output += "2 "
                        else:
                            print("ERROR in SaveProgress, language is \"all\", but pokemon is not in any of the language lists")
        
        output += "\n"
        
        with open("savestate.txt", mode="wb") as file:
            file.write(output.encode())
    
    def LoadProgress(self):
        if not exists("savestate.txt"):
            return
        #else:
        with open("savestate.txt", mode="rb") as file:
            d = file.read()
            lines = d.decode().split("\n")
            lang = lines[0]
            self.language = loc.getLanguage(lang)
            # # the following two lines are not useful, since loading of gens 
            # # is not supported for gameid, yet...
            # gameid = int(lines[1]) 
            # self.current_game_id = gameid
            answers = int(lines[2])
            self.found_answers = answers
            timer = int(lines[3])
            self.pause_time = timer
            self.time_needed = self.maxtime*10-self.pause_time
            self.progress = [int(i) for i in lines[4].split()]
        
        self.loaded_progress = True
        remove("savestate.txt")
        

game = Game()

