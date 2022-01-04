

import sys, os, time
import configparser
import logging, logging.handlers, re
import yaml
import importlib

from dotmap import DotMap

from .BaseDevice import BaseDevice, DeviceException
from .Activity import Activity, ActivityException
from .Controller import Controller, ControllerException
from .ActivityButton import ActivityButton
from .ActivityEvent import ActivityEvent
from .DotDict import DotDict
from .Timer import Timer


rootDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
defaultConfigFile = os.path.join(rootDir, 'etc', 'config-default.ini')
localConfigFile = os.path.join(rootDir, 'etc', 'config.ini')


logger = logging.getLogger('hub')
config = None
quit = False
devices = DotDict()
activities = DotDict()
controllers = DotDict()
state = DotDict()


class HubException(Exception):
    pass
    
    
def start():
    loadMainConfig()
    configureLogging()
    logger.info('Starting...')
    configure()
    run()
    logger.info('Stopped')
    
    
def configure():
    try:
        loadDevicesConfig()
        loadActivitiesConfig()
        loadControllersConfig()
    except Exception as e:
        logger.exception('Configuration exception: {}'.format(e))
        sys.exit(1)
    
def run():
    for (id, device) in devices.items():
        device.start()
        
    for (id, activity) in activities.items():
        activity.initialize()
        
    for (id, controller) in controllers.items():
        controller.start()
        
    try:
        while not quit:
            time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        pass
    
    for (id, controller) in controllers.items():
        controller.stop()

    for (id, device) in devices.items():
        device.stop()
    
    
def loadMainConfig():
    global config
    config = configparser.ConfigParser(
        interpolation = None,
        converters = {
            'path': resolvePath
        }
    )
    config.optionxform = str    # preserve option case
    config.clear()
    config.read(defaultConfigFile)
    config.read(localConfigFile)

    
def loadDevicesConfig():
    file = config.getpath('configuration', 'devicesConfig')
    logger.info('Loading devices from {}...'.format(file))
    if not os.path.exists(file):
        logger.warn('Devices configuration file, {}, not found!'.format(file))
        return
    with open(file, 'r') as f:
        confs = yaml.safe_load(f)
    devices.clear()
    for (id, conf) in confs.items():
        if 'driver' not in conf:
            logger.error('Device "{}" is missing driver!'.format(id))
            continue
        driver = conf['driver']
        
        try:
            module = importlib.import_module('drivers.' + driver)
        except ImportError:
            logger.exception('Unable to load driver "{}" for device "{}":'.format(driver, id))
            continue
            
        if not hasattr(module, 'Device'):
            logger.error('Driver "{}" does not declare a Device class!'.format(driver))
            continue
            
        device = module.Device(id)
        device.configure(**conf)
        devices[id] = device
        logger.info('Created device "{}" with driver "{}"'.format(id, driver))
    logger.info('Loaded {} devices'.format(len(devices)))

    
def loadActivitiesConfig():
    file = config.getpath('configuration', 'activitiesConfig')
    logger.info('Loading activities from {}...'.format(file))
    if not os.path.exists(file):
        logger.warn('Activities configuration file, {}, not found!'.format(file))
        return
    with open(file, 'r') as f:
        confs = yaml.safe_load(f)
    activities.clear()
    for (id, conf) in confs.items():
        activity = Activity(id)
        activity.configure(**conf)
        activities[id] = activity
        logger.info('Created activity "{}"'.format(id))
    logger.info('Loaded {} activities'.format(len(activities)))
    
    
def loadControllersConfig():
    file = config.getpath('configuration', 'controllersConfig')
    logger.info('Loading controllers from {}...'.format(file))
    if not os.path.exists(file):
        logger.warn('Controllers configuration file, {}, not found!'.format(file))
        return
    with open(file, 'r') as f:
        confs = yaml.safe_load(f)
    controllers.clear()
    for (id, conf) in confs.items():
        controller = Controller(id)
        controller.configure(**conf)
        controllers[id] = controller
        logger.info('Created controller "{}"'.format(id))
    logger.info('Loaded {} controllers'.format(len(controllers)))

    
def configureLogging():
    root = logging.getLogger()
    root.setLevel(getattr(logging, config.get('logging', 'logLevel')))
    
    handler = logging.handlers.RotatingFileHandler(
        config.getpath('logging', 'logFile'),
        maxBytes = config.getint('logging', 'logSize'),
        backupCount = config.getint('logging', 'logCount'))
        
    handler.setFormatter(logging.Formatter(fmt = config.get('logging', 'logFormat')))
    root.addHandler(handler)

    if config.getboolean('logging', 'console'):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt = config.get('logging', 'logFormat')))
        root.addHandler(handler)

    levelPattern = re.compile(r"^level\.(.*)")
    for (k, v) in config.items('logging'):
        m = levelPattern.match(k)
        if m:
            logging.getLogger(m.group(1)).setLevel(getattr(logging, v))
    
def resolvePath(str):
    str = os.path.expanduser(str)
    if os.path.isabs(str):
        return str
    else:
        return os.path.normpath(os.path.join(rootDir, str))
    