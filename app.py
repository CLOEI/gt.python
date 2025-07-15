from enums import LoginMethod, NetMessage
from ffi import  enet_initialize, enet_host_create, enet_host_use_crc32, enet_host_use_new_packet, enet_host_compress_with_range_coder, ENetAddress, enet_address_set_host, enet_host_connect, enet_host_service, ENetEvent, ENetEventType, ENetPacket, enet_packet_create, enet_peer_send, enet_packet_destroy
from packet_handler import PacketHandler
from utils import GAME_VERSION, PROTOCOL_VERSION, fetch_login_urls, fetch_server_data, generate_klv, hash_string, login_via_growtopia, random_hex, random_mac
import ctypes

if enet_initialize() != 0:
    print("Failed to initialize ENet.")

class SaveData:
    def __init__(self):
        self.tank_id_name = None
        self.tank_id_pass = None
        self.requested_name = None
        self.ltoken = None
        self.token = None
        self.lmode = "1"
        self.f = "1"
        self.protocol = PROTOCOL_VERSION
        self.game_version = GAME_VERSION
        self.fz = "21905432"
        self.cbits = "0"
        self.player_age = "20"
        self.gdpr = "2"
        self.category = "_-5100"
        self.total_play_time = "0"
        self.meta = None
        self.fhash = "-716928004"
        self.rid = random_hex(32, uppercase=True)
        self.platform_id = "0,1,1"
        self.device_version = "0"
        self.country = "us"
        self.mac = random_mac()
        self.wk = random_hex(32, uppercase=True)
        self.zf = "-1623530258"
        self.klv = generate_klv(self.protocol, self.rid)
        self.hash = hash_string(f"{self.mac}RT")
        self.hash2 = hash_string(f"{random_hex(16, uppercase=True)}RT")
        self.uuid = None
        self.user = None
        self.door_id = None
        self.aat = None

    def build(self):
        fields = [
            ("tankIDName", self.tank_id_name),
            ("tankIDPass", self.tank_id_pass),
            ("requestedName", self.requested_name),
            ("f", self.f),
            ("protocol", self.protocol),
            ("game_version", self.game_version),
            ("fz", self.fz),
            ("cbits", self.cbits),
            ("player_age", self.player_age),
            ("GDPR", self.gdpr),
            ("category", self.category),
            ("totalPlaytime", self.total_play_time),
            ("klv", self.klv),
            ("hash2", self.hash2),
            ("meta", self.meta),
            ("fhash", self.fhash),
            ("rid", self.rid),
            ("platformID", self.platform_id),
            ("deviceVersion", self.device_version),
            ("country", self.country),
            ("hash", self.hash),
            ("mac", self.mac),
            ("wk", self.wk),
            ("zf", self.zf),
        ]
        return "\n".join(f"{k}|{v if v is not None else ''}" for k, v in fields)

class Player:
    def __init__(self, login_method=LoginMethod.LEGACY, username=None, password=None):
        if login_method is LoginMethod.LEGACY and (username is None or password is None):
            raise ValueError("Username and password must be provided for legacy login method.")
        
        self.world_name = None
        self.address = None
        self.port = None
        self.redirected = False
        self.login_method = login_method
        self.username = username
        self.password = password
        self.save_data = SaveData()
        self.login_urls = None
        self.peer = None
        self.host = enet_host_create(None, 1, 2, 0, 0);
        if self.host is None:
            print("An error occurred while trying to create an ENet client host.")
            return
        enet_host_use_new_packet(self.host)
        enet_host_use_crc32(self.host)
        enet_host_compress_with_range_coder(self.host)
    
    def connect(self):
        if self.redirected:
            enet_addr = ENetAddress()
            if enet_address_set_host(ctypes.byref(enet_addr), self.address.encode('utf-8')) != 0:
                print("Failed to set host address.")
                return
            enet_addr.port = int(self.port)
        else:
            server_data = fetch_server_data()
            self.save_data.meta = server_data['meta']
            self.login_urls = fetch_login_urls(self.save_data.build())
            self.save_data.ltoken = login_via_growtopia(self.login_urls['growtopia'], self.username, self.password)

            enet_addr = ENetAddress()
            if enet_address_set_host(ctypes.byref(enet_addr), server_data['server'].encode('utf-8')) != 0:
                print("Failed to set host address.")
                return
            enet_addr.port = int(server_data['port'])

        self.peer = enet_host_connect(self.host, ctypes.byref(enet_addr), 2, 0)
        if self.peer is None:
            print("Failed to create a connection to the server.")
        
        self.loop()
    
    def send_packet(self, packet_type, data):
        packet = enet_packet_create(None, 4 + len(data), 1)
        packet_type_ptr = ctypes.cast(packet.contents.data, ctypes.POINTER(ctypes.c_uint32))
        packet_type_ptr[0] = packet_type.value
        data_start = ctypes.addressof(packet.contents.data.contents) + 4
        ctypes.memmove(data_start, data.encode("utf-8"), len(data))
        if enet_peer_send(self.peer, 0, packet) < 0:
            print("Failed to send packet.")
        else:
            print(f"Sent packet of type: {packet_type.name}")

    def send_packet_raw(self, tank_packet):
        packet = enet_packet_create(None, 4 + ctypes.sizeof(tank_packet) + tank_packet.extended_data_length, 1)
        packet_type_ptr = ctypes.cast(packet.contents.data, ctypes.POINTER(ctypes.c_uint32))
        packet_type_ptr[0] = NetMessage.GamePacket.value
        data_start = ctypes.addressof(packet.contents.data.contents) + 4
        ctypes.memmove(data_start, ctypes.byref(tank_packet), ctypes.sizeof(tank_packet))
        if enet_peer_send(self.peer, 0, packet) < 0:
            print("Failed to send tank packet.")
        else:
            print("Sent tank packet successfully.")


    def loop(self):
        event = ENetEvent()
        while True:
            if enet_host_service(self.host, ctypes.byref(event), 250) > 0:
                if event.type == ENetEventType.CONNECT:
                    print("Connected to server.")
                elif event.type == ENetEventType.RECEIVE:
                    packet = ctypes.cast(event.packet, ctypes.POINTER(ENetPacket)).contents
                    PacketHandler.handle(self, packet)
                    enet_packet_destroy(event.packet)
                elif event.type == ENetEventType.DISCONNECT:
                    print("Disconnected from server.")
                    if self.redirected:
                        print("Redirecting to new server...")
                    self.connect()
                    break
                elif event.type == ENetEventType.DISCONNECT_TIMEOUT:
                    print("Connection timed out.")
                    break


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not username or not password:
        raise ValueError("Username and password must be set in the environment variables.")

    player = Player(username=username, password=password)
    player.connect()