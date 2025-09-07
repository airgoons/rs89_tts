from enum import StrEnum


class UnitType(StrEnum):
    ARMOR = "ARMOR"
    ARTILLERY = "ARTILLERY"
    HEADQUARTERS = "HEADQUARTERS"
    INFANTRY = "INFANTRY"
    MECHINF = "MECHINF"
    MISSILE = "MISSILE"
    NAVY = "NAVY"
    RECONAISSANCE = "RECONAISSANCE"
    AMPHIB_ARMOR = "AMPHIB_ARMOR"
    AMPHIB_MECHINF = "AMPHIB_MECHINF"
    AMPHIB_RECON = "AMPHIB_RECON"

class UnitFormation(StrEnum):
    FRONT = "FRONT"
    ARMY = "ARMY"
    CORPS = "CORPS"
    DIVISION = "DIVISION"
    BRIGADE = "BRIGADE"
    REGIMENT = "REGIMENT"
    BATTALION = "BATTALION"
    COMPANY = "COMPANY"


class UnitDataEntry:
    filename : str
    unit_type : UnitType
    unit_formation : UnitFormation

    def __init__(self, filename: str, unit_type: UnitType, unit_formation: UnitFormation):
        self.filename = filename
        self.unit_type = unit_type
        self.unit_formation = unit_formation


SpecialCases = [
    UnitDataEntry("7A_US_F_1.png", UnitType.HEADQUARTERS, UnitFormation.ARMY),
    UnitDataEntry("7A_US_F_2.png", UnitType.MISSILE, None),
    UnitDataEntry("7A_US_F_3.png", UnitType.MISSILE, None),
    UnitDataEntry("7A_US_F_4.png", UnitType.MISSILE, None),
    UnitDataEntry("BAOR_F_1.png", UnitType.HEADQUARTERS, UnitFormation.ARMY),
    UnitDataEntry("NF_SO_F_1.png", UnitType.HEADQUARTERS, UnitFormation.FRONT),
    UnitDataEntry("RS_Ground_Units_F_286.png", UnitType.MISSILE, None),
    UnitDataEntry("RS_Ground_Units_F_287.png", UnitType.MISSILE, None),
    UnitDataEntry("SF_SO_F_1.png", UnitType.HEADQUARTERS, UnitFormation.FRONT),
    UnitDataEntry("SOUTHAG_US_F_2.png", UnitType.HEADQUARTERS, UnitFormation.ARMY),
    UnitDataEntry("SWF_SO_F_1.png", UnitType.HEADQUARTERS, UnitFormation.FRONT),
    UnitDataEntry("WF_SO_F_1.png", UnitType.HEADQUARTERS, UnitFormation.FRONT)
]