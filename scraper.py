from os import system
from colorama import init, deinit, Fore, Style
from server import Server, ServerDoesNotExist
from time import strftime
import platform

__VERSION__ = '1.0.4'
__AUTHOR__ = 'workonfire'


def color_print(color, text):
    init(autoreset=True)
    print(Style.BRIGHT + color + text)
    deinit()


def main():
    if platform.system() == 'Windows':
        system('title CraftserveScraper')

    banner = ["   ______           ______                          ",
              "  / ____/________ _/ __/ /_________  ______   _____ ",
              " / /   / ___/ __ `/ /_/ __/ ___/ _ \\/ ___/ | / / _ \\",
              "/ /___/ /  / /_/ / __/ /_(__  )  __/ /   | |/ /  __/",
              "\\____/_/   \\__,_/_/  \\__/____/\\___/_/    |___/\\___/ "]

    for line in banner:
        color_print(Fore.GREEN, line)
    print(f"\nScraper v{__VERSION__}")
    color_print(Fore.YELLOW, f"by {__AUTHOR__}\n")

    while True:
        try:
            server_ids = input("Server ID range (e.g. 10000-123456): ")
            lower_bound, upper_bound = server_ids.split('-')
            break
        except ValueError:
            color_print(Fore.RED, "Incorrect format.")

    logging = input("Enable logging? (y/n) ").lower() == 'y'
    verbosity = input("Enable verbosity? (y/n) ").lower() == 'y'
    filtering = input("Enable filtering? (y/n) ").lower() == 'y'
    special_query = False
    online_filter = False
    max_players_filter = False
    max_players_filter_value = 0
    server_type_filter = 'all'
    online_mode_filter = False
    plugins_filter = False
    filtered_plugins = []

    if filtering:
        online_filter = input("Filter by online servers? (y/n) ").lower() == 'y'
        max_players_filter = input("Filter by max players? (y/n) ").lower() == 'y'
        if max_players_filter:
            max_players_filter_value = int(input("Max players filter value (e.g. 10): "))
        server_type_filter = input("Filter by server type? (grass/diamond/km/all) ").lower()
        online_mode_filter = input("Filter by online mode? (y/n) ").lower() == 'y'
        plugins_filter = input("Filter by plugins? (y/n) ").lower() == 'y'
        if plugins_filter:
            print("Please type the plugin name, e.g. EssentialsX.")
            print("If you want to finish, type \"end\".")
            while True:
                filtered_plugin = input(">> ")
                if filtered_plugin == 'end':
                    break
                else:
                    filtered_plugins.append(filtered_plugin)
        if online_mode_filter or plugins_filter:
            special_query = True
            color_print(Fore.RED,
                        "WARN: Filtering by online mode or plugins or version might cause the program to query the "
                        "server longer.")
            color_print(Fore.RED, "It is better to not use this option, unless you really have to.")
    if not verbosity and not logging:
        color_print(Fore.RED, "WARN: Logging and verbosity is disabled. What is the point of that..?")

    color_print(Fore.CYAN, "\nScraper launched!\n")
    for server_id in range(int(lower_bound), int(upper_bound)):
        try:
            print(f"Querying {str(server_id)}/{upper_bound}...")

            server = Server(server_id, special_query=special_query)

            try:
                if filtering:
                    if online_filter and not server.running:
                        continue
                    if max_players_filter and not max_players_filter_value == server.max_online:
                        continue
                    if server_type_filter != 'all' and not server_type_filter == str(server.type).lower():
                        continue
                    if online_mode_filter and not server.online_mode:
                        continue
                    if plugins_filter and not any(plugin in server.plugins for plugin in filtered_plugins):
                        continue
                if logging:
                    with open('logs.txt', 'a') as log_file:
                        log_file.write(f"[{strftime('%d.%m.%Y %H:%M:%S')}] ----- MATCH FOUND! -----\n" +
                                       f"ID: {server.id}\n" +
                                       f"Name: {server.name}\n" +
                                       f"Address: {'none' if server.address is None else server.address}\n" +
                                       f"Is running: {'yes' if server.running else 'no'}\n" +
                                       f"Players: {str(server.online_now)}/{str(server.max_online)}\n" +
                                       f"Type: {server.type}\n" +
                                       f"Expiration date: {'none' if server.expiration_date is None else server.expiration_date}\n" +
                                       f"Price: {'none' if server.price is None else server.price}\n")
                        if server.special_query:
                            log_file.write(f"Plugin list: {', '.join([str(plugin) for plugin in server.plugins])}")
                        log_file.write("\n")

                if verbosity:
                    color_print(Fore.GREEN, "----- MATCH FOUND! -----")
                    print(f"ID: {server.id}")
                    print(f"Name: {server.name}")
                    print(f"Address: {'none' if server.address is None else server.address}")
                    print(f"Is running: {'yes' if server.running else 'no'}")
                    print(f"Players: {str(server.online_now)}/{str(server.max_online)}")
                    print(f"Type: {server.type}")
                    print(f"Expiration date: {'none' if server.expiration_date is None else server.expiration_date}")
                    print(f"Price: {'none' if server.price is None else server.price}")
                    if server.special_query:
                        print(f"Plugin list: {', '.join([str(plugin) for plugin in server.plugins])}")
                    color_print(Fore.RED, "----- END -----")
                else:
                    color_print(Fore.GREEN, "MATCH FOUND: " + str(server.id))
            except (AttributeError, UnicodeEncodeError):
                color_print(Fore.RED, f"Something weird happened. Skipping {server.id}...")
        except ServerDoesNotExist:
            if verbosity:
                color_print(Fore.RED, f"This server does not exist. Skipping {server_id}...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if platform.system() == 'Windows':
            system("pause")
