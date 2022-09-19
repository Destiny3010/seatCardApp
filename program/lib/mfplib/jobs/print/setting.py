# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

"""This module implements PrintSetting class."""

from enum import Enum
from ...utilities.enum_fallback import fallback


@fallback('a4')
class PaperSize(Enum):
    """This enum represents a print paper size."""
    A3 = 'a3'  # A3
    A4 = 'a4'  # A4
    A5 = 'a5'  # A5-R
    Letter = 'letter'  # LT
    Legal = 'legal'  # LG
    Ledger = 'ledger'  # LD
    B4 = 'b4'  # B4
    B5 = 'b5'  # B5
    Folio = 'folio'  # FOLIO
    Statement = 'statement'  # ST-R
    Computer = 'computer'  # COMP
    GovernmentLegal = '13_legal'  # 13"LG
    Square85 = '85_sq'  # 8.5SQ


@fallback('mono')
class ColorMode(Enum):
    """This enum represents print color mode."""
    Mono = 'mono'
    FullColor = 'full_color'
    AutoColor = 'auto_color'


@fallback('normal')
class TonerMode(Enum):
    """This enum represents print toner mode."""
    Normal = 'normal'
    ErasableBlue = 'erasableblue'


@fallback('simplex')
class DuplexMode(Enum):
    """This enum represents print duplex mode."""
    Simplex = 'simplex'
    Book = 'duplex_book'
    Tablet = 'duplex_tablet'


@fallback('non_staple')
class StaplePosition(Enum):
    """This enum represents print staple position."""
    None_ = 'non_staple'
    UpperLeft = 'upper_left'
    UpperRight = 'upper_right'
    DualTop = 'dual_top'
    DualLeft = 'dual_left'
    SaddleStitch = 'saddle_stitch'


@fallback('none')
class HolePunchPosition(Enum):
    """This enum represents print hole punch position."""
    None_ = 'none'
    MiddleLeft = 'middle_left'
    CenterTop = 'center_top'


@fallback('fit')
class ScalingType(Enum):
    """This enum represents print page scaling type."""
    Fit = 'fit'  # Enlarge or shrink to fit to paper size
    ShrinkOnly = 'shrink_only'  # Shrink overred size


class PrintSetting:
    """This class represents a print setting.

    Attributes:
        sets (int): Print sets.
        paper_size (~mfplib.jobs.print.PaperSize): Paper size.
            This parameter is available when original_size_prioritized is False.
        color_mode (~mfplib.jobs.print.ColorMode): Color mode.
        toner_mode (~mfplib.jobs.print.TonerMode): Toner mode.
        duplex_mode (~mfplib.jobs.print.DuplexMode): Duplex mode.
        staple (~mfplib.jobs.print.StaplePosition): Staple position.
        hole_punch (~mfplib.jobs.print.HolePunchPosition): Hole punch position.
        original_size_prioritized (bool): Output paper size is set based on original size in file, or not.
            This parameter is available when print file format is PDF based.
        scaling_type (~mfplib.jobs.print.ScalingType): Page scaling type for print page size.
            This parameter is available when original_size_prioritized is False.
    """
    def __init__(
            self,
            sets=1,
            paper_size=PaperSize.A4,
            color_mode=ColorMode.Mono,
            toner_mode=TonerMode.Normal,
            duplex_mode=DuplexMode.Simplex,
            staple=StaplePosition.None_,
            hole_punch=HolePunchPosition.None_,
            original_size_prioritized=True,
            scaling_type=ScalingType.Fit):
        self.paper_size = paper_size
        self.sets = sets
        self.color_mode = color_mode
        self.toner_mode = toner_mode
        self.duplex_mode = duplex_mode
        self.staple = staple
        self.hole_punch = hole_punch
        self.original_size_prioritized = original_size_prioritized
        self.scaling_type = scaling_type

    def serialize(self):
        """Serializes this instance.

        Returns:
            dict: Serialized data of this instance.
        """
        serialized = {
            'sets': self.sets,
            'paper_size': self.paper_size.value,
            'color_mode': self.color_mode.value,
            'toner_mode': self.toner_mode.value,
            'duplex_mode': self.duplex_mode.value,
            'staple': self.staple.value,
            'hole_punch': self.hole_punch.value,
            'original_size_prioritized': self.original_size_prioritized,
            'scaling_type': self.scaling_type.value,
        }
        return serialized
