from enum import Enum
from . import Definitions


class Protocol:
    CONST_FRECUENCY = 65536  # 2^16 -> 16 bits -> MHz

    def __init__(
        self,
        phy_index: bytes = 0,
        name: str = "Base Protocol",
        phy_label: str = "Base Protocol",
        base_frequency: float = 0,
        spacing: float = 0,
        channel_range: list = [0, 0],
        pcap_header: int = 147,
        common_names: list = [],
        profile: str = "Default",
    ):
        self.phy_index = phy_index
        self.name = name
        self.phy_label = phy_label
        self.base_frequency = base_frequency
        self.spacing = spacing
        self.channel_range = channel_range
        self.pcap_header = pcap_header
        self.common_names = common_names
        self.profile = profile

    def find_by_name(self, name: str):
        if name in self.common_names:
            return self
        return None

    def get_profile(self):
        return self.profile

    def get_common_name_str(self):
        return ", ".join(self.common_names)

    def get_phy_index(self):
        return self.phy_index

    def get_name(self):
        return self.name

    def get_phy_label(self):
        return self.phy_label

    def get_base_frequency(self):
        return self.base_frequency

    def get_spacing(self):
        return self.spacing

    def get_channel_range(self):
        return self.channel_range

    def get_pcap_header(self):
        return self.pcap_header

    def __calculate_fractional_frequency(self, frequency: int) -> (int, int):
        """Calculate the fractional frequency"""
        # The fractional frequency is calculated as
        # Get the integer value of the frequency
        # Then get the fractional value of the frequency
        # The decimal part of the frequency is divided by 65536 -> 2^16
        integer_value = int(frequency)
        fractional_value = int((integer_value - integer_value) * self.CONST_FRECUENCY)
        return integer_value, fractional_value

    def calculate_frequency(self, frequency: int) -> bytes:
        """
        Return the frequency in bytes.

        Args:
          frequency (int): The frequency in Hz.

        Returns:
          Bytes: A bytes containing two bytes arrays.
            - The first bytes array represents the integer value of the frequency.
            - The second bytes array represents the fractional value of the frequency in MHz.
        """
        (frequency_int, frequency_fract) = self.__calculate_fractional_frequency(
            frequency
        )
        # The frequency is returned as a 4 bytes array
        # 0-1 bytes: Integer value of the frequency
        frequency_int_bytes = frequency_int.to_bytes(2, byteorder="little")
        # 2-3 bytes: Fractional value of the frequency in MHz
        frequency_fract_bytes = frequency_fract.to_bytes(2, byteorder="little")
        return frequency_int_bytes + frequency_fract_bytes

    def get_channel_bytes(self, channel_index: int) -> bytes:
        """Return the channel in bytes"""
        for _channel in self.channel_range:
            if _channel[0] == channel_index:
                return _channel[1]
        return b""

    def get_channel_range_bytes(self, channel: int) -> int:
        """Return the channel range in bytes"""
        for _channel in self.channel_range:
            if _channel[0] == channel:
                return _channel
        return 0

    def get_frequency_by_channel(self, channel: int) -> float:
        """Return the frequency by channel"""
        for _channel in self.channel_range:
            if _channel[0] == channel:
                return _channel[1]
        return 0

    def command_start(self) -> bytes:
        """Return the start command of the protocol"""
        return Definitions.PacketCommand(Definitions.SnifferCommands.CMD_START.value)

    def command_stop(self) -> bytes:
        """Return the start command of the protocol"""
        return Definitions.PacketCommand(Definitions.SnifferCommands.CMD_STOP.value)

    def command_ping(self) -> bytes:
        """Return the ping command of the protocol"""
        return Definitions.PacketCommand(Definitions.SnifferCommands.CMD_PING.value)

    def command_cfg_phy(self) -> bytes:
        """Return the command for configure the PHY"""
        return Definitions.PacketCommand(
            Definitions.SnifferCommands.CMD_CFG_PHY.value, bytes(self.phy_index)
        )

    def command_cfg_frequency(self, channel: int) -> bytes:
        """Return the command for configure the frequency"""
        get_channel = self.get_channel_bytes(channel)
        get_frequency = self.calculate_frequency(get_channel)

        return Definitions.PacketCommand(
            Definitions.SnifferCommands.CMD_CFG_FREQUENCY.value, get_frequency
        )

    def command_cfg_init_address(self, address: bytes) -> bytes:
        """Return the command for configure the initiator address"""
        return Definitions.PacketCommand(
            Definitions.SnifferCommands.CMD_CFG_BLE_INITIATOR_ADDRESS.value, address
        )

    def command_startup(self, channel: int) -> list:
        """Return the startup command of the protocol"""
        return [
            self.command_ping(),
            self.command_stop(),
            self.command_cfg_phy(),
            self.command_cfg_frequency(channel),
            self.command_start(),
        ]

    @property
    def list_channel_range(self):
        channels = []
        for channel in self.channel_range:
            channels.append(channel[0])
        return channels

    def __str__(self):
        return f"PHY Index: {self.phy_index}\nName: {self.name}\nPHY Label: {self.phy_label}\nBase Frequency: {self.base_frequency}\nSpacing: {self.spacing}\nChannel Range: {self.channel_range}\nPCAP Header: {self.pcap_header}"


