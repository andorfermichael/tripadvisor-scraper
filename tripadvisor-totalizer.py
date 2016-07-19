import argparse
import logging
import time
import shutil
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

def copy_review_files(source_directory, destination_directory):
    src_files = os.listdir(source_directory)

    for file_name in src_files:
        full_file_name = os.path.join(source_directory, file_name)
        if (os.path.isfile(full_file_name)):
            shutil.copy(full_file_name, destination_directory)

def copy_hotel_information(source_directory, destination_directory):
    src_files = os.listdir(source_directory)
    file_name = ''

    for src_file in src_files:
        if 'information' in src_file:
            file_name = src_file
            break

    full_file_name = os.path.join(source_directory, file_name)
    if (os.path.isfile(full_file_name)):
        shutil.copy(full_file_name, destination_directory)

def copy_review_csv_information(source_directory, destination_directory):

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

    for sub_directory_path in sub_directory_paths:
        sub_directory_name = os.path.basename(os.path.normpath(sub_directory_path))

        if sub_directory_name == '1-star':
            copy_review_files(sub_directory_path, star_directories[0])
        elif sub_directory_name == '2-star':
            copy_review_files(sub_directory_path, star_directories[1])
        elif sub_directory_name == '3-star':
            copy_review_files(sub_directory_path, star_directories[2])
        elif sub_directory_name == '4-star':
            copy_review_files(sub_directory_path, star_directories[3])
        elif sub_directory_name == '5-star':
            copy_review_files(sub_directory_path, star_directories[4])
        else:
            copy_hotel_information(sub_directory_path, target_directory)




