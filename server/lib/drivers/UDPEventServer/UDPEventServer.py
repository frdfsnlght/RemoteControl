
import socketserver, threading, json
from hub import BaseDevice

        
class Device(BaseDevice):

    def configure(self, **config):
        self.port = config.get('port', 1968)
        self.address = config.get('address', '127.0.0.1')
        self.apiKey = config.get('apiKey')
        self.server = None
        
    def start(self):
        if self.server is not None: return
        super().start()
        myself = self
        
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                myself._handleEvent(self.request[0].strip(), self.client_address[0])

        self.server = socketserver.UDPServer((self.address, self.port), Handler)
        thread = threading.Thread(target = self.__serve, name = 'udpEventServer.' + self.id, daemon = True)
        thread.start()
        
    def stop(self):
        if self.server is None: return
        super().stop();
        self.server.shutdown()
        self.server = None
                
    def __serve(self):
        self.logger.info('Server started')
        self.server.serve_forever()
        self.logger.info('Server stopped')
        self.server = None
        
    def _handleEvent(self, event, address):
        event = json.loads(event.decode('utf-8'))
        if not isinstance(event, dict):
            self.logger.error('Invalid event from {}'.format(address))
            return
            
        if self.apiKey is not None:
            if 'apiKey' not in event:
                self.logger.error('Missing apiKey from {}'.format(address))
                return
            if self.apiKey != event.get('apiKey'):
                self.logger.error('Invalid apiKey from {}'.format(address))
            
        if 'type' not in event:
            self.logger.error('Missing event type from {}: {}'.format(address, event))
            return
        type = event['type']
        if type == 'generic':
            id = event.get('id')
            if not id:
                self.logger.error('Missing id from {}: {}'.format(address, event))
                return
            self.emitGenericEvent(id = id, payload = event.get('payload', {}))
        elif type == 'button':
            button = event.get('button')
            state = event.get('state')
            if not button or not state:
                self.logger.error('Invalid button event from {}: {}'.format(address, event))
                return
            self.emitButtonEvent(button = button, state = state)
        else:
            self.logger.error('Invalid event type from {}: {}'.format(address, event))
        