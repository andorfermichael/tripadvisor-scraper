import argparse
import logging
import time
import os

def get_subdirectories(rootdir):
    return [x[0] for x in os.walk(rootdir)]

# Creates a directory for a session
def create_session_directory(directory_name):
    # Build directory name
    directory_path = os.getcwd() + '/totalized/' + directory_name

    logger.info('STARTED: Creation of directory ' + os.getcwd() + '/totalized/' + directory_name)

    # Create the folder
    os.makedirs(directory_path)

    logger.info('FINISHED: Creation of directory ' + os.getcwd() + '/totalized/' + directory_name)

    return directory_path

# Creates a directory for each rating category (e.g. 5 stars, 4 stars)
def create_rating_directories(path):
    stars = [1, 2, 3, 4, 5]

    paths = list()

    for star in stars:
        # Build directory name
        directory_path = path + '/' + str(star) + '-star'

        logger.info('STARTED: Creation of directory ' + directory_path)

        # Create the folder
        os.makedirs(directory_path)

        logger.info('FINISHED: Creation of directory ' + directory_path)

        paths.append(directory_path)

    return paths

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

    source_path = args.path
    source_folder = os.path.basename(os.path.normpath(source_path))

    target_directory = create_session_directory(source_folder)
    star_directories = create_rating_directories(target_directory)

    sub_directory_paths = get_subdirectories(source_path)



