import requests
from urllib3 import disable_warnings, exceptions
from bs4 import BeautifulSoup


class ServerDoesNotExist(Exception):
    pass


class Server:
    def __init__(self, craftserve_id, primitive_address=False, special_query=False):
        self.primitive_address = primitive_address
        self.special_query = special_query
        disable_warnings(exceptions.InsecureRequestWarning)
        request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/83.0.4103.116 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.9"}
        request = requests.get("https://craftserve.pl/s/" + str(craftserve_id), headers=request_headers, verify=False)
        soup = BeautifulSoup(request.text, 'html.parser')

        try:
            server_name = soup.find("meta", property="og:title")['content']
        except TypeError:
            raise ServerDoesNotExist("The server with the given ID ({}) does not exist.".format(craftserve_id))
        server_state = soup.find("div", id="status").getText()
        online_now = int(soup.find("div", {"class": "progress-bar"})['aria-valuemin'])
        max_online = int(
            str(soup.find("span", {"style": "font-weight: bold;font-size: 16px;color: #9f9f9f;"}).getText()).strip("/"))
        primitive_address_value = "s{}.csrv.pl".format(craftserve_id)
        if primitive_address:
            server_address = primitive_address_value
        else:
            try:
                server_address = str(soup.find("div", {"class": "zielony-txt"}).getText()).rstrip()
            except AttributeError:
                server_address = primitive_address_value

        unparsed_server_details = soup.find_all("div", {"class": "staty-text col-md-6"})
        server_details = []
        for data in unparsed_server_details:
            server_details.append(BeautifulSoup(str(data), 'html.parser').find('p').getText())

        self.id = craftserve_id
        self.running = True if server_state == "ON" else False
        self.address = server_address
        self.name = server_name
        self.online_now = online_now
        self.max_online = max_online
        try:
            self.type = server_details[0]
            self.expiration_date = None if server_state == "OFF" else server_details[1]
            self.price = server_details[1] if server_state == "OFF" else server_details[2]
        except IndexError:
            pass

        if special_query and server_address is not None:
            details = requests.get("https://api.mcsrvstat.us/2/" + server_address).json()
            self.online_mode = details['online']
            self.ip = details['ip']
            self.port = details['port']
            self.motd = [] if not details['online'] else details['motd']['clean']
            self.online_list = [] if online_now == 0 else details['players']['list']
            try: # WARNING: This is shit.
                self.plugins = [] if not details['online'] or not details['debug']['query'] else details['plugins'][
                    'names']
            except KeyError:  # Something weird happened.
                self.plugins = []
