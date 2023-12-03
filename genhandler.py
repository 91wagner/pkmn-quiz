import importlib
# need a way to include them to exe without explicity importing them 
import poke_gen1
import poke_gen2
import poke_gen3
import poke_gen4
import poke_gen5
import poke_gen6
import poke_gen7
import poke_gen8
import poke_gen9

print("Loading gens...")

class Gen():
    def __init__(self, index=-1):
        if index == -99:
            self.index = -99
            self.names = [{"wattzapf" : [(8357, "Wattzapf")]}, {"joltik" : [(8357, "Joltik")]}, {"joltik" : [(8357, "Joltik")], "wattzapf" : [(8357, "Wattzapf")]}]
            self.ids = [{8357 : "Wattzapf"}, {8357 : "Joltik"}, {8357 : "Joltik"}]
            self.maxtime = 333*60+33
            self.combined = [-99]

        elif index < 0: # empty gen for building combinations
            self.index = -1
            self.names = [{},{},{}]
            self.ids = [{},{},{}]
            self.maxtime = 0
            self.combined = []

        else:
            pg = importlib.import_module(f"poke_gen{index}")
            # make sure that the order of languages is correct if you add new languages to localization.py
            self.index = index
            self.names = [pg.gen_name_ger, pg.gen_name_eng, pg.gen_name_all]
            self.ids = [pg.gen_id_ger, pg.gen_id_eng, pg.gen_id_all]
            self.maxtime = (20*60, #1
                            15*60, #2
                            20*60, #3
                            15*60, #4
                            20*60, #5
                            15*60, #6
                            15*60, #7
                            15*60, #8
                            20*60, #9
                            )[index-1]
            self.combined = [index]
    
    def getNames(self, ilang):
        try:
            return self.names[ilang]
        except IndexError:
            print(f"ERROR in getNames: language index {ilang} is not supported for current gen {self.index}")

    def getIDs(self, ilang):
        try:
            return self.ids[ilang]
        except IndexError:
            print(f"ERROR in getIDs: language index {ilang} is not supported for current gen {self.index}")

    def containsName(self, name, ilang) -> bool:
        return name.lower() in self.names[ilang].keys()
    def containsID(self, id, ilang) -> bool:
        return id in self.ids[ilang].keys()
    
    def __iadd__(self, other):
        """
        Can only append if self has index -1 (not a vanilla gen)
        """
        if self.index >= 0:
            print("WARNING: You are trying to add to a vanilla gen. I will ignore that...")
            return self
        if other.index <= 0:
            print("WARNING: You are trying to add a combined gen. I will ignore that...")
            return self
        
        for i in range(0, len(self.names)):
            self.names[i].update(other.names[i])
            self.ids[i].update(other.ids[i])
        self.maxtime += other.maxtime
        self.combined.append(other.index)
        return self
    
    def getTitle(self) -> str:
        if self.combined[0] == -99:
            return "Gen ???"
        #else
        if len(self.combined) == 1:
            return f"Gen {self.combined[0]}"
        #else
        return "Gens " + "".join([str(i) for i in self.combined])
        

    def __str__(self) -> str:
        output = f"Gen {self.index}:  #={len(self.ids[-1])},  T={self.maxtime//60}min,\n"
        if self.index == -99:
            output += "first: ???,  last: ???"
            return output
        if len(self.names[0]) != 0:
            output += f"first: {self.names[-1][next(iter(self.ids[-1].values())).lower()]},  "
            output += f"last: {self.names[-1][next(reversed(self.ids[-1].values())).lower()]}\n"
        return output



class GenHandler():

    def __init__(self, total):
        self.total_gen_number = 0
        self.gens = []
        self.gen_colors =  ["black", "blue", "red", "green", "orange", "purple", "brown", "cyan", "violet"]
        self.current = None
        for i in range(1,total+1):
            self.addGen(Gen(i))
        self.secret = Gen(-99)


    def addGen(self, gen):
        if self.total_gen_number == 0:
            self.current = gen
        self.total_gen_number += 1
        self.gens.append(gen)

    def getGen(self, index):
        return self.gens[index]
    
    def getCurrentNames(self, ilang):
        return self.current.getNames(ilang)
    
    def getCurrentIDs(self, ilang):
        return self.current.getIDs(ilang)
    
    def buildCurrent(self, indices):
        """
        indices: 
        - int        -> single gen 
        - list       -> build combined gen with elements \n
        handles empty list appropriately ;)
        """
        if type(indices)==type(1):
            indices = [indices]
        
        if len(indices)==0:
            self.current = self.secret
        # elif len(indices)==1:
        #     self.current = self.gens[indices[0]-1]
        else:
            self.current = Gen()
            for i in indices:
                self.current += self.gens[i-1] 


    def getMaxTime(self):
        return self.current.maxtime

    def __str__(self) -> str:
        output = "Gen Handler:\n"
        for gen in self.gens:
            output += f"{gen}\n"

        output += f"Current gen:\n{self.current}\n"

        return output

gens = GenHandler(9)

gens.buildCurrent([1,4,6])
print(gens)
