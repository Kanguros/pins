"""
Policy Inspector scenarios package.

This module imports all available scenarios to ensure they are registered.
"""

# Import legacy scenarios
from . import shadowing

# Import enhanced scenarios
try:
    from . import enhanced_shadowing  # noqa: F401
except ImportError:
    # Enhanced scenarios not available
    pass
