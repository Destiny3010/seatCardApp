# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.


def fallback(fallback_value):
    """This decorator adds 'parse' class method into Enum class.
        'parse' method parses passed enum value.
        If the enum value is not defined in th enum members, 'fallback_value' will be used.
    """

    def wrapper(cls):
        def _parse(value):
            """Parses enum value with fallback."""
            try:
                # Try to parse enum value
                return cls(value)
            except ValueError:
                # Fallback because passed value is not defined in enum members
                return cls(fallback_value)

        # Add parse method
        cls.parse = _parse
        return cls

    return wrapper
