from os import system
from colorama import init, deinit, Fore, Style
from server import Server, ServerDoesNotExist
from time import strftime

__VERSION__ = '1.0.3'
__AUTHOR__ = 'workonfire'


def color_print(color, text):
    init(autoreset=True)
    print(Style.BRIGHT + color + text)
    deinit()


def main():
    banner = ["   ______           ______                          ",
              "  / ____/________ _/ __/ /_________  ______   _____ ",
              " / /   / ___/ __ `/ /_/ __/ ___/ _ \\/ ___/ | / / _ \\",
              "/ /___/ /  / /_/ / __/ /_(__  )  __/ /   | |/ /  __/",
              "\\____/_/   \\__,_/_/  \\__/____/\\___/_/    |___/\\___/ "]

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
    server_version_filter = 'n'
    server_version_filter_value = None
    filtered_plugins = []

    if filtering == 'y':
        online_filter = input("Filter by online servers? (y/n) ").lower()
        max_players_filter = input("Filter by max players? (y/n) ").lower()
        if max_players_filter == 'y':
            max_players_filter_value = int(input("Max players filter value (e.g. 10): "))
        server_type_filter = input("Filter by server type? (grass/diamond/km/all) ").lower()
        online_mode_filter = input("Filter by online mode? (y/n) ").lower()
        server_version_filter = input("Filter by server version? (y/n) ").lower()
        if server_version_filter == 'y':
            server_version_filter_value = input("Server version (e.g. 1.15.2): ")
        plugins_filter = input("Filter by plugins? (y/n) ").lower()
        if plugins_filter == 'y':
            print("Please type the plugin name, e.g. EssentialsX.")
            print("If you want to finish, type \"end\".")
            while True:
                filtered_plugin = input(">> ")
                if filtered_plugin == 'end':
                    break
                else:
                    filtered_plugins.append(filtered_plugin)
        if online_mode_filter == 'y' or plugins_filter == 'y':
            special_query = True
            color_print(Fore.RED,
                        "WARN: Filtering by online mode or plugins or version might cause the program to query the "
                        "server longer.")
            color_print(Fore.RED, "It is better to not use this option, unless you really have to.")
    if verbosity == 'n' and logging == 'n':
        color_print(Fore.RED, "WARN: Logging and verbosity is disabled. What is the point of that..?")

    color_print(Fore.CYAN, "\nScraper launched!\n")
    for server_id in range(int(lower_bound), int(upper_bound)):
        try:
            print("Querying {}/{}...".format(str(server_id), upper_bound))

            server = Server(server_id, special_query=special_query)

            try:
                if filtering == 'y':
                    if online_filter == 'y' and not server.running:
                        continue
                    if max_players_filter == 'y' and not max_players_filter_value == server.max_online:
                        continue
                    if server_type_filter != 'all' and not server_type_filter == str(server.type).lower():
                        continue
                    if online_mode_filter == 'y' and not server.online_mode:
                        continue
                    if server_version_filter == 'y' and not server.version == server_version_filter_value:
                        continue
                    if plugins_filter == 'y' and not any(plugin in server.plugins for plugin in filtered_plugins):
                        continue
                if logging == 'y':
                    with open('logs.txt', 'a') as log_file:
                        log_file.write("[" + strftime("%d.%m.%Y %H:%M:%S") + "] ----- MATCH FOUND! -----\n"
                                       "ID: {}\n".format(server.id) +
                                       "Name: {}\n".format(server.name) +
                                       "Address: {}\n".format("none" if server.address is None else server.address) +
                                       "Is running: {}\n".format("yes" if server.running else "no") +
                                       "Players: {}/{}\n".format(str(server.online_now), str(server.max_online)) +
                                       "Type: {}\n".format(server.type) +
                                       "Expiration date: {}\n".format(
                                           "none" if server.expiration_date is None else server.expiration_date) +
                                       "Price: {}\n".format("none" if server.price is None else server.price) +
                                       "Wallet: {}\n".format("none" if server.wallet is None else server.wallet) +
                                       "Version: {}\n".format("none" if server.version is None else server.version))
                        if server.special_query:
                            log_file.write("Plugin list: {}".format(
                                ', '.join([str(plugin) for plugin in server.plugins])))
                        log_file.write("\n")

                if verbosity == 'y':
                    color_print(Fore.GREEN, "----- MATCH FOUND! -----")
                    print("ID: {}".format(server.id))
                    print("Name: {}".format(server.name))
                    print("Address: {}".format("none" if server.address is None else server.address))
                    print("Is running: {}".format("yes" if server.running else "no"))
                    print("Players: {}/{}".format(str(server.online_now), str(server.max_online)))
                    print("Type: {}".format(server.type))
                    print("Expiration date: {}".format(
                        "none" if server.expiration_date is None else server.expiration_date))
                    print("Price: {}".format("none" if server.price is None else server.price))
                    print("Wallet: {}".format("none" if server.wallet is None else server.wallet))
                    print("Version: {}".format("none" if server.version is None else server.version))
                    if server.special_query:
                        print("Plugin list: {}".format(', '.join([str(plugin) for plugin in server.plugins])))
                    color_print(Fore.RED, "----- END -----")
                else:
                    color_print(Fore.GREEN, "MATCH FOUND: " + str(server.id))
            except (AttributeError, UnicodeEncodeError):
                color_print(Fore.RED, "Something weird happened. Skipping {}...".format(server.id))
        except ServerDoesNotExist:
            pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        system("pause")
