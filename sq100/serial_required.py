from gh600_serial_exception import GH600SerialException


def serial_required(function):
    def serial_required_wrapper(x, *args, **kw):
        try:
            x._connectSerial()
            return function(x, *args, **kw)
        except GH600SerialException as e:
            raise
        finally:
            x._disconnectSerial()
    return serial_required_wrapper
