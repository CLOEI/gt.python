from enum import Enum

class LoginMethod(Enum):
    APPLE = "apple"
    GOOGLE = "google"
    LEGACY = "legacy"

class NetMessage(Enum):
    Unknown = 0
    ServerHello = 1
    GenericText = 2
    GameMessage = 3
    GamePacket = 4
    Error = 5
    Track = 6
    ClientLogRequest = 7
    ClientLogResponse = 8
    Max = 9

class NetGamePacket(Enum):
    State = 0
    CallFunction = 1
    UpdateStatus = 2
    TileChangeRequest = 3
    SendMapData = 4
    SendTileUpdateData = 5
    SendTileUpdateDataMultiple = 6
    TileActivateRequest = 7
    TileApplyDamage = 8
    SendInventoryState = 9
    ItemActivateRequest = 10
    ItemActivateObjectRequest = 11
    SendTileTreeState = 12
    ModifyItemInventory = 13
    ItemChangeObject = 14
    SendLock = 15
    SendItemDatabaseData = 16
    SendParticleEffect = 17
    SetIconState = 18
    ItemEffect = 19
    SetCharacterState = 20
    PingReply = 21
    PingRequest = 22
    GotPunched = 23
    AppCheckResponse = 24
    AppIntegrityFail = 25
    Disconnect = 26
    BattleJoin = 27
    BattleEvent = 28
    UseDoor = 29
    SendParental = 30
    GoneFishin = 31
    Steam = 32
    PetBattle = 33
    Npc = 34
    Special = 35
    SendParticleEffectV2 = 36
    ActivateArrowToItem = 37
    SelectTileIndex = 38
    SendPlayerTributeData = 39
    FTUESetItemToQuickInventory = 40
    PVENpc = 41
    PVPCardBattle = 42
    PVEApplyPlayerDamage = 43
    PVENPCPositionUpdate = 44
    SetExtraMods = 45
    OnStepTileMod = 46