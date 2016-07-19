import argparse
import logging


# Main
if __name__ == '__main__':
    # Setup commandline handler
    parser = argparse.ArgumentParser(description='put together all reviews of a city' , usage='python tripadvisor-totalizer C:\\Users\\Administrator\\tripadvisor-scrapper\\2016-06-01-1522-vienna')
    parser.add_argument('path', help='path of city directory with reviews')
    args = parser.parse_args()

    session_timestamp = time.strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(filename='./logs/' + session_timestamp + '-totalizer.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger().addHandler(logging.StreamHandler())





