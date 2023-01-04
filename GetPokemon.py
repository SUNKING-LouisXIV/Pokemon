# Goal:     Get list of pokemon relevant from the pokeapi
#           Export their attributes to a CSV og/and JSON file
# Functions:
#           get_pokemon_data: collects from the pokeapi, a set of pokamons and some of their attributes
#           create_dict_entry: called by get_pokemon_data with the attributes of the pokemon to create a dictionary
#           write_to_csv: write the CSV formatted result to a csv file
#           write_to_json: write the JSON formatted result to a json file

# We start by importing the python wrapper for the pokemon API.
import pokebase
# In order to create the csv and json file
import json
import csv

## Global variables
DEBUG = True # Print progress reports and stats for debugging
# We only want pokemons that have played in valid_games
valid_games = ["red", "blue", "leafgreen", "white"] 
# Output file name
csv_file = 'pokemon.csv' 
json_file = 'pokemon.json'

# this is the definition of the dictionary
def create_dict_entry(id, name, name_pii, base_experience, height, weight, bmi, order, slot1, slot2, sprite):
# The result of this dictionary will be the attributes of a pokemon passed as argument.

    return {
        "id": id,
        "name": name,
        "name_pii" : name_pii,
        "base_experience": base_experience,
        "height": height,
        "weight": weight,
        "bmi": bmi,
        "order": order,
        "slot1": slot1,
        "slot2": slot2,
        "sprite": sprite
    }


def get_pokemon_data(valid_games):
    # arguments:
    #    valid_games: a list with game colours. Only retain pokemons that played in any of the colours on the list
    # results:
    #    a list of dictionaries that can easily be exported to JSON or CSV
    #
    # We get a list of all the pokemons
    all_pokemons = (pokebase.APIResource("pokemon", "")).results
    ##all_pokemons = all_pokemons[:30] # For demo purpose, limit to 30 pokemons
    # as each pokemon's attribute are read, they are stored into a dict and appended to the list_of_dict
    # list_of_dict is the result of this function
    list_of_dict = [] 
    # Now we need to make sure that only the right pokemons make the cut
    for pokemon in all_pokemons:
        # This determines if the individual pokemon played in our valid game set
        # This tells us all games the pokemon was part of
        games = [gi.version.name for gi in pokemon.game_indices]
        # We list the attributes if the pokemon is in any of the valid games
        # We use 'if any' to make just check if the pokemon is in any of the valid games  
        if any(item in games for item in valid_games):
            #extract the attributes
            id = pokemon.id
            name = pokemon.name.capitalize()
            name_pii = hash(name) # name is transformed into an hash value for GDPR PII
            height = pokemon.height / 10  # in meters
            weight = pokemon.weight / 10  # in kilos
            bmi = weight / (height**2)
            order = pokemon.order
            base_experience = pokemon.base_experience
            # We then want get the slots the pokemon is part of. 
            # Can be 1 or 2 slots
            slots = [x.type.name for x in pokemon.types]
            # We assume that slot 1 is always in first position and slot 2 (if it exists) is always in the second position 
            slot1 = slots[0]
            slot2 = slots[1] if len(slots) == 2 else ""
            sprite = pokemon.sprites.front_default
            if DEBUG:
                print(
                    "Id {}, Name {}, Name_pii {}, Base Experience {}, Heigh {}, Weight {}, BMI {:0.1f}, Order {}, Slot1 {}, Slot2 {}, Sprite URL {}".format(
                        id,
                        name,
                        name_pii,
                        base_experience,
                        height,
                        weight,
                        bmi,
                        order,
                        slot1,
                        slot2,
                        sprite
                    )
                )
            # dict is loaded with the data from create_dict_entry
            # This is then appended to list_of_dict, as we need a list of each dictionary for the individual pokemon
            dict = create_dict_entry(id, name, name_pii, base_experience, height, weight, bmi, order, slot1, slot2, sprite)
            list_of_dict.append(dict)
        else:
            if DEBUG: print("Skipping {}".format(pokemon.id))
            #pokemon was not part of any valid_game
    return list_of_dict

def write_to_csv(list_of_dict, file_name):
# Write the list of dictionary to a csv formatted file  
    file = open(file_name, 'w')
    writer = csv.DictWriter(file, fieldnames=["id", "name", "name_pii", "base_experience", "height", "weight", "bmi", "order", "slot1", "slot2", "sprite"])
    writer.writeheader()
    writer.writerows(list_of_dict)
    file.close()

def write_to_json(list_of_dict, file_name): 
# Write the list of dictionary to a json formatted file
    file = open(file_name, 'w')
    json.dump(list_of_dict,file)
    file.close()

# This is the start of the program
if DEBUG: print("starting")
list_of_dict = get_pokemon_data(valid_games)
write_to_csv(list_of_dict, csv_file)
write_to_json(list_of_dict, json_file)
if DEBUG: print(json.dumps(list_of_dict, indent=2))
if DEBUG: print("Found {} pokemons in {} games".format(len(list_of_dict),", ".join(valid_games)))