"""
Definition of the different simulation steps available.
"""
import yaml
import json
import zlib
import os.path


class JSONContainer:
    """
    A Container for JSON Files
    """

    # def __init__(self):
    #     """
    #     Initializes the container
    #     """
    #     self.data = dict()
    #     self.read_only = False

    def __init__(self, filename: str = None):
        """
        Initializes the container from file if path is given,
        else create empty Container

        :param filename:
        """
        if filename is not None:
            with open(filename) as f:
                self.data = json.load(f)
                f.close()
            self.read_only = True
        else:
            self.data = dict()
            self.read_only = False

    def __getitem__(self, item):
        """
        Returns value of specific key
        """
        return self.data[item]

    def __setitem__(self, key, value):
        """
        Set value of specific key
        """
        if not self.read_only:
            self.data[key] = value

    def save(self, filename):
        """
        Save container to file
        """
        json_object = json.dumps(self.data, indent=4)

        # Writing to sample.json
        with open(filename, "w") as outfile:
            outfile.write(json_object)
            outfile.close()

    def hash(self):
        """
        compute hashname over data
        """
        json_object = json.dumps(self.data, indent=4)
        # Problem vllt wegen Kollisionen
        hashName = zlib.adler32(json_object.encode("utf-8"))
        return str(hashName)

    def __eq__(self, container):
        # hier den Operator für die Klasse überschreiben
        # falls das eine gute Idee ist
        return self.data == container.data


class YAMLContainer:
    """
    A Container for YAML Files
    """

    def __init__(self, filename):
        """
        Initializes the container from file
        """
        # with open(filename) as f:
        #     self.data = yaml.load(f, Loader=yaml.SafeLoader)
        #     f.close()
        # self.filename = filename
        f = open(filename)
        self.data = yaml.load(f, Loader=yaml.SafeLoader)
        f.close()

    def __hasattr__(self, name):
        """
        Check if container contains specific item
        """
        if hasattr(self.data, name):
            return True
        else:
            return False

    def __getitem__(self, item):
        """
        Returns the value of specific item
        """
        return self.data[item]

    # def save(self, filename):
    def save(self):
        """
        Save container to file
        """
        # f = open(filename, "w")
        f = open(self.filename, "w")
        f.write(yaml.dump(self.data, default_flow_style=False, allow_unicode=True))
        f.close()


# import chefkoch.container as cont
# yam = cont.YAMLContainer("/home/maka/PycharmProjects
#                           /chefkoch/test/example.yaml")
# yeet = yam.xmas_fifth_day
# print( yeet["calling-birds"])
