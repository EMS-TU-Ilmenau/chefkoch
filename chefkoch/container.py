"""
Container to store and manage information from JSON and YAML-Files.
The configuration is stored into a YAML-File, which can be managed
by the YAML-Container.
The JSON-Container manages other information like dependencies.
"""
import yaml
import json
import hashlib
import os.path


class JSONContainer:
    """
    A Container for JSON Files.
    It allows to initialize and manage a container.
    Furthermore it's possilbe to hash the content of the Container
    and merge it with other containers.
    """

    def __init__(self, filename: str = None, data: dict = None):
        """
        Initializes the container from file if path is given or
        a given dictionary else it creates an empty container.
        If given a file, the container is read only.

        Parameters
        ----------
            filename(str): name of a given file
            data(dict): a initialized dictionary

        """
        if filename is not None:
            with open(filename) as f:
                self.data = json.load(f)
                f.close()
            self.read_only = True
        elif data is not None:
            self.data = data
            # read_only eigentlich irrelevant
            self.read_only = False
        else:
            self.data = dict()
            self.read_only = False

    def __getitem__(self, item):
        """
        Returns value of specific key

        Parameters
        ----------
            item(str): name of wanted item
        """
        return self.data[item]

    def __setitem__(self, key, value):
        """
        Set value of specific key, if the container is not
        set to "read-only"

        Parameters
        ----------
            key(str): key of new entry
            value(): value of new entry
        """
        if not self.read_only:
            self.data[key] = value

    def save(self, filename):
        """
        Save container to a given filename

        Parameters
        ----------
            filename(str): name of file
        """
        json_object = json.dumps(self.data, indent=4)

        # Writing to sample.json
        with open(filename, "w") as outfile:
            outfile.write(json_object)
            outfile.close()

    def hash(self):
        """
        compute hash (sha256) over data

        Returns
        -------
            hashname(str)
        """
        json_object = json.dumps(self.data, indent=4)
        # geänderter Hash zu sha256
        h = hashlib.sha256()
        h.update(json_object.encode("utf-8"))
        hashName = h.hexdigest()
        return str(hashName)

    def __eq__(self, container):
        """
        Prototype-Function to determine if a given container has the
        sama data stored
        """
        # hier den Operator für die Klasse überschreiben
        # falls das eine gute Idee ist
        return self.data == container.data

    def merge(self, container):
        """
        Allows to merge the own data with data from another container

        Parameters
        ----------
        container(JSONContainer):
            a different JSONContainer
        """
        # es kann passieren, dass hier nochmal die Reihenfolge
        # geändert werden muss
        self.data.update(container.data)


class YAMLContainer:
    """
    A Container for YAML Files. It's used to organize the configuration.
    """

    def __init__(self, filename):
        """
        Initializes the container from file

        Parameters
        ----------
            filename(str): name of the file
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

        Parameters
        ----------
            name(str): name of item
        """
        if hasattr(self.data, name):
            return True
        else:
            return False

    def __getitem__(self, item):
        """
        Returns the value of specific item

        Parameters
        ----------
            name(str): name of wanted item
        """
        return self.data[item]

    # def save(self, filename):
    def save(self):
        """
        Save container to file
        """
        # f = open(filename, "w")
        f = open(self.filename, "w")
        f.write(
            yaml.dump(self.data, default_flow_style=False, allow_unicode=True)
        )
        f.close()
