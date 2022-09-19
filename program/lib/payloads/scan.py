# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from mfplib.app.comm import TaskPayload


class ScanTaskPayload(TaskPayload):
    """This class represents a task payload for background upload job after scan.

    Attributes:
        dir_path (str): Directory path which stores scan files.
    """

    def __init__(self, dir_path):
        """Initializes a new instance."""
        self.dir_path = dir_path
