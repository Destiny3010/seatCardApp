# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

"""This module implements ScanSetting class."""

from enum import Enum
from ...utilities.enum_fallback import fallback


@fallback('pdf_multi')
class ImageFileFormat(Enum):
    """This enum represents scan image file format."""
    Jpeg = 'jpeg'
    TiffSingle = 'tiff_single'
    TiffMulti = 'tiff_multi'
    PdfSingle = 'pdf_single'
    PdfMulti = 'pdf_multi'
    SearchablePdfSingle = 'searchable_pdf_single'
    SearchablePdfMulti = 'searchable_pdf_multi'
    PdfASingle = 'pdf_a_single'
    PdfAMulti = 'pdf_a_multi'
    SearchablePdfASingle = 'searchable_pdf_a_single'
    SearchablePdfAMulti = 'searchable_pdf_a_multi'
    SlimPdfSingle = 'slim_pdf_single'
    SlimPdfMulti = 'slim_pdf_multi'
    SearchableSlimPdfSingle = 'searchable_slim_pdf_single'
    SearchableSlimPdfMulti = 'searchable_slim_pdf_multi'
    WordSingle = 'word_single'
    WordMulti = 'word_multi'
    ExcelSingle = 'excel_single'
    ExcelMulti = 'excel_multi'
    PowerPointSingle = 'power_point_single'
    PowerPointMulti = 'power_point_multi'

    def is_ocr_necessary(self):
        """Gets whether file format needs OCR or not.

        Returns:
            bool: This file format needs OCR.
        """
        ocr_needed = self in [
            ImageFileFormat.SearchablePdfSingle,
            ImageFileFormat.SearchablePdfMulti,
            ImageFileFormat.SearchablePdfASingle,
            ImageFileFormat.SearchablePdfAMulti,
            ImageFileFormat.SearchableSlimPdfSingle,
            ImageFileFormat.SearchableSlimPdfMulti,
            ImageFileFormat.WordSingle,
            ImageFileFormat.WordMulti,
            ImageFileFormat.ExcelSingle,
            ImageFileFormat.ExcelMulti,
            ImageFileFormat.PowerPointSingle,
            ImageFileFormat.PowerPointMulti,
        ]
        return ocr_needed


@fallback('black')
class ColorMode(Enum):
    """This enum represents scan color mode."""
    Black = 'black'
    GrayScale = 'gray_scale'
    FullColor = 'full_color'
    Auto = 'auto'


@fallback('dpi200')
class Resolution(Enum):
    """This enum represents scan resolution."""
    Dpi100 = 'dpi100'
    Dpi150 = 'dpi150'
    Dpi200 = 'dpi200'
    Dpi300 = 'dpi300'
    Dpi400 = 'dpi400'
    Dpi600 = 'dpi600'


@fallback('text')
class OriginalMode(Enum):
    """This enum represents scan original mode."""
    Text = 'text'
    TextPhoto = 'text_photo'
    Photo = 'photo'
    Custom = 'custom'
    BlueOriginal = 'blue_original'


@fallback('angle0')
class ImageRotation(Enum):
    """This enum represents scan image rotation."""
    Angle0 = 'angle0'
    Angle90 = 'angle90'
    Angle180 = 'angle180'
    Angle270 = 'angle270'


@fallback('simplex')
class DuplexMode(Enum):
    """This enum represents scan duplex mode."""
    Simplex = 'simplex'
    Book = 'duplex_book'
    Tablet = 'duplex_tablet'


@fallback('zero')
class ExposureLevel(Enum):
    """This enum represents exposure level."""
    Auto = 'auto'
    Zero = 'zero'
    Positive1 = 'positive1'
    Positive2 = 'positive2'
    Positive3 = 'positive3'
    Positive4 = 'positive4'
    Positive5 = 'positive5'
    Negative1 = 'negative1'
    Negative2 = 'negative2'
    Negative3 = 'negative3'
    Negative4 = 'negative4'
    Negative5 = 'negative5'


@fallback('zero')
class BackgroundLevel(Enum):
    """This enum represents background adjustment level."""
    Zero = 'zero'
    Positive1 = 'positive_1'
    Positive2 = 'positive_2'
    Positive3 = 'positive_3'
    Positive4 = 'positive_4'
    Negative1 = 'negative_1'
    Negative2 = 'negative_2'
    Negative3 = 'negative_3'
    Negative4 = 'negative_4'


@fallback('zero')
class ContrastLevel(Enum):
    """This enum represents contrast level."""
    Zero = 'zero'
    Positive1 = 'positive_1'
    Positive2 = 'positive_2'
    Positive3 = 'positive_3'
    Positive4 = 'positive_4'
    Negative1 = 'negative_1'
    Negative2 = 'negative_2'
    Negative3 = 'negative_3'
    Negative4 = 'negative_4'


