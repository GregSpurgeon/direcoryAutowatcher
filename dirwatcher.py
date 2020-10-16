#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = """Greg Spurgeon with help from Pete Mayor and
                other students in dirwatcher group"""

import sys
import logging
import os
import signal
import time
import argparse
import datetime

exit_flag = False
watch_dict = {}

format1 = '%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(format=format1,
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def search_for_magic(filename, start_line, magic_string):
    with open(filename) as f:
        """Function reads a file and finds if a predefined string is in that
        file and what line number it appears on"""
        file_lines = f.readlines()
        found_lines = []
        for line_num, line in enumerate(file_lines):
            if line_num < start_line:
                continue

            watch_dict[filename] = line_num + 1
            result = line.find(magic_string)

            if result != -1:
                found_lines.append(line_num + 1)
        if len(found_lines) > 0:
            logger.info(f"New magic string found in {filename} on line \
                        {found_lines}")

    return


def watch_directory(path, magic_string, extension, interval):
    """function that watches a certain folder to see if any changes happen
    to any text files within that folder"""
    file_list = os.listdir(path)
    for k in list(watch_dict):
        if k.split("/")[1] not in file_list:
            logger.info(f"File Deleted {k}")
            watch_dict.pop(k)
    for _file in file_list:
        path_file = path + "/" + _file

        if path_file not in watch_dict and path_file.endswith(extension):
            logger.info(f"New File Added {path_file} ")
            watch_dict[path_file] = 0
        if path_file.endswith(extension):
            search_for_magic(path_file, watch_dict[path_file], magic_string)

    return


def create_parser():
    """Function that sets up argument flags to be passed in the CMD line"""
    parser = argparse.ArgumentParser(description='watch for file changes')
    parser.add_argument('-d', '--dir', help="dir to watch")
    parser.add_argument('-e', '--ext', default='.txt',
                        help='filters what kind of file extension \
                        to search within')
    parser.add_argument('-i', '--int', default=1, type=int,
                        help='controls polling interval for checking dict')
    parser.add_argument('-t', '--text', help='magic text string to look at')

    return parser


def signal_handler(sig_num, frame):
    """function that recives signals from outside the program and
    returns the proper output"""
    logger.warning('Received ' + signal.Signals(sig_num).name)
    if signal.Signals(sig_num).name == "SIGINT":
        logger.info('Terminating Dirwatcher, keyboard interupt recieved')
    if signal.Signals(sig_num).name == "SIGTERM":
        logger.info('Terminating Dirwatcher, OS interupt recieved')
    global exit_flag
    exit_flag = True
    return


def main(args):
    """function that continuesly runs the program waiting for signals
    from the CMD line. Also alerts user when the program is started and
    when the program was eneded"""
    ns = create_parser().parse_args()
    start_time = time.time()

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    logging.info("""
        -------------------------------------------------------------------\n
                            Started dirwatcher.py
                                    Hello
        -------------------------------------------------------------------\n
    """)
    while not exit_flag:
        try:
            # call my directory watching function
            watch_directory(ns.dir, ns.text, ns.ext, ns.int)
            pass
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            logger.error(e)
            pass

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(ns.int)

    finish_time = time.time()
    elapse_time = finish_time - start_time
    up_time = str(datetime.timedelta(seconds=elapse_time))
    logging.info(f"""
        -------------------------------------------------------------------\n
                            Stopped dirwatcher.py
                            program uptime {up_time}
                                    GOODBYE
        -------------------------------------------------------------------\n
    """)
    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start
    return


if __name__ == '__main__':
    main(sys.argv[1:])
