import tarfile as tf
from sys import getsizeof
import os.path
import os
from math import ceil


def pack(filename, files):
    """
    Pack various files into a single tar archive
    :param filename: Name of the file to create
    :param files: Files to pack into archive
    """
    with tf.open(filename, "a") as tar:
        for file in files:
            tar.add(os.path.basename(file))
        tar.close()


def unpack(filename, destination):
    """
    Extract files of archive to a specific location
    :param filename: Name of the file to unpack
    :param destination: Target destination
    """
    with tf.open(filename, "r") as tar:
        tar.extractall(destination)
        tar.close()


def test(filename):
    """
    Test archive for consistency of containing files
    :param filename: Name of the archive to be tested
    :return: True if everything is ok
    """
    t = tf.open(filename, "r:")
    members = t.getmembers()
    tarsize = os.stat(filename).st_size
    filesize = 0
    for member in members:
        if member.type == b"5":
            filesize += 1024
        filesize += 512 * ceil(member.size / 512)
    filesize += len(members) * 512
    if filesize == tarsize:
        return True
    else:
        return False


def test2(filename, BLOCK_SIZE=1024):
    """
    Another way to test archive for errors (Not well tested)
    :param filename: File to be tested
    :param BLOCK_SIZE: Size of testing blocks
    :return: True if everything is OK
    """
    ok = True

    try:
        tar = tf.open(filename)
    except Exception as e:
        print(
            "There was an error opening tarfile. "
            "The file might be corrupt or missing."
        )
        ok = False

    try:
        members = tar.getmembers()
    except Exception as e:
        print("There was an error reading tarfile members.")
        ok = False

    for member_info in members:
        try:
            check = tar.extractfile(member_info.name)
            while not member_info.isdir():
                data = check.read(BLOCK_SIZE)
                if not data:
                    break
        except Exception as e:
            print("File: %r is corrupt." % member_info.name)
            ok = False
    tar.close()
    if ok:
        return True
    else:
        return False
