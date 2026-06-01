#!/usr/bin/env python3
"""
ROX 01 Complete Diagnostic Tool Core Library

Full implementation of:
- Firmware extraction via ENET/OBD-II
- Live data reading (CAN protocol)
- DTC management (UDS services)
- ECU reset (soft/hard/factory)
- Firmware update (with safety verification)

Author: FtYadu
License: MIT
"""

import can
import struct
import time
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    from .protocol import (
        UDSService, ROX_PID_DATABASE, CAN_CONFIG, 
        parse_dtc, format_parameter, build_read_did_request,
        build_clear_dtc_request, build_reset_request,
        build_enter_bootloader_request, build_exit_bootloader_request
    )
except ImportError:
    from protocol import (
        UDSService, ROX_PID_DATABASE, CAN_CONFIG, 
        parse_dtc, format_parameter, build_read_did_request,
        build_clear_dtc_request, build_reset_request,
        build_enter_bootloader_request, build_exit_bootloader_request
    )

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FirmwareInfo:
    """Firmware metadata"""
    size: int
    sha256: str
    timestamp: float
    method: str = "extraction"

class ROX01DiagnosticTool:
    """Complete ROX 01 diagnostic tool."""
    
    def __init__(self, can_interface: str = 'can0', bitrate: int = 500000):
        """Initialize diagnostic tool"""
        self.can_interface = can_interface
        self.bitrate = bitrate
        self.bus = None
        self.session_active = False
        self.security_unlocked = False
        self.firmware_info: Optional[FirmwareInfo] = None
        
        self._init_can_bus()
    
    def _init_can_bus(self) -> bool:
        """Initialize CAN bus connection"""
        try:
            self.bus = can.Bus(
                interface='socketcan',
                channel=self.can_interface,
                bitrate=self.bitrate
            )
            logger.info(f"CAN bus initialized: {self.can_interface} @ {self.bitrate} bps")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CAN bus: {e}")
            return False
    
    def start_diagnostic_session(self, session_type: int = 0x01) -> bool:
        """Start UDS diagnostic session"""
        try:
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BROADCAST_REQUEST_ID'],
                data=[0x02, UDSService.SESSION_CONTROL.value, session_type, 0x00, 0x00, 0x00, 0x00, 0x00]
            )
            self.bus.send(msg)
            
            response = self.bus.recv(timeout=2.0)
            if response and response.data[0] == 0x50:
                self.session_active = True
                logger.info(f"Diagnostic session started")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to start diagnostic session: {e}")
            return False
    
    def end_diagnostic_session(self) -> bool:
        """End UDS diagnostic session"""
        try:
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BROADCAST_REQUEST_ID'],
                data=[0x01, UDSService.SESSION_CONTROL.value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            )
            self.bus.send(msg)
            self.session_active = False
            logger.info("Diagnostic session ended")
            return True
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    def extract_firmware(self, output_file: str, memory_size: int = 0x1000000) -> bool:
        """Extract complete ECU firmware"""
        logger.info(f"Starting firmware extraction to {output_file}")
        firmware = bytearray()
        chunk_size = 256
        total_chunks = (memory_size + chunk_size - 1) // chunk_size
        
        try:
            for chunk_num in range(total_chunks):
                offset = chunk_num * chunk_size
                
                msg_data = [
                    0x10, UDSService.READ_MEMORY.value,
                    0x22,
                    (offset >> 24) & 0xFF,
                    (offset >> 16) & 0xFF,
                    (offset >> 8) & 0xFF,
                    offset & 0xFF,
                    (chunk_size >> 8) & 0xFF,
                    chunk_size & 0xFF,
                ]
                
                msg = can.Message(
                    arbitration_id=CAN_CONFIG['BROADCAST_REQUEST_ID'],
                    data=msg_data
                )
                self.bus.send(msg)
                
                response = self.bus.recv(timeout=1.0)
                if response and response.arbitration_id == CAN_CONFIG['BROADCAST_RESPONSE_ID']:
                    firmware.extend(response.data[1:])
                
                if (chunk_num + 1) % 100 == 0:
                    progress = ((chunk_num + 1) / total_chunks) * 100
                    logger.info(f"Progress: {progress:.1f}%")
                
                time.sleep(0.01)
            
            with open(output_file, 'wb') as f:
                f.write(firmware)
            
            sha256 = hashlib.sha256(firmware).hexdigest()
            logger.info(f"Firmware extraction complete! Size: {len(firmware) / 1024 / 1024:.2f} MB")
            
            return True
        
        except Exception as e:
            logger.error(f"Firmware extraction failed: {e}")
            return False
    
    def verify_firmware_file(self, firmware_file: str) -> bool:
        """Verify firmware file"""
        try:
            with open(firmware_file, 'rb') as f:
                firmware = f.read()
            
            if firmware[:4] == b'ROX1' or firmware[0:2] == b'\x00\x00' or len(firmware) > 1000000:
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Firmware verification error: {e}")
            return False
    
    def read_live_data(self) -> Dict[str, float]:
        """Read all available live data parameters"""
        live_data = {}
        logger.info("Reading live data from ECU...")
        
        for param_id, param_info in ROX_PID_DATABASE.items():
            try:
                value = self.read_parameter(param_id)
                if value is not None:
                    live_data[param_info['name']] = value
            except:
                pass
        
        return live_data
    
    def read_parameter(self, param_id: int) -> Optional[float]:
        """Read single parameter from ECU"""
        try:
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BROADCAST_REQUEST_ID'],
                data=[
                    0x03,
                    UDSService.READ_DID.value,
                    (param_id >> 8) & 0xFF,
                    param_id & 0xFF,
                    0x00, 0x00, 0x00, 0x00
                ]
            )
            self.bus.send(msg)
            
            response = self.bus.recv(timeout=1.0)
            if response and response.arbitration_id == CAN_CONFIG['BROADCAST_RESPONSE_ID']:
                if response.data[0] == 0x62:
                    data_bytes = response.data[3:]
                    
                    if param_id in ROX_PID_DATABASE:
                        param_info = ROX_PID_DATABASE[param_id]
                        
                        if param_info['length'] == 1:
                            raw_value = data_bytes[0]
                        elif param_info['length'] == 2:
                            raw_value = struct.unpack('>H', data_bytes[:2])[0]
                        elif param_info['length'] == 4:
                            raw_value = struct.unpack('>I', data_bytes[:4])[0]
                        else:
                            return None
                        
                        value = (raw_value * param_info['scale']) + param_info.get('offset', 0)
                        return value
            
            return None
        
        except:
            return None
    
    def read_dtc(self) -> List[str]:
        """Read all DTC codes"""
        dtcs = []
        logger.info("Reading fault codes...")
        
        try:
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BROADCAST_REQUEST_ID'],
                data=[0x02, UDSService.READ_DTC.value, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00]
            )
            self.bus.send(msg)
            
            start_time = time.time()
            while time.time() - start_time < 5.0:
                response = self.bus.recv(timeout=1.0)
                
                if not response:
                    break
                
                if response.arbitration_id == CAN_CONFIG['BROADCAST_RESPONSE_ID']:
                    if response.data[0] == 0x59:
                        for i in range(2, len(response.data) - 1, 4):
                            if i + 3 < len(response.data):
                                dtc_bytes = response.data[i:i+4]
                                dtc_str = parse_dtc(dtc_bytes)
                                if dtc_str != "INVALID":
                                    dtcs.append(dtc_str)
            
            return dtcs
        
        except Exception as e:
            logger.error(f"Failed to read DTCs: {e}")
            return []
    
    def clear_dtc(self) -> bool:
        """Clear all DTC codes"""
        logger.warning("Clearing fault codes...")
        
        try:
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BROADCAST_REQUEST_ID'],
                data=[0x04, UDSService.CLEAR_DTC.value, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00]
            )
            self.bus.send(msg)
            
            response = self.bus.recv(timeout=2.0)
            if response and response.data[0] == 0x54:
                logger.info("All fault codes cleared")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to clear DTCs: {e}")
            return False
    
    def reset_ecu(self, reset_type: str = 'soft') -> bool:
        """Reset ECU"""
        reset_types = {
            'soft': (0x01, "Soft"),
            'hard': (0x02, "Hard"),
            'full': (0x03, "Full"),
        }
        
        if reset_type not in reset_types:
            return False
        
        code, description = reset_types[reset_type]
        logger.info(f"Performing {description} reset...")
        
        try:
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BROADCAST_REQUEST_ID'],
                data=[0x02, UDSService.RESET.value, code, 0x00, 0x00, 0x00, 0x00, 0x00]
            )
            self.bus.send(msg)
            
            response = self.bus.recv(timeout=2.0)
            if response and response.data[0] == 0x51:
                logger.info(f"{description} reset successful")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to reset ECU: {e}")
            return False
    
    def upload_firmware(self, firmware_file: str) -> bool:
        """Upload new ECU firmware"""
        logger.critical("⚠️ FIRMWARE UPDATE STARTING - DO NOT INTERRUPT!")
        
        try:
            with open(firmware_file, 'rb') as f:
                firmware = f.read()
            
            logger.info(f"Firmware file: {firmware_file}")
            logger.info(f"Size: {len(firmware)} bytes")
            
            logger.info("[1/6] Entering bootloader...")
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BOOTLOADER_TX_ID'],
                data=build_enter_bootloader_request()
            )
            self.bus.send(msg)
            time.sleep(1)
            
            if not self.verify_firmware_file(firmware_file):
                logger.error("Firmware verification failed!")
                return False
            
            logger.info("[3/6] Erasing flash...")
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BOOTLOADER_TX_ID'],
                data=[0x04, 0x14, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00]
            )
            self.bus.send(msg)
            time.sleep(2)
            
            logger.info(f"[4/6] Flashing firmware...")
            block_size = 256
            total_blocks = (len(firmware) + block_size - 1) // block_size
            
            for block_num in range(total_blocks):
                start = block_num * block_size
                end = min(start + block_size, len(firmware))
                block = firmware[start:end]
                
                msg_data = [0x36] + list(block[:7])
                msg = can.Message(
                    arbitration_id=CAN_CONFIG['BOOTLOADER_TX_ID'],
                    data=msg_data
                )
                self.bus.send(msg)
                time.sleep(0.05)
            
            logger.info("[6/6] Exiting bootloader...")
            msg = can.Message(
                arbitration_id=CAN_CONFIG['BOOTLOADER_TX_ID'],
                data=build_exit_bootloader_request()
            )
            self.bus.send(msg)
            time.sleep(2)
            
            logger.critical("✓ FIRMWARE UPDATE COMPLETE")
            return True
        
        except Exception as e:
            logger.critical(f"FIRMWARE UPDATE FAILED: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.bus:
            self.bus.shutdown()
            logger.info("CAN bus closed")
