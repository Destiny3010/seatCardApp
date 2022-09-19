# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from mfplib.app.config import AppConfig, AppConfigItem


class SampleConfig(AppConfig):
    """This class loads or saves settings using app config.

    Attributes:
        name (str): Sample setting name.
        value (str): Sample setting value.
    """

    # In 'meta/appconfdef.xml' file, 3 sections ('sample1', 'sample2' and 'sample3')
    # are defined.
    # These sections have same setting items which are 'name' and 'value'.

    _SECTION_COUNT = 3
    _SECTION_NAME = 'sample{}'

    name = AppConfigItem.text()  # App config has 'name' setting item and the type is text
    value = AppConfigItem.text()  # App config has 'value' setting item and the type is text

    @classmethod
    def load_one(cls, api_token, section_id):
        """Loads 'sample' section setting from app config.

        Args:
            api_token (str): API access token.
            section_id (int): Section ID of 'sample' section
                (e.g. section_id = 1: 'sample1' section).
        Returns:
            SampleConfig: 'sample' section setting.
        """
        section = cls._SECTION_NAME.format(section_id)
        return super().load_section(api_token, section)

    @classmethod
    def load_all(cls, api_token):
        """Loads all settings of 'sample' sections from app config.

        Args:
            api_token (str): API access token.
        Returns:
            list[SampleConfig]: All settings of 'sample' sections.
        """
        sections = [
            cls._SECTION_NAME.format(i + 1)
            for i in range(cls._SECTION_COUNT)
        ]
        return super().load_sections(api_token, sections)

    def save(self, api_token, section_id):
        """Saves current 'name' and 'value' into specific 'sample' section
        in app config.

        Args:
            api_token (str): API access token.
        """
        section = self._SECTION_NAME.format(section_id)
        super().save_section(api_token, section)
