from ffi import enet_peer_disconnect
from variant import VariantList
from enums import NetMessage

class VariantHandler:
    @staticmethod
    def handle(player, data):
        variant_list = VariantList.deserialize(data)
        function_name = variant_list.get(0).as_string()
        
        print(f"Handling variant function: {function_name}")

        if function_name == "OnSendToServer":
            port = variant_list.get(1).as_int32()
            token = variant_list.get(2).as_string()
            user_id = variant_list.get(3).as_string()
            server_data = variant_list.get(4).as_string().split('|')
            aat = variant_list.get(5).as_int32()

            player.address = server_data[0]
            player.port = port
            player.redirected = True
            player.save_data.token = token
            player.save_data.user = user_id
            player.save_data.door_id = server_data[1]
            player.save_data.uuid = server_data[2]
            player.save_data.aat = aat

            enet_peer_disconnect(player.peer, 0)

        if function_name == "OnSuperMainStartAcceptLogonHrdxs47254722215a":
            player.send_packet(NetMessage.GenericText, "action|enter_game\n")