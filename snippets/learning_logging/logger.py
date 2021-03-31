import logging
import logging.config
import yaml

# logging mit config-file
# logging.config.fileConfig(fname='./snippets/learning_logging/file.conf', disable_existing_loggers=False)

# logging mit yaml
with open('./snippets/learning_logging/config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

# Get the logger specified in the file
logger = logging.getLogger(__name__)

logger.debug('this is a debug message')