from enum import Enum


class Track(Enum):
    Unknown = -1
    Melbourne = 0
    Paul_Ricard = 1
    Shanghai = 2
    Sakhir = 3  # Bahrain
    Catalunya = 4
    Monaco = 5
    Montreal = 6
    Silverstone = 7
    Hockenheim = 8
    Hungaroring = 9
    Spa = 10
    Monza = 11
    Singapore = 12
    Suzuka = 13
    Abu_Dhabi = 14
    Texas = 15
    Brazil = 16
    Austria = 17
    Sochi = 18
    Mexico = 19
    Baku = 20  # Azerbaijan
    Sakhir_Short = 21
    Silverstone_Short = 22
    Texas_Short = 23
    Suzuka_Short = 24
    Hanoi = 25
    Zandvoort = 26
    Imola = 27
    Portimao = 28
    Jeddah = 29
    Miami = 30
    Las_Vegas = 31
    Losail = 32


class SessionType(Enum):
    Unknown = 0
    P1 = 1
    P2 = 2
    P3 = 3
    Short_P = 4
    Q1 = 5
    Q2 = 6
    Q3 = 7
    Short_Q = 8
    OSQ = 9
    R = 10
    R2 = 11
    R3 = 12
    Time_Trial = 13


class Weather(Enum):
    Clear = 0
    Light_Cloud = 1
    Overcast = 2
    Light_Rain = 3
    Heavy_Rain = 4
    Storm = 5


class SurfaceType(Enum):
    Tarmac = 0
    Rumble_strip = 1
    Concrete = 2
    Rock = 3
    Gravel = 4
    Mud = 5
    Sand = 6
    Grass = 7
    Water = 8
    Cobblestone = 9
    Metal = 10
    Ridged = 11