PROTOCOL_BLE = Protocol(
    phy_index=bytearray([0x13]),
    name="Bluetooth LE",
    phy_label="2402 MHz - Freq Band",
    base_frequency=2402.0,
    spacing=2,
    channel_range=[(37, 2402), (38, 2426), (39, 2480)],
    pcap_header=147,
    common_names=["ble", "bluetooth", "bluetoothle"],
)

PROTOCOL_ZIGBEE = Protocol(
    phy_index=bytearray([0x12]),
    name="Zigbee",
    phy_label="2405 MHz - Freq Band",
    base_frequency=2405.0,
    spacing=5,
    channel_range=[
        (channel, (2405.0 + (5 * (channel - 11)))) for channel in range(11, 27)
    ],
    pcap_header=147,
    common_names=["zigbee", "zig", "zb"],
    profile="Zigbee",
)

PROTOCOL_THREAD = Protocol(
    phy_index=bytearray([0x12]),
    name="Thread",
    phy_label="2405 MHz - Freq Band",
    base_frequency=2405.0,
    spacing=5,
    channel_range=[
        (channel, (2405.0 + (5 * (channel - 11)))) for channel in range(11, 27)
    ],
    pcap_header=147,
    common_names=["thread"],
    profile="Thread",
)


class LoraProtocol(Protocol):
    def __init__(self, packet_bytes: bytes) -> None:
        super().__init__(packet_bytes)
        self.badwidth_range = [
            7.8,
            10.4,
            15.6,
            20.8,
            31.25,
            41.7,
            62.5,
            125,
            250.0,
            500.0,
        ]

    def set_badwidth(self, badwidth_index: int) -> None:
        self.badwidth = self.badwidth_range[badwidth_index]


PROTOCOL_LORA = Protocol(
    phy_index=bytearray([0x14]),
    name="LoRa",
    phy_label="915 MHz - Freq Band",
    base_frequency=915.0,
    spacing=125,
    channel_range=[(0, 433), (1, 434), (2, 435)],
    pcap_header=148,
    profile="Default",
)


class PROTOCOLSLIST(Definitions.BaseEnum):
    PROTOCOL_BLE: Protocol = PROTOCOL_BLE
    PROTOCOL_ZIGBEE: Protocol = PROTOCOL_ZIGBEE
    PROTOCOL_THREAD: Protocol = PROTOCOL_THREAD
    PROTOCOL_LORA: Protocol = PROTOCOL_LORA

    @classmethod
    def get_list_protocols(cls):
        return list(cls)

    @classmethod
    def get_str_list_protocols(cls):
        str_list = ""
        for index, protocol in enumerate(cls):
            str_list += f"[{index}] {protocol.name}\n"
        return str_list

    @classmethod
    def get_str_list_channels(cls, protocol_index: int):
        get_protocol = cls.get_by_index(protocol_index)
        str_list = ""
        for channel in get_protocol.value.channel_range:
            str_list += f"[{channel[0]}] {channel[1]}\n"
        return str_list

    @classmethod
    def get_protocol_by_name(cls, name: str):
        for protocol in cls:
            if protocol.name == name:
                return protocol
            else:
                get_protocol = protocol.value.find_by_name(name)
                if get_protocol:
                    return get_protocol
        return None

    def __str__(self):
        return super().__str__()
