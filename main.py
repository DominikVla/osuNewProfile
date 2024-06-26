from ossapi import Ossapi
import json
import os
from prettytable import PrettyTable
from time import sleep
import math

# create a new client at https://osu.ppy.sh/home/account/edit#oauth
client_id = 0
client_secret = 'secret'
api = Ossapi(client_id, client_secret)

# Save user scores to external file
def save_scores(user_scores, get_id):
    for score in user_scores:
        # Change object type of mods
        mods_used = score.mods
        mods_used = str(mods_used)

        # Convert accuracy to be more readable
        converted_accuracy = round(100 * score.accuracy, 2)

        # Saving scores with PP values
        if score.pp !=None:
            score_data = {
                "Title": score.beatmapset.title,
                "Mods": mods_used,
                "PP": score.pp,
                "Accuracy": converted_accuracy,
                "Score ID": score.id
            }
            json_object = json.dumps(score_data, indent=None, separators=(',', ':'))
            with open ("scores.json", "a") as f: # Storing
                f.write(json_object)
                f.write('\n')
                f.close()

    # Saving user ID
    file_check = check_file = os.path.isfile('./userid.txt')
    if file_check != True:
        user_id = str(get_id)
        with open ("userid.txt", "a") as f:
            f.write(user_id)
            f.close()

    print ("Your scores and ID have been saved!")
    user_id = None

# get user details (Name/ID, Gamemode)
def get_user():
    file_check = check_file = os.path.isfile('./userid.txt')
    if file_check != True:
        print("Please provide either your user ID or ign:")
        name = input()
    else:
        f = open("userid.txt", "r")
        saved_id = f.read()
        name = saved_id
    return name

# Displays content of JSON file in a table
def show_scores():
    table = PrettyTable(["Title", "Mods", "PP", "Accuracy", "Score ID"])

    # Creating table
    scores = []
    unique_scores = set()
    total_pp = 0
    weighted_pp = 0
    weighting = 1
    weighted_total = 0

    try:
        with open("scores.json", "r") as f:
            for line in f:
                data = json.loads(line)
                # Checking for unique scores
                score_key = (data["Title"], data["Mods"], data["PP"], data["Accuracy"], data["Score ID"])
                if score_key not in unique_scores:
                    unique_scores.add(score_key)
                    scores.append(data)
        fix_duplicates()
    except:
        print ("No Scores Saved! Returning to menu")
        main_menu()

    # Table Sorting
    print ("How do you want to sort your scores? ('pp'/'accuracy').")
    lock = True
    while lock:
        sort_key = input().lower()
        match sort_key:
            case "pp":
                scores.sort(key=lambda x: x["PP"], reverse=True)
                lock = False
            case "accuracy" | "acc":
                scores.sort(key=lambda x: x["Accuracy"], reverse=True)
                lock = False
            case _:
                print("'" + sort_key + "' is not a valid sort method. Please type either 'pp' or 'accuracy'.")

    # Headings and printing
    for score in scores:
        table.add_row([score["Title"], score["Mods"], score["PP"], score["Accuracy"], score["Score ID"]])
        total_pp += score["PP"]
        weighted_pp = score["PP"] * weighting
        weighted_total += weighted_pp
        weighting = weighting * 0.95
    print(table)
    print(f"Total PP: {total_pp:.2f}pp (Unweighted) | Weighted PP: {weighted_total:.2f}pp")
    main_menu()

# Deletes the JSON file
def delete_user():
    print ("Are you sure you want to delete your data? This will result in your scores and user ID being removed. (y/n)")
    while True:
        confirmation = input().lower()
        match confirmation:
            case "y" | "yes":
                file_check = check_file = os.path.isfile('./scores.json')
                if file_check == True:
                    os.remove("scores.json")

                file_check = check_file = os.path.isfile('./userid.txt')
                if file_check ==True:
                    os.remove("userid.txt")
                print("User data successfully removed.")
                get_data()
            case "n" | "no":
                print("Returning to menu.")
                main_menu()
            case _:
                print("Invalid reply. Please reply with y or n to confirm your decision.")

# Gets the Users ID's and scores sets within the past 24hrs of signing up.
def get_data():
    name = get_user()
    try:
        get_id = api.user(name).id
        if int(get_id) != get_id:
            print("Invalid osu! Account!")
            sleep(3)
            quit()
        user_scores = api.user_scores(get_id, type="recent", limit=100)
        if len(user_scores) == 0 or user_scores == None:
            print("No Scores detected! No scores have been saved. Use update in the main menu")
            file_check = check_file = os.path.isfile('./userid.txt')
            if file_check != True:
                user_id = str(get_id)
                with open("userid.txt", "a") as f:
                    f.write(user_id)
                    f.close()
            main_menu()

        save_scores(user_scores, get_id)
        main_menu()
    except Exception as e:
        print("Sorry, something went wrong...\nError:", e," \nExiting...")
        sleep(5)
        quit()

# Check if there's any data present
def check_data():
    file_check = check_file = os.path.isfile('./scores.json')
    if file_check != True:
        get_data()

# Removes any duplicate scores stored in scores.json
def fix_duplicates():
    scores = []
    unique_scores = set()
    with open("scores.json", "r") as f:
        for line in f:
            data = json.loads(line)
            # Checking for unique scores
            score_key = (data["Title"], data["Mods"], data["PP"], data["Accuracy"])
            if score_key not in unique_scores:
                unique_scores.add(score_key)
                scores.append(data)
    f.close()
    with open("scores.json", "w") as f:
        for score in scores:
            json.dump(score, f)
            f.write('\n')
    f.close()

def help():
    print("""--------------------------------------------------------------------------------------
    Here's the list of commands you can use: 'show scores' 'delete data' 'update'
--------------------------------------------------------------------------------------""")
    main_menu()

# Main function!!
def main_menu():
    print("Main menu. Please enter a command or use 'help' to see the command list.")
    while True:
        sent_command = input().lower()
        match sent_command:
            case "show scores" | "scores":
                show_scores()
            case "delete data" | "delete":
                delete_user()
            case "help":
                help()
            case "update":
                get_data()
            case _ :
                print ("'"+sent_command+"' is not a valid command. Use the 'help' command if you aren't sure what to do.")

# running functions
check_data()
main_menu()
