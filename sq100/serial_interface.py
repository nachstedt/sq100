from gh600_serial_exception import GH600SerialException

import serial
import time


class SerialInterface():
    _sleep = 2
    
    def _connectSerial(self):
        """connect via serial interface"""
        try:
            self.serial = serial.Serial(port=self.config.get("serial", "comport"), 
                                        baudrate=self.config.get("serial", "baudrate"),
                                        timeout=self.config.getint("serial", "timeout"))
            self.logger.debug("serial connection on " + self.serial.portstr)
        except serial.SerialException:
            self.logger.critical("error establishing serial connection")
            raise GH600SerialException
    
    def _disconnectSerial(self):
        """disconnect the serial connection"""
        self.serial.close()
        self.logger.debug("serial connection closed")
        time.sleep(self._sleep)
    
    def _writeSerial(self, command, *args, **kwargs):
        #try:
            if command in self.COMMANDS:
                hex = self.COMMANDS[command] % kwargs
            else:
                hex = command
            
            self.logger.debug("writing to serialport: %s" % hex)
            self.serial.write(bytearray.fromhex(hex))
            #self.serial.sendBreak(2)
            time.sleep(self._sleep)
            self.logger.debug("waiting at serialport: %i" % self.serial.inWaiting())
        #except:
        #    raise GH600SerialException
    
    def _readSerial(self, size = 2070):
        data = self.serial.read(size)
        print(data)
        self.logger.debug("serial port returned: %s" % data if len(data) < 30 else "%s... (truncated)" % data[:30])
        return data
    
    def _querySerial(self, command, *args, **kwargs):
        tries = 0
        while True:
            tries += 1
            self._writeSerial(command, *args, **kwargs)
            data = self._readSerial()
            if data:
                return data
            else:
                if tries < 2:
                    self.logger.debug("no data at serial port, retry command #%i" % tries)
                    time.sleep(self._sleep)
                    continue
                else:
                    raise GH600SerialException
        
    def _diagnostic(self):
        """check if a connection can be established"""
        try:
            self._connectSerial()
            self._querySerial('whoAmI')
            self._disconnectSerial()
            self.logger.info("serial connection established successfully")
            return True
        except GH600SerialException:
            self.logger.info("error establishing serial port connection, please check your config.ini file")
            return False
