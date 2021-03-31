import logging

# this is all the default logger named root
"""
# this function can be called only once, that's gonna be a problem
# logging.basicConfig(filename='snippets/logtest.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
name = 'James'
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info('Admin logged in')
logging.warning('Admin logged out')
logging.error(f'{name} destroyed this equipment')


a = 0
b = 0
try:
    c = a/b
except Exception as e:
    # logging.error("Exception occurred", exc_info=True)
    # does the same thing, like th one above
    logging.exception("Exception occured")


logging.debug('this is a debug message')
logging.info('this is an info message')
logging.warning('this is a warning message')
logging.error('this is an error message')
logging.critical('this is a critical message')
"""

