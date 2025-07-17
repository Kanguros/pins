def get_matching_methods(obj: object | type, method_prefix: str) -> list[str]:
    """
    Discover matching methods for a given instance.

    Args:
        obj: The object to inspect methods.
        method_prefix: The prefix used to identify methods.

    Returns:
        List of format names.
    """
    formats = []
    for attr_name in dir(obj):
        if attr_name.startswith(method_prefix) and callable(
            getattr(obj, attr_name)
        ):
            format_name = attr_name[len(method_prefix) :]
            formats.append(format_name)
    return sorted(set(formats))
