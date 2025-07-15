import ctypes
import platform
from enum import IntEnum

system = platform.system()
if system == "Windows":
    lib_name = './enet/enet.dll'
elif system == "Darwin":
    lib_name = './enet/enet.dylib'
else:
    lib_name = './enet/enet.so'

try:
    enet = ctypes.CDLL(lib_name)
except OSError:
    print(f"Failed to load {lib_name}. Ensure it is compiled and located in the 'enet' directory.")
    exit(1)

class TankPacket(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint8),
        ("unk1", ctypes.c_uint8),
        ("unk2", ctypes.c_uint8),
        ("unk3", ctypes.c_uint8),
        ("net_id", ctypes.c_uint32),
        ("sec_id", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("unk6", ctypes.c_float),
        ("value", ctypes.c_uint32),
        ("vector_x", ctypes.c_float),
        ("vector_y", ctypes.c_float),
        ("vector_x2", ctypes.c_float),
        ("vector_y2", ctypes.c_float),
        ("unk12", ctypes.c_float),
        ("int_x", ctypes.c_int32),
        ("int_y", ctypes.c_int32),
        ("extended_data_length", ctypes.c_uint32)
    ]

class ENetAddress(ctypes.Structure):
    _fields_ = [
        ("host", ctypes.c_uint8 * 16),
        ("port", ctypes.c_uint16),
        ("sin6_scope_id", ctypes.c_uint16)
    ]

class ENetEventType(IntEnum):
    NONE = 0
    CONNECT = 1
    DISCONNECT = 2
    RECEIVE = 3
    DISCONNECT_TIMEOUT = 4

class ENetPacket(ctypes.Structure):
    _fields_ = [
        ("referenceCount", ctypes.c_size_t),           # size_t
        ("flags", ctypes.c_uint32),                    # enet_uint32
        ("data", ctypes.POINTER(ctypes.c_uint8)),      # enet_uint8*
        ("dataLength", ctypes.c_size_t),               # size_t
        ("freeCallback", ctypes.c_void_p),             # ENetPacketFreeCallback (function pointer)
        ("userData", ctypes.c_void_p)                  # void*
    ]

class ENetEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),           # ENetEventType (enum)
        ("peer", ctypes.c_void_p),        # ENetPeer* 
        ("channelID", ctypes.c_uint8),    # enet_uint8
        ("data", ctypes.c_uint32),        # enet_uint32
        ("packet", ctypes.c_void_p)       # ENetPacket*
    ]

enet_initialize = enet.enet_initialize
enet_initialize.argtypes = []
enet_initialize.restype = ctypes.c_int

enet_host_create = enet.enet_host_create
enet_host_create.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
enet_host_create.restype = ctypes.c_void_p

enet_host_service = enet.enet_host_service
enet_host_service.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
enet_host_service.restype = ctypes.c_int

enet_address_set_host = enet.enet_address_set_host
enet_address_set_host.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
enet_address_set_host.restype = ctypes.c_int

enet_host_connect = enet.enet_host_connect
enet_host_connect.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32]
enet_host_connect.restype = ctypes.c_void_p

enet_host_use_new_packet = enet.enet_host_use_new_packet
enet_host_use_new_packet.argtypes = [ctypes.c_void_p]
enet_host_use_new_packet.restype = None

enet_host_use_crc32 = enet.enet_host_use_crc32
enet_host_use_crc32.argtypes = [ctypes.c_void_p]
enet_host_use_crc32.restype = None

enet_host_compress_with_range_coder = enet.enet_host_compress_with_range_coder
enet_host_compress_with_range_coder.argtypes = [ctypes.c_void_p]
enet_host_compress_with_range_coder.restype = ctypes.c_int

enet_host_destroy = enet.enet_host_destroy
enet_host_destroy.argtypes = [ctypes.c_void_p]
enet_host_destroy.restype = ctypes.c_int

enet_packet_destroy = enet.enet_packet_destroy
enet_packet_destroy.argtypes = [ctypes.c_void_p]
enet_packet_destroy.restype = None

enet_peer_send = enet.enet_peer_send
enet_peer_send.argtypes = [ctypes.c_void_p, ctypes.c_uint8, ctypes.c_void_p]
enet_peer_send.restype = ctypes.c_int

enet_packet_create = enet.enet_packet_create
enet_packet_create.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32]
enet_packet_create.restype = ctypes.POINTER(ENetPacket)

enet_peer_disconnect = enet.enet_peer_disconnect
enet_peer_disconnect.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
enet_peer_disconnect.restype = None