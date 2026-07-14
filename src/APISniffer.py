# ---------------------------------------------------------------------------------- #
#                            Part of the X3r0Day project.                            #
#              You are free to use, modify, and redistribute this code,              #
#          provided proper credit is given to the original project X3r0Day.          #
# ---------------------------------------------------------------------------------- #

"""
APISniffer.py  —  Legacy wrapper / re-export module.

Kept for backward compatibility.  New code should import from
src.APIScanner directly.
"""

from src.APIScanner import main  # noqa: F401
