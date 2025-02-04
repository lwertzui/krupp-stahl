#!/usr/bin/env python3

#python script to read contents of a blaustahl storage device and extract passwords stored on it

import serial
import logging
import glob

class BlaustahlSRWP:
    logger = logging.getLogger(__name__)

    def __init__(self, device:str|None='/dev/ttyACM0', fram_size:int=8192):
        self.fram_size = fram_size

        if device is None:
            device = self.find_device()

        self.connect_over_serial(device)

    def connect_over_serial(self, device:str|None='/dev/ttyACM0'):
        self.srwp = serial.Serial(device, 115200, timeout=1, rtscts=False, dsrdtr=False)

    @staticmethod
    def find_device():
        """
        Finds the first available /dev/ttyACM device.
        :return: The path to the device as a string.
        :raises FileNotFoundError: If no device is found.
        """
        devices = glob.glob('/dev/ttyACM*')
        if not devices:
            raise FileNotFoundError("No /dev/ttyACM device found.")
        return devices[0]

    def flush(self):
        while self.srwp.in_waiting:
            data = self.srwp.read(4096)
            self.logger.debug(f"Flushed Data: {data}")

    def echo(self, msg):
        self.flush()

        ba = bytearray()
        ml = len(msg)

        ba.extend(b'\x00')    # Enter SRWP mode
        ba.extend(b'\x00')    # Command: Echo
        ba.extend(ml.to_bytes(4, byteorder='little'))
        ba.extend(msg.encode(encoding="ascii"))

        self.srwp.write(ba)
        self.srwp.flush()

        data = self.srwp.read(ml)
        print(data)

    def read_fram(self, addr:int, size:int):
        """
        Reads the first 7600 bytes from the FRAM chip.
        """
        self.flush()

        ba = bytearray()
        ba.extend(b'\x00')    # Enter SRWP mode
        ba.extend(b'\x01')    # Command: Read FRAM
        ba.extend(addr.to_bytes(4, byteorder='little'))    # 4-byte address
        ba.extend(size.to_bytes(4, byteorder='little'))    # 4-byte size

        self.srwp.write(ba)
        self.srwp.flush()

        data = self.srwp.read(size)
        return data

    def read_fram_retry(self, addr:int, size:int, max_retries:int=3):
        """
        Reads `size` bytes from address `addr` on the FRAM chip with retries.
        :param addr: Starting address
        :param size: Total number of bytes to read
        :param max_retries: Maximum number of retries for incomplete reads
        :return: All data as bytes
        """
        for attempt in range(max_retries):
            data = self.read_fram(addr, size)
            if len(data) == size:
                return data  # Successful read
            self.logger.warning(f"Incomplete read: Expected {size}, got {len(data)}. Retrying... (Attempt {attempt + 1})")
        raise IOError(f"Failed to read {size} bytes from FRAM after {max_retries} attempts")

    def read_fram_all(self, chunk_size:int=100):
        """
        Reads the entire content of the FRAM chip with retries.
        :return: All data on the FRAM chip as bytes.
        """
        data = bytearray()
        for offset in range(0, self.fram_size, chunk_size):
            chunk = self.read_fram_retry(offset, min(chunk_size, self.fram_size - offset))
            data.extend(chunk)
        return bytes(data)

# Main program
if __name__ == "__main__":
    bs = BlaustahlSRWP()
    ascii_data = bs.read_fram(0, 7600).decode('ascii')
    print(ascii_data)


