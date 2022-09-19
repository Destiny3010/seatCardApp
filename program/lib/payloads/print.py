# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from mfplib.app.comm import TaskPayload


class PrintTaskPayload(TaskPayload):
    """This class represents a task payload for background print job.

    Attributes:
        setting (mfplib.jobs.print.PrintSetting): Print setting.
        file_name (str): Target print file name.
    """

    def __init__(self, setting, file_name):
        """Initializes a new instance."""
        self.setting = setting
        self.file_name = file_name
