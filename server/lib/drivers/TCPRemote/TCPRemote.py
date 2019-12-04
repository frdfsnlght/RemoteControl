
import threading, struct, socket, json

from hub import BaseDevice, DeviceException


numLEDs = 5

COLORS = {
    'red': [255, 0, 0],
    'orange': [255, 128, 0],
    'yellow': [255, 255, 0],
    'lime': [128, 255, 0],
    'green': [0, 255, 0],
    'bluegreen': [0, 255, 128],
    'cyan': [0, 255, 255],
    'lightblue': [0, 128, 255],
    'blue': [0, 0, 255],
    'purple': [128, 0, 255],
    'magenta': [255, 0, 255],
    'fuschia': [255, 0, 128],
    'black': [0, 0, 0],
    'white': [255, 255, 255],
    'white50': [128, 128, 128],
}


class TCPRemoteClient():

    def __init__(self, device, sock, address):
        self.device = device
        self.address = address[0]
        self.port = address[1]
        self.socket = sock
        self.infile = sock.makefile(mode = 'r', buffering = 1, encoding = 'utf-8-sig')
        self.outfile = sock.makefile(mode = 'w', buffering = 1, encoding = 'utf-8', newline = '\r\n')
        self.name = None
        self.authorized = False
        
    def run(self):
        self.device._addClient(self)
        while True:
            line = self.infile.readline()
            if line:
                try:
                    print(line)
                    data = json.loads(line[:-1])
                    if not isinstance(data, dict):
                        self.logger.error('Client {} data is not a dict'.format(self))
                        if self.authorized:
                            self.sendError('bad request', 400)
                        else:
                            break
                    elif not self.device._process(self, data):
                        break
                except json.decoder.JSONDecodeError as e:
                    print(e);
                    self.device.logger.error('Invalid JSON received from {}:{}: {}'.format(self.address, self.port, line[:-1]))
                    if self.authorized:
                        self.sendError('bad request', 400)
                    else:
                        break
            else:
                break
        self.stop()
        self.device._removeClient(self)
        
    def stop(self):
        self.infile.close()
        self.outfile.close()
        self.socket.close()
        
    def send(self, data):
        line = json.dumps(data)
        self.outfile.write(line)
        self.outfile.write('\n')
        self.outfile.flush()
    
    def sendError(self, msg, status):
        self.send({'error': msg, 'status': status})
        
    def __str__(self):
        if self.name is None:
            return '{}:{}'.format(self.address, self.port)
        else:
            return '{}[{}:{}]'.format(self.name, self.address, self.port)
        

class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address', 'localhost')
        if self.address == '*':
            self.address = ''
        self.port = config.get('port', 1970)
        self.apiKey = config.get('apiKey')
        self.buttonMap = config.get('buttonMap', {})
        self.__reset()
        self.ledColors = [0] * (numLEDs * 3)
            
    def start(self):
        if self.__run: return
        super().start()
        self.__run = True
        thread = threading.Thread(target = self.__loop, name = 'TCPRemote.' + self.id, daemon = True)
        thread.start()

    def stop(self):
        if not self.__run: return
        super().stop();
        self.__run = False
        self.__socket.close()
        for client in self.__clients:
            client.stop()
        self.__reset()
        
    def __reset(self):
        self.__run = False
        self.__socket = None
        self.__clients = []
        
    def __loop(self):
        self.__socket = socket.socket()
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind((self.address, self.port))
        self.__socket.listen(0)
        self.logger.info('Listening on {}:{}'.format(self.address if self.address else '*', self.port))
        
        while self.__run:
            (conn, clientAddress) = self.__socket.accept()
            client = TCPRemoteClient(self, conn, clientAddress)
            self.logger.info('Connected to {}'.format(client))
            client.run()
            self.logger.info('Disconnected from {}'.format(client))
            self.emitGenericEvent(id = 'TCPRemoteDisconnected')
            
        self.__socket.close()

    def __setLEDColors(self, *colors):
        if not self.__run: return
        data = {'action': 'setLEDs', 'colors': colors}
        for client in self.__clients:
            client.send(data)

    def _addClient(self, client):
        self.__clients.append(client)
        
    def _removeClient(self, client):
        self.__clients.remove(client)
        
    def _process(self, client, data):
        if not client.authorized:
            if 'hello' not in data:
                self.logger.error('Client {} did not say hello'.format(client))
                client.sendError('unauthorized', 401)
                return False
            client.name = str(data['hello'])
            if self.apiKey is not None:
                if 'apiKey' not in data:
                    self.logger.error('Client {} did not provide apiKey'.format(client))
                    client.sendError('unauthorized', 401)
                    return False
                if data['apiKey'] != self.apiKey:
                    self.logger.error('Client {} provided invalid apiKey: {}'.format(client, data['apiKey']))
                    client.sendError('unauthorized', 401)
                    return False
                self.logger.info('Client {} authorized'.format(client))
            client.authorized = True
            self.__setLEDColors(*self.ledColors)
            self.emitGenericEvent(id = 'TCPRemoteConnected')
            self.logger.info('Client {} ready'.format(client))
            return True
            
        if 'goodbye' in data:
            return False
            
        if 'button' in data:
            return self.__processButton(client, data)

        self.logger.error('Unknown message from {}: {}'.format(client, data))
        client.sendError('bad request', 400)
        return True
        
    def __processButton(self, client, data):
        button = data.get('button')
        state = data.get('state')
        if state is None:
            self.logger.error('Button message is missing state from {}'.format(client))
            client.sendError('bad request', 400)
            return True
        if button in self.buttonMap:
            button = self.buttonMap[button]
        self.emitButtonEvent(button, state)
        return True
    
    #--------------------------------------------------------------------------
    # Public API
    #
        
    def setLEDColors(self, *colors):
        while len(colors) < numLEDs:
            colors.append(None)
        cols = []
        for color in colors:
            if color is None:
                color = [0, 0, 0]
            elif isinstance(color, list):
                color = color[:3]
                while len(color) < 3:
                    color.append(color[-1])
            elif isinstance(color, str):
                if color not in COLORS:
                    self.logger.error('LED color "{}" is unknown'.format(color))
                    color = [0, 0, 0]
                else:
                    color = COLORS[color]
            else:
                self.logger.error('LED color "{}" is unknown'.format(color))
                color = [0, 0, 0]
            cols.extend(color)

        self.ledColors = cols
        self.__setLEDColors(*cols)
