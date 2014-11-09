
import logging
import os


class Logger(object):

    log_file = None  # must be overriden by subclass
    ref_class = None  # must be overriden by subclass
    cli = None
    LOG_FMT = ('%(asctime)s.%(msecs)d|%(process)d|%(thread)d|<%(name)s>'
               '|%(levelname)s|%(message)s')
    DATE_FMT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, log_level=None, cli=None):
        self.log_level = log_level
        self.cli = cli
        self.verify_logfile()
        if self.log_level is None:  self.log_level = logging.DEBUG
        if self.cli is None:  self.cli = True
        self.log = logging.getLogger(self.ref_class)
        self.log.setLevel(self.log_level)
        if len(self.log.handlers) == 0:  # make sure we don't dup handlers
            self.setup_logfile()
            if self.cli:  self.setup_cli()

    def setup_cli(self):
        cli = logging.StreamHandler()
        cli.setFormatter(self.ColoredFormatter(self.LOG_FMT, datefmt=self.DATE_FMT))
        self.log.addHandler(cli)

    def setup_logfile(self):
        f = logging.FileHandler(self.log_file)
        # want plain text in log files, so no colors here
        f.setFormatter(logging.Formatter(self.LOG_FMT, datefmt=self.DATE_FMT))
        self.log.addHandler(f)

    def verify_logfile(self):
        if os.path.isfile(self.log_file):  return
        f = open(self.log_file, 'w')
        f.write("")
        f.close()

    class ColoredFormatter(logging.Formatter):
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)        
        COLORS = {
            'INFO': GREEN,
            'DEBUG': BLUE,
            'WARNING': YELLOW,
            'CRITICAL': YELLOW,
            'ERROR': RED
        }
        # colored sequences in bash
        RESET_SEQ = '\033[0m'
        COLOR_SEQ = '\033[1;%dm'
        BOLD_SEQ = '\033[1m'

        def __init__(self, fmt, datefmt=None):
            process_str = '%(process)d'
            thread_str = '%(thread)d'
            fmt = fmt.replace(process_str, self._colorize(self.CYAN,
                                                          process_str))
            fmt = fmt.replace(thread_str, self._colorize(self.CYAN,
                                                         thread_str))
            logging.Formatter.__init__(self, fmt, datefmt=datefmt)

        def format(self, record):
            lvlname = record.levelname
            if lvlname in self.COLORS:
                lvlname_color = self._colorize(self.COLORS[lvlname], lvlname)
                record.levelname = lvlname_color
            return logging.Formatter.format(self, record)
        
        def _colorize(self, color, text):
            return self.COLOR_SEQ % (30 + color) + text + self.RESET_SEQ