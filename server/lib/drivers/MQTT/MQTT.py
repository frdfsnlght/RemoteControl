
import time
import paho.mqtt.client as mqtt

from hub import BaseDevice, DeviceException, Timer
   
class Device(BaseDevice):

    def configure(self, **config):
        super().configure(**config)
        self.address = config.get('address')
        if self.address is None:
            raise DeviceException('Address is required!')
        self.port = config.get('port', 1883)
        self.username = config.get('username')
        self.password = config.get('password')
        self.publishTopic = config.get('publishTopic')
        self.subscribeTopic = config.get('subscribeTopic')
        self.apiKey = config.get('apiKey')
        if not self.publishTopic and not self.subscribeTopic:
            raise DeviceException('At least one of publishTopic or subscribeTopic is required!')
        self.__reset()

    def start(self):
        if self.connected: return
        super().start()

        self.client = mqtt.Client()
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_publish = self.__on_publish
        self.client.on_subscribe = self.__on_subscribe
        if self.username is not None:
            self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.address, self.port)
        self.logger.info('Connecting...')
        self.client.loop_start()
       
    def stop(self):
        if self.client is None:
            return
        self.client.disconnect()
        self.client.loop_stop()
        self.client = None
        self.__reset()

    def __reset(self):
        self.connected = False
        self.client = None

    def __on_connect(self, client, userdata, flags, rc):
        self.connected = True
        self.logger.info('Connected to MQTT broker at {}:{}'.format(self.address, self.port))
        if self.subscribeTopic:
            (result, mid) = self.client.subscribe(self.subscribeTopic, 0)
            self.subscribeMid = mid
            self.client.message_callback_add(self.subscribeTopic, self.__on_message)
        
    def __on_publish(self, client, userdata, mid):
        pass
        
    def __on_subscribe(self, client, userdata, mid, grantedQOS):
        if mid == self.subscribeMid:
            self.logger.info('Subscribed to MQTT topic {}'.format(self.subscribeTopic))
    
    # Handles incoming messages exactly like the UDPEventServer does
    def __on_message(self, client, userdata, message):
        event = json.loads(message.payload.decode('utf-8'))
        if not isinstance(event, dict):
            self.logger.error('Invalid event from MQTT topic {}'.format(self.subscribeTopic))
            return
            
        if self.apiKey is not None:
            if 'apiKey' not in event:
                self.logger.error('Missing apiKey from MQTT topic {}'.format(self.subscribeTopic))
                return
            if self.apiKey != event.get('apiKey'):
                self.logger.error('Invalid apiKey from MQTT topic {}'.format(self.subscribeTopic))
                return
                
        if 'type' not in event:
            self.logger.error('Missing event type from MQTT topic {}: {}'.format(self.subscribeTopic, event))
            return
        type = event['type']
        if type == 'generic':
            id = event.get('id')
            if not id:
                self.logger.error('Missing id from MQTT topic {}: {}'.format(self.subscribeTopic, event))
                return
            self.emitGenericEvent(id = id, **event.get('args', {}))
        elif type == 'button':
            button = event.get('button')
            state = event.get('state')
            if not button or not state:
                self.logger.error('Invalid button event from MQTT topic {}: {}'.format(self.subscribeTopic, event))
                return
            self.emitButtonEvent(button = button, state = state)
        else:
            self.logger.error('Invalid event type from MQTT topic {}: {}'.format(self.subscribeTopic, event))
    
    def __on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.logger.info('Disconnected from MQTT broker at {}:{} with result code {}'.format(self.address, self.port, rc))

    #--------------------------------------------------------------------------
    # Public API
    #

    def publish(self, message, topic = None, qos = 0):
        #if not self.connected: return
        if not topic:
            topic = self.publishTopic
        if not topic:
            self.logger.error('Unable to publish: missing topic')
            return
        self.client.publish(topic, payload = message, qos = qos)
