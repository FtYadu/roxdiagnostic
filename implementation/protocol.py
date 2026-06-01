"""ROX 01 UDS Protocol Implementation

Unified Diagnostic Services (UDS) protocol specification for ROX 01 vehicles.
Based on ISO 14229-1 (road vehicles diagnostic services)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import struct

class UDSService(Enum):
    """UDS Service Codes"""
    SESSION_CONTROL = 0x10
    RESET = 0x11
    READ_DID = 0x22                    # ReadDataByIdentifier
    WRITE_DID = 0x2E                   # WriteDataByIdentifier
    READ_MEMORY = 0x23                 # ReadMemoryByAddress
    WRITE_MEMORY = 0x3D                # WriteMemoryByAddress
    TESTER_PRESENT = 0x3E
    READ_DTC = 0x19
    CLEAR_DTC = 0x14
    SECURITY_ACCESS = 0x27
    TRANSFER_DATA = 0x36
    REQUEST_DOWNLOAD = 0x34            # RequestFileDownload (firmware)
    TRANSFER_EXIT = 0x37

class DiagnosticSession(Enum):
    """Diagnostic Sessions"""
    DEFAULT = 0x01
    PROGRAMMING = 0x10
    EXTENDED = 0x03

@dataclass
class UDSRequest:
    """UDS Request Frame"""
    service: int
    data: bytes = b''
    
    def encode(self) -> bytes:
        """Encode to CAN frame"""
        return bytes([self.service]) + self.data

@dataclass
class UDSResponse:
    """UDS Response Frame"""
    service: int
    data: bytes
    
    @property
    def is_success(self) -> bool:
        return (self.service & 0x40) == 0x40
    
    @property
    def error_code(self) -> Optional[int]:
        if not self.is_success and self.service == 0x7F:
            return self.data[1] if len(self.data) > 1 else None
        return None

# ROX 01 DID (Data Identifiers) Database
ROX_PID_DATABASE = {
    # Engine Parameters
    0x010C: {"name": "Engine_RPM", "length": 2, "scale": 0.25, "offset": 0, "unit": "rpm"},
    0x010D: {"name": "Vehicle_Speed", "length": 1, "scale": 1.0, "offset": 0, "unit": "km/h"},
    0x010E: {"name": "Timing_Advance", "length": 1, "scale": 0.5, "offset": -64, "unit": "degrees"},
    0x010F: {"name": "Intake_Air_Temp", "length": 1, "scale": 1.0, "offset": -40, "unit": "C"},
    0x0110: {"name": "MAF_Airflow", "length": 2, "scale": 0.01, "offset": 0, "unit": "g/s"},
    0x0111: {"name": "Absolute_Load", "length": 1, "scale": 0.39, "offset": 0, "unit": "%"},
    0x0112: {"name": "Fuel_Pressure", "length": 1, "scale": 3.0, "offset": 0, "unit": "kPa"},
    0x0113: {"name": "O2_Sensor_1", "length": 2, "scale": 0.0078, "offset": 0, "unit": "V"},
    0x0114: {"name": "Short_Term_Trim_B1", "length": 1, "scale": 0.39, "offset": -100, "unit": "%"},
    0x0115: {"name": "Long_Term_Trim_B1", "length": 1, "scale": 0.39, "offset": -100, "unit": "%"},
    
    # Temperature & Cooling
    0x0105: {"name": "Engine_Coolant_Temp", "length": 1, "scale": 1.0, "offset": -40, "unit": "C"},
    0x011E: {"name": "Engine_Load_Calculated", "length": 1, "scale": 0.39, "offset": 0, "unit": "%"},
    0x011F: {"name": "Fuel_Trim_System_Status", "length": 1, "scale": 1.0, "offset": 0, "unit": "flags"},
    
    # EV-Specific (ROX ADAMAS is EV)
    0xF190: {"name": "VIN", "length": 17, "scale": 1.0, "offset": 0, "unit": "string"},
    0xF18C: {"name": "OBD_Module_Status", "length": 1, "scale": 1.0, "offset": 0, "unit": "flags"},
    0xF186: {"name": "Active_Diagnostic_Session", "length": 1, "scale": 1.0, "offset": 0, "unit": "enum"},
    0x022100: {"name": "Battery_State_of_Charge", "length": 2, "scale": 0.1, "offset": 0, "unit": "%"},
    0x022101: {"name": "Battery_Voltage", "length": 2, "scale": 0.01, "offset": 0, "unit": "V"},
    0x022102: {"name": "Battery_Current", "length": 2, "scale": 0.1, "offset": -3200, "unit": "A"},
    0x022103: {"name": "Motor_Speed", "length": 2, "scale": 1.0, "offset": 0, "unit": "rpm"},
    0x022104: {"name": "Motor_Torque", "length": 2, "scale": 0.1, "offset": 0, "unit": "Nm"},
}

# CAN Frame Configuration
CAN_CONFIG = {
    "BROADCAST_REQUEST_ID": 0x7DF,
    "BROADCAST_RESPONSE_ID": 0x7E8,
    "BOOTLOADER_TX_ID": 0x731,
    "BOOTLOADER_RX_ID": 0x732,
    "BITRATE": 500000,
}

def parse_dtc(dtc_bytes: bytes) -> str:
    """Parse DTC from 4-byte format"""
    if len(dtc_bytes) < 4:
        return "INVALID"
    
    code = struct.unpack('>I', dtc_bytes[:4])[0]
    dtc_type = ['P', 'C', 'B', 'U'][(code >> 24) & 0x03]
    dtc_code = code & 0xFFFF
    
    return f"{dtc_type}{dtc_code:04X}"

def format_parameter(param_id: int, value_bytes: bytes) -> Optional[float]:
    """Format raw parameter bytes using scaling from database"""
    if param_id not in ROX_PID_DATABASE:
        return None
    
    param = ROX_PID_DATABASE[param_id]
    
    if param['length'] == 1:
        raw = value_bytes[0]
    elif param['length'] == 2:
        raw = struct.unpack('>H', value_bytes[:2])[0]
    elif param['length'] == 4:
        raw = struct.unpack('>I', value_bytes[:4])[0]
    else:
        return None
    
    return (raw * param['scale']) + param['offset']

def build_read_did_request(did: int) -> bytes:
    """Build UDS ReadDataByIdentifier request"""
    return bytes([
        0x03,
        UDSService.READ_DID.value,
        (did >> 8) & 0xFF,
        did & 0xFF
    ])

def build_clear_dtc_request() -> bytes:
    """Build UDS ClearDiagnosticInformation request"""
    return bytes([
        0x04,
        UDSService.CLEAR_DTC.value,
        0xFF,
        0xFF,
        0xFF
    ])

def build_reset_request(reset_type: str = 'soft') -> bytes:
    """Build UDS ECUReset request"""
    reset_codes = {
        'soft': 0x01,
        'hard': 0x02,
        'full': 0x03,
    }
    
    code = reset_codes.get(reset_type, 0x01)
    
    return bytes([
        0x02,
        UDSService.RESET.value,
        code
    ])

def build_enter_bootloader_request() -> bytes:
    """Build request to enter bootloader mode"""
    return bytes([0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

def build_exit_bootloader_request() -> bytes:
    """Build request to exit bootloader and reset"""
    return bytes([0x11, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