@fallback('zero')
class SharpnessLevel(Enum):
    """This enum represents sharpness level."""
    Zero = 'zero'
    Positive1 = 'positive_1'
    Positive2 = 'positive_2'
    Positive3 = 'positive_3'
    Positive4 = 'positive_4'
    Negative1 = 'negative_1'
    Negative2 = 'negative_2'
    Negative3 = 'negative_3'
    Negative4 = 'negative_4'


@fallback('english')
class OcrLanguage(Enum):
    """This enum represents OCR language."""
    None_ = 'none'
    English = 'english'
    German = 'german'
    French = 'french'
    Spanish = 'spanish'
    Italian = 'italian'
    Danish = 'danish'
    Finnish = 'finnish'
    Norwegian = 'norwegian'
    Swedish = 'swedish'
    Netherlandish = 'netherlandish'
    Polish = 'polish'
    Russian = 'russian'
    Japanese = 'japanese'
    ChineseSimplified = 'chinese_simplified'
    ChineseTraditional = 'chinese_traditional'
    BrazilianPortuguese = 'brazilian_portuguese'
    EuropeanPortuguese = 'european_portuguese'
    Turkish = 'turkish'


class OcrSetting:
    """This class represents a OCR setting.

    Attributes:
        primary_language (OcrLanguage): Primary OCR language.
        secondary_language (OcrLanguage): Secondary OCR language.
        auto_rotation (bool): Auto rotation enabled or not.
    """
    def __init__(
            self,
            primary_language=OcrLanguage.English,
            secondary_language=OcrLanguage.None_,
            auto_rotation=False):
        self.primary_language = primary_language
        self.secondary_language = secondary_language
        self.auto_rotation = auto_rotation

    def serialize(self):
        """Serializes this instance.

        Returns:
            dict: Serialized data of this instance.
        """
        serialized = {
            'primary_language': self.primary_language.value,
            'secondary_language': self.secondary_language.value,
            'auto_rotation': self.auto_rotation,
        }
        return serialized


class ScanSetting:
    """This class represents a scan setting.

    Attributes:
        file_format (~mfplib.jobs.scan.ImageFileFormat): Image file format.
        color_mode (~mfplib.jobs.scan.ColorMode): Color mode.
        resolution (~mfplib.jobs.scan.Resolution): Resolution.
        original_mode (~mfplib.jobs.scan.OriginalMode): Original mode.
        image_rotation (~mfplib.jobs.scan.ImageRotation): Image rotation.
        duplex_mode (~mfplib.jobs.scan.DuplexMode): Duplex mode.
        preview (bool): Scan image preview enabled or not.
        omit_blank_page (bool): Omit blank page enabled or not.
        ocr (OcrSetting): OCR setting.
        exposure (~mfplib.jobs.scan.ExposureLevel): Exposure level.
        background (~mfplib.jobs.scan.BackgroundLevel): Background adjustment level.
        contrast (~mfplib.jobs.scan.ContrastLevel): Contrast level.
        sharpness (~mfplib.jobs.scan.SharpnessLevel): Sharpness level.
    """
    def __init__(
            self,
            file_format=ImageFileFormat.PdfSingle,
            color_mode=ColorMode.Black,
            resolution=Resolution.Dpi300,
            original_mode=OriginalMode.Text,
            image_rotation=ImageRotation.Angle0,
            duplex_mode=DuplexMode.Simplex,
            preview=False,
            omit_blank_page=False,
            ocr=None,
            exposure=ExposureLevel.Auto,
            background=BackgroundLevel.Zero,
            contrast=ContrastLevel.Zero,
            sharpness=SharpnessLevel.Zero):
        self.file_format = file_format
        self.color_mode = color_mode
        self.resolution = resolution
        self.original_mode = original_mode
        self.image_rotation = image_rotation
        self.duplex_mode = duplex_mode
        self.preview = preview
        self.omit_blank_page = omit_blank_page
        self.ocr = OcrSetting() if ocr is None else ocr
        self.exposure = exposure
        self.background = background
        self.contrast = contrast
        self.sharpness = sharpness

    def serialize(self):
        """Serializes this instance.

        Returns:
            dict: Serialized data of this instance.
        """
        serialized = {
            'file_format': self.file_format.value,
            'color_mode': self.color_mode.value,
            'resolution': self.resolution.value,
            'original_mode': self.original_mode.value,
            'image_rotation': self.image_rotation.value,
            'duplex_mode': self.duplex_mode.value,
            'preview': self.preview,
            'omit_blank_page': self.omit_blank_page,
            'exposure': self.exposure.value,
            'background': self.background.value,
            'contrast': self.contrast.value,
            'sharpness': self.sharpness.value,
        }

        if self.ocr:
            serialized['ocr'] = self.ocr.serialize()

        return serialized
