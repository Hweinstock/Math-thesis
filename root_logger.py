import logging

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class RootLogger:
    LEVEL = logging.ERROR

    def log_info(msg):
        logging.info(f'{bcolors.OKBLUE}{msg}{bcolors.ENDC}')
    
    def log_warning(msg):
        logging.warning(f'{bcolors.WARNING}{msg}{bcolors.ENDC}')
    
    def log_debug(msg):
        logging.debug(f'{bcolors.OKGREEN}{msg}{bcolors.ENDC}')