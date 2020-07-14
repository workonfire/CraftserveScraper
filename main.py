from os import system
from colorama import init, deinit, Fore, Style
from server import Server, ServerDoesNotExist
from time import strftime

__VERSION__ = '1.0.0'
__AUTHOR__ = 'workonfire'

def color_print(color, text):
    init(autoreset = True)
    print(Style.BRIGHT + color + text)
    deinit()

def main():
    banner = ["   ______           ______                          ",
              "  / ____/________ _/ __/ /_________  ______   _____ ",
              " / /   / ___/ __ `/ /_/ __/ ___/ _ \/ ___/ | / / _ \\",
              "/ /___/ /  / /_/ / __/ /_(__  )  __/ /   | |/ /  __/",
              "\____/_/   \__,_/_/  \__/____/\___/_/    |___/\___/ "]

    for line in banner:
        color_print(Fore.GREEN, line)
    print("\nScraper v{}".format(__VERSION__))
    color_print(Fore.YELLOW, "by {}\n".format(__AUTHOR__))

    while True:
        try:
            server_ids = input("Server ID range (e.g. 10000-123456): ")
            lower_bound, upper_bound = server_ids.split('-')
            break
        except ValueError:
            color_print(Fore.RED, "Incorrect format.")

    # Filter wizard
    logging = input("Enable logging? (y/n) ")
    verbosity = input("Enable verbosity? (y/n) ")
    filtering = input("Enable filtering? (y/n) ")
    special_query = False
    online_filter = 'n'
    max_players_filter = 'n'
    max_players_filter_value = 0
    server_type_filter = 'all'
    online_mode_filter = 'n'
    plugins_filter = 'n'
    filtered_plugins = []

    if filtering == 'y':
        online_filter = input("Filter by online servers? (y/n) ")
        max_players_filter = input("Filter by max players? (y/n) ")
        if max_players_filter == 'y':
            max_players_filter_value = input("Max players filter value (e.g. 10): ")
        server_type_filter = input("Filter by server type? (grass/diamond/km/all) ")
        online_mode_filter = input("Filter by online mode? (y/n) ")
        plugins_filter = input("Filter by plugins? (y/n) ")
        if plugins_filter == 'y':
            print("Please type the plugin name with the appropriate version, e.g. Essentials 2.17.2.146.")
            print("If you want to finish, type \"end\".")
            while True:
                filtered_plugin = input(">> ")
                if filtered_plugin == 'end':
                    break
                else:
                    filtered_plugins.append(filtered_plugin)
        if online_mode_filter == 'y' or plugins_filter =='y':
            special_query = True
            color_print(Fore.RED, "WARN: Filtering by online mode or plugins or version might cause the program to query the server longer.")
            color_print(Fore.RED, "It is better to not use this option, unless you really have to.")
    if verbosity == 'n' and logging == 'n':
        color_print(Fore.RED, "WARN: Logging and verbosity is disabled. What is the point of that..?")

    for server_id in range(int(lower_bound), int(upper_bound)):
        try:
            print("Querying {}/{}...".format(str(server_id), upper_bound))

            server = Server(server_id, special_query=special_query, primitive_address=True)

            if filtering == 'y':
                if online_filter == 'y' and not server.running:
                    continue
                if max_players_filter == 'y' and not max_players_filter_value == server.max_online:
                    continue
                if server_type_filter != 'all' and not server_type_filter == str(server.type).lower():
                    continue
                if online_mode_filter == 'y' and not server.online_mode:
                    continue
                if plugins_filter == 'y' and not any(plugin in server.plugins for plugin in filtered_plugins):
                    continue

            if logging == 'y':
                with open('logs.txt', 'a') as log_file:
                    log_file.write("[" + strftime("%d.%m.%Y %H:%M:%S") + "] ----- FOUND! -----\n"
                                   "Name: " + server.name + "\n"
                                   "Address: " + ("none" if server.address is None else server.address) + "\n"
                                   "Is running: " + ("yes" if server.running else "no")  + "\n"
                                   "Players: " + str(server.online_now) + "/" + str(server.max_online) + "\n"
                                   "Type: " + server.type + "\n"
                                   "Expiration date: " + ("none" if server.expiration_date is None else server.expiration_date) + "\n"
                                   "Price: " + ("none" if server.price is None else server.price) + "\n")
                    if server.special_query:
                        log_file.write("Plugin list: " + ', '.join([str(plugin) for plugin in server.plugins]))
                    log_file.write("\n")

            if verbosity == 'y':
                color_print(Fore.GREEN, "----- FOUND! -----")
                print("Name: " + server.name)
                print("Address: " + ("none" if server.address is None else server.address))
                print("Is running: " + ("yes" if server.running else "no"))
                print("Players: " + str(server.online_now) + "/" + str(server.max_online))
                print("Type: " + server.type)
                print("Expiration date: " + ("none" if server.expiration_date is None else server.expiration_date))
                print("Price: " + ("none" if server.price is None else server.price))
                if server.special_query:
                    print("Plugin list: " + ', '.join([str(plugin) for plugin in server.plugins]))
                color_print(Fore.RED, "----- END -----")
            else:
                color_print(Fore.GREEN, "MATCH FOUND: " + str(server_id))
        except ServerDoesNotExist:
            pass

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        system("pause")