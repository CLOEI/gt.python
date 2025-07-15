from enums import NetGamePacket, NetMessage
from ffi import TankPacket, enet_peer_disconnect
from utils import read_u32
import ctypes

from variant_handler import VariantHandler

class PacketHandler:
    @staticmethod
    def handle(player, packet):
        if packet.dataLength < 4:
            print("Packet data is too short to read message type.")
            return
        message_type = NetMessage(read_u32(packet.data))

        data_start = ctypes.addressof(packet.data.contents) + 4
        if message_type == NetMessage.ServerHello:
            data = None
            if player.redirected:
                data = (
                    "UUIDToken|{}\nprotocol|{}\nfhash|{}\nmac|{}\nrequestedName|{}\n"
                    "hash2|{}\nfz|{}\nf|{}\nplayer_age|{}\ngame_version|{}\nlmode|{}\n"
                    "cbits|{}\nrid|{}\nGDPR|{}\nhash|{}\ncategory|{}\ntoken|{}\n"
                    "total_playtime|{}\ndoor_id|{}\nklv|{}\nmeta|{}\nplatformID|{}\n"
                    "deviceVersion|{}\nzf|{}\ncountry|{}\nuser|{}\nwk|{}\naat|{}\n"
                ).format(
                    player.save_data.uuid,
                    player.save_data.protocol,
                    player.save_data.fhash,
                    player.save_data.mac,
                    player.save_data.requested_name,
                    player.save_data.hash2,
                    player.save_data.fz,
                    player.save_data.f,
                    player.save_data.player_age,
                    player.save_data.game_version,
                    player.save_data.lmode,
                    player.save_data.cbits,
                    player.save_data.rid,
                    player.save_data.gdpr,
                    player.save_data.hash,
                    player.save_data.category,
                    player.save_data.token,
                    player.save_data.total_play_time,
                    player.save_data.door_id,
                    player.save_data.klv,
                    player.save_data.meta,
                    player.save_data.platform_id,
                    player.save_data.device_version,
                    player.save_data.zf,
                    player.save_data.country,
                    player.save_data.user,
                    player.save_data.wk,
                    player.save_data.aat,
                )
                player.redirected = False
            else:
                data = f"protocol|{player.save_data.protocol}\nltoken|{player.save_data.ltoken}\nplatformID|{player.save_data.platform_id}\n"
            player.send_packet(NetMessage.GenericText, data)

        if message_type == NetMessage.GameMessage:
            try:
                text_data = ctypes.string_at(data_start, packet.dataLength - 4).decode('utf-8').strip()
                print(f"Game message received: {text_data}")

                if "action|logon_fail" in text_data:
                    enet_peer_disconnect(player.peer, 0)
            except UnicodeDecodeError:
                print("Failed to decode game message as UTF-8.")

        if message_type == NetMessage.GamePacket:
            tank_data_ptr = ctypes.cast(data_start, ctypes.POINTER(TankPacket))
            tank_data = tank_data_ptr.contents
            tank_type = NetGamePacket(tank_data.type)

            if tank_type == NetGamePacket.CallFunction:
                tank_packet_size = ctypes.sizeof(TankPacket)
                extended_data_start = data_start + tank_packet_size
                extended_data = ctypes.string_at(extended_data_start, tank_data.extended_data_length)
                VariantHandler.handle(player, extended_data)
            
            if tank_type == NetGamePacket.PingRequest:
                print("Received PingRequest, sending PingReply.")
                tank_packet = TankPacket()
                tank_packet.type = NetGamePacket.PingReply.value
                tank_packet.vector_x = 64.0
                tank_packet.vector_y = 64.0
                tank_packet.vector_x2 = 1000.0
                tank_packet.vector_y2 = 250.0
                tank_packet.value = tank_data.value + 5000
                player.send_packet_raw(tank_packet)
