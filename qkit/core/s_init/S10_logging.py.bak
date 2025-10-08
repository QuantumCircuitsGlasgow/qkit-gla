import qkit
import os,sys
import logging
from time import strftime

class CustomFormatter(logging.Formatter):
    purple = "\x1b[35;1m"
    blue = "\x1b[34;1m"
    yellow = "\x1b[43;34;1m"
    red = "\x1b[31;1m"
    bold_red = "\x1b[31;43;1m"
    reset = "\x1b[0m"
    
    format = '%(asctime)s [ %(levelname)-4s ]|: %(message)s <%(filename)s :%(funcName)s:%(lineno)d>'

    FORMATS = {
        logging.DEBUG: purple + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt,datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def cleanup_logfiles():
    '''
    if qkit.cfg['maintain_logiles'] is not False, this script checks the log folder and removes all log files except for the latest 10.
    :return:
    '''
    if qkit.cfg.get('maintain_logfiles',True):
        ld = [filename for filename in os.listdir(qkit.cfg['logdir']) if filename.startswith('qkit') and filename.endswith('.log')]
        ld.sort()
        for f in ld[:-10]:
            try:
                os.remove(os.path.join(qkit.cfg['logdir'], f))
            except:
                pass


def _setup_logging():

    level=getattr(logging, qkit.cfg.get('debug', 'WARNING'))

    fileLogLevel = getattr(logging, qkit.cfg.get('file_log_level', 'WARNING'))# repeat
    stdoutLogLevel = getattr(logging, qkit.cfg.get('stdout_log_level', 'WARNING')) #
    
    rootLogger = logging.getLogger()
    
    fileLogger = logging.FileHandler(filename=os.path.join(qkit.cfg['logdir'], strftime('qkit_%Y%m%d_%H%M%S.log')), mode='a+')
    fileLogger.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)-4s: %(message)s <%(pathname)s -> %(module)s->%(funcName)s:%(lineno)d>',
                              datefmt='%Y-%m-%d %H:%M:%S'))
    fileLogger.setLevel(min(level, fileLogLevel))

    jupyterLogger = logging.StreamHandler(sys.stdout)
    jupyterLogger.setFormatter(CustomFormatter())
    jupyterLogger.setLevel(level) # thows to the jupyter output
    
    rootLogger.addHandler(fileLogger)
    rootLogger.addHandler(jupyterLogger)
    rootLogger.setLevel(min(level, fileLogLevel))
    
    logging.info(' ---------- LOGGING STARTED ---------- ')
    
    logging.debug('Set logging level for file to: %s ' % fileLogLevel)
    logging.debug('Set logging level for stdout to: %s ' % stdoutLogLevel)
    
    cleanup_logfiles()



#NOT USED
def set_debug(enable):
    logger = logging.getLogger()
    if enable:
        logger.setLevel(logging.DEBUG)
        logging.info('Set logging level to DEBUG')
    else:
        logger.setLevel(logging.INFO)
        logging.info('Set logging level to INFO')


_setup_logging()
