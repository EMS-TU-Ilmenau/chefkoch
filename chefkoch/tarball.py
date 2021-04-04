import tarfile as tf
from sys import getsizeof
import os
from math import ceil


class Tarball:
    """
    represents a tarball

    WIP
    Momentan wird nur die init-Funktion verwendet
    """

    def __init__(self, filename, listing):
        """
        creates a tar-file and packs all given files from directory
        into it

        Parameters
        ----------
        filename(str):
            name of future tar-archive

        listing(list):
            lists all files from directory
        """

        with tf.open(filename + ".tar", "w") as tar:
            print(listing)
            for entry in listing:
                # may need to change it up, if there is a more
                # complex folder structure
                tar.addfile(
                    tf.TarInfo(os.path.basename(entry)),
                    open(os.path.abspath(entry)),
                )
        tar.close()

    def pack(self, filename, files):
        """
        Pack various files into a single tar archive
        now use init...

        Parameters
        ----------
        filename(str):
            Name of the file to create
        files(filename):
            Files to pack into archive
        """
        with tf.open(filename, "w") as tar:
            for file in files:
                print(file)
                path = os.path.basename(file)
                print(path)
                tar.add(path)
            tar.close()

    def unpack(self, filename, destination):
        """
        Extract files of archive to a specific location

        Parameters
        ----------
        filename(str):
            Name of the file to unpack
        destination(str):
            Target destination
        """
        with tf.open(filename, "r") as tar:
            tar.extractall(destination)
            tar.close()

    def test(self, filename):
        """
        Test archive for consistency of containing files

        Parameters
        ----------
        filename(str):
            Name of the archive to be tested

        Returns
        -------
        True, if everything is ok
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

    def test2(self, filename, BLOCK_SIZE=1024):
        """
        Another way to test archive for errors (Not well tested)

        Parameters
        ----------
        filename(str):
            File to be tested
        BLOCK_SIZE(int):
            Size of testing blocks

        Returns
        -------
        True, if everything is OK
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
