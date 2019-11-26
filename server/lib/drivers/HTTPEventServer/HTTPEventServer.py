
import os, threading, flask, logging

from hub import BaseDevice

        
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.port = config.get('port', 1969)
        self.address = config.get('address', '127.0.0.1')
        self.apiKey = config.get('apiKey')
        self.route = config.get('route', '/event')
        self.methods = config.get('methods', ['POST'])
        self.accessLog = config.get('accessLog', False)
        self.server = None
        
    def start(self):
        if self.server is not None: return
        super().start()
        
        if not self.accessLog:
            logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        self.server = flask.Flask(__name__)
        thread = threading.Thread(target = self.__serve, name = 'httpEventServer.' + self.id, daemon = True)
        thread.start()
        
    def stop(self):
        if self.server is None: return
        super().stop();
        self.server = None
                
    def __serve(self):
        self.logger.info('Server started')
        self.server.add_url_rule(
            rule = self.route,
            endpoint = 'handleEvent',
            view_func = self.__handleEvent,
            methods = self.methods)
        os.environ['FLASK_ENV'] = 'development'
        self.server.run(
            host = self.address,
            port = self.port,
            debug = False,
            use_reloader = False,
            use_debugger = False)

        self.logger.info('Server stopped')
        self.server = None

    def __handleEvent(self):
        event = flask.request.get_json(force = True, silent = True)
        if not isinstance(event, dict):
            self.logger.error('Invalid event from {}'.format(flask.request.remote_addr))
            return self.__error('Invalid event', 400)
            
        if self.apiKey is not None:
            if 'apiKey' not in event:
                self.logger.error('Missing apiKey from {}'.format(flask.request.remote_addr))
                return self.__error('Missing apiKey', 401)
            if self.apiKey != event.get('apiKey'):
                self.logger.error('Invalid apiKey from {}'.format(flask.request.remote_addr))
                return self.__error('Invalid apiKey', 401)
            
        if 'type' not in event:
            self.logger.error('Missing event type from {}: {}'.format(flask.request.remote_addr, event))
            return self.__error('Missing event type', 400)
        type = event['type']
        if type == 'generic':
            id = event.get('id')
            if not id:
                self.logger.error('Missing id from {}: {}'.format(flask.request.remote_addr, event))
                return self.__error('Missing id', 400)
            self.emitGenericEvent(id = id, payload = event.get('payload', {}))
            return self.__ok()
        elif type == 'button':
            button = event.get('button')
            state = event.get('state')
            if not button or not state:
                self.logger.error('Invalid button event from {}: {}'.format(flask.request.remote_addr, event))
                return self.__error('Invalid button event', 400)
            self.emitButtonEvent(button = button, state = state)
            return self.__ok()
        else:
            self.logger.error('Invalid event type from {}: {}'.format(flask.request.remote_addr, event))
            return self.__error('Invalid event type', 400)
        
    def __error(self, msg, status):
        return ({'success': False, 'error': msg}, status)
        
    def __ok(self):
        return ({'success': True}, 200)
    