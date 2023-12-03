class Language():

    def __init__(self, index, dict={}):
        self.index = index
        self.name = dict.get("name", "All") # German, English, All
        self.tag = dict.get("tag", "all") # ger, eng, all

        self.exit = dict.get("exit", "Exit")
        self.start = dict.get("start", "Start")
        self.restart = dict.get("restart", "Restart")
        self.pause = dict.get("pause", "Pause")
        self.continu = dict.get("continue", "Continue")
        self.settings = dict.get("settings", "Settings")
        self.giveup = dict.get("giveup", "Give Up")
        self.confirm = dict.get("confirm", "Confirm")
        self.save = dict.get("save", "Save")
        self.loading = dict.get("loading", "Loading...")
        self.paused = dict.get("paused", "Paused")
        self.game = dict.get("game", "Game")
        self.highscores = dict.get("highscores", "Highscores")

        self.choose_gen = dict.get("choose_gen", "Choose a single generation")
        self.combination = dict.get("combination", "Combination")
        self.language_text = dict.get("language_text", "Language")
        self.multiple_gen = dict.get("multiple_gen", "Or combine several generations")
        self.all = dict.get("all", "all")
        self.in_order_text = dict.get("in_order_text", "Fill in order")
        self.cancel = dict.get("cancel", "Cancel")
        self.credits = dict.get("credits", "Credits")
        self.credits_text = dict.get("credits_text", "Game Idea: www.sporcle.com/games/g/pokemon\nProgramming & Testing: Mathias Wagner")
        self.nice_try = dict.get("nice_try", "nice try")

german = {
    "name": "Deutsch",
    "tag": "ger",

    "exit": "Beenden",
    # "start": "Start",
    "restart": "Neustart",
    # "pause": "Pause",
    "continue": "Weiter",
    "settings": "Einstellungen",
    "giveup": "Aufgeben",
    "confirm": "Bestätigen",
    "save": "Speichern",
    "loading": "Lädt...",
    "paused": "Pausiert",
    "game": "Spiel",
    # "highscores": "Highscores",

    "choose_gen": "Wähle einzelne Generation",
    "combination": "Kombination",
    "language_text": "Sprache",
    "multiple_gen": "Oder kombiniere mehrere Generationen",
    "all": "alle",
    "in_order_text": "Der Reihe nach",
    "cancel": "Abbrechen",
    # "credits": "Credits",
    "credits_text": "Spielidee: www.sporcle.com/games/g/pokemon\nProgrammierung & Testen: Mathias Wagner",
    "nice_try": "netter Versuch"
          }

class Localization():

    def __init__(self):
        self.languages = {}
        self.default = ""
        self.number_languages = 0

    def addLanguage(self, tag, lang):
        if tag in self.languages.keys():
            print(f"WARNING: Language \"{tag}\" added more than once, skip second time...")
            return
        self.languages[tag] = lang
        self.number_languages += 1
        print(f"Added support for language \"{tag}\".")
        if self.default == "":
            self.default = tag
            print(f"Set \"{tag}\" to default language.")

    def changeDefault(self, tag):
        if not tag in self.languages.keys():
            print(f"WARNING: Language \"{tag}\" does not exist. Don't change default...")
            return
        olddefault = self.default
        self.default = tag
        print(f"Change default language from  \"{olddefault}\" to \"{tag}\".")

    def getLanguage(self, tag):
        try:
            lang = self.languages[tag]
        except KeyError:
            print(f"ERROR: No language support for tag \"{tag}\" defined!")
            exit(1)
        return lang
    
    def getLanguageFromIndex(self, index):
        for val in self.languages.values():
            if val.index == index:
                return self.languages[val.tag]
        print(f"ERROR: No language with index {index} found. Return default ({self.default})...")
        return self.languages[self.default]
    
    def getIndexFromTag(self, tag):
        return self.languages[tag].index




# !!!when adding new languages, make sure that the index of "all" is the last one!!!
loc = Localization()
loc.addLanguage("all", Language(index=2, dict={"name":"All", "tag": "all"}))
loc.addLanguage("eng", Language(index=1, dict={"name":"English", "tag": "eng"}))
loc.addLanguage("ger", Language(index=0, dict=german))