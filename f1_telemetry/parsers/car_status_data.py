import struct
from dataclasses import dataclass

from f1_telemetry.parsers.packet_header import PacketHeader


@dataclass
class CarStatusData:
    m_tractionControl: int          # 0 = off, 1 = medium, 2 = full
    m_antiLockBrakes: int           # 0 = off, 1 = on
    m_fuelMix: int                  # 0 = lean, 1 = standard, 2 = rich, 3 = max
    m_frontBrakeBias: int           # Front brake bias (percentage)
    m_pitLimiterStatus: int         # 0 = off, 1 = on
    m_fuelInTank: float             # Current fuel mass
    m_fuelCapacity: float           # Fuel capacity
    m_fuelRemainingLaps: float      # Fuel remaining in terms of laps
    m_maxRPM: int                   # Cars max RPM, point of rev limiter
    m_idleRPM: int                  # Cars idle RPM
    m_maxGears: int                 # Maximum number of gears
    m_drsAllowed: int               # 0 = not allowed, 1 = allowed
    m_drsActivationDistance: int    # 0 = DRS not available, non-zero = available in [X] metres
    m_actualTyreCompound: int       # Actual tyre compound (16=C5, 17=C4, 18=C3, 19=C2, 20=C1, 21=C0, 7=inter, 8=wet)
    m_visualTyreCompound: int       # Visual tyre compound (16=soft, 17=medium, 18=hard, 7=inter, 8=wet)
    m_tyresAgeLaps: int             # Age in laps of the current set of tyres
    m_vehicleFIAFlags: int          # -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow
    m_enginePowerICE: float         # Engine power output of ICE (W)
    m_enginePowerMGUK: float        # Engine power output of MGU-K (W)
    m_ersStoreEnergy: float         # ERS energy store in Joules
    m_ersDeployMode: int            # 0 = none, 1 = medium, 2 = hotlap, 3 = overtake
    m_ersHarvestedThisLapMGUK: float  # ERS energy harvested this lap by MGU-K
    m_ersHarvestedThisLapMGUH: float  # ERS energy harvested this lap by MGU-H
    m_ersDeployedThisLap: float     # ERS energy deployed this lap
    m_networkPaused: int            # Whether the car is paused in a network game

    _struct = struct.Struct("<BBBBBfffHHBBHBBBbfffBfffB")

    @classmethod
    def from_buffer(cls, buffer: bytes, offset: int = 0):
        unpacked = cls._struct.unpack_from(buffer, offset)
        return cls(
            m_tractionControl=unpacked[0],
            m_antiLockBrakes=unpacked[1],
            m_fuelMix=unpacked[2],
            m_frontBrakeBias=unpacked[3],
            m_pitLimiterStatus=unpacked[4],
            m_fuelInTank=unpacked[5],
            m_fuelCapacity=unpacked[6],
            m_fuelRemainingLaps=unpacked[7],
            m_maxRPM=unpacked[8],
            m_idleRPM=unpacked[9],
            m_maxGears=unpacked[10],
            m_drsAllowed=unpacked[11],
            m_drsActivationDistance=unpacked[12],
            m_actualTyreCompound=unpacked[13],
            m_visualTyreCompound=unpacked[14],
            m_tyresAgeLaps=unpacked[15],
            m_vehicleFIAFlags=unpacked[16],
            m_enginePowerICE=unpacked[17],
            m_enginePowerMGUK=unpacked[18],
            m_ersStoreEnergy=unpacked[19],
            m_ersDeployMode=unpacked[20],
            m_ersHarvestedThisLapMGUK=unpacked[21],
            m_ersHarvestedThisLapMGUH=unpacked[22],
            m_ersDeployedThisLap=unpacked[23],
            m_networkPaused=unpacked[24],
        )


@dataclass
class PacketCarStatusData:
    m_header: PacketHeader
    m_carStatusData: list[CarStatusData]

    @classmethod
    def from_buffer(cls, buffer: bytes):
        header = PacketHeader.from_buffer(buffer, 0)
        offset = PacketHeader._struct.size

        cars = []
        for _ in range(22):  # cs_maxNumCarsInUDPData
            car = CarStatusData.from_buffer(buffer, offset)
            cars.append(car)
            offset += CarStatusData._struct.size

        return cls(header, cars)
