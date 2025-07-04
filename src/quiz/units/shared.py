class MappingError(Exception):
    """
    Exception raised when there is an error in mapping arguments to options.
    """

    pass


def map_args_to_option(option, args, mapping, required_length=0):
    """
    Map arguments to an option based on a provided mapping.

    Parameters:
    ---------
    option (dict): The option dictionary to update.
    args (list): The list of arguments to map.
    mapping (list of tuples): Each tuple contains a key and a type to convert
                            the argument to, e.g.:
                            [("key1", int), ("key2", str)]
    required_length (int): The number of arguments must match this length.
                                Defaults to 0.
    """
    if len(args) < required_length:
        raise MappingError(
            f"Expected at least {required_length} arguments"
        )

    if len(args) > len(mapping):
        raise MappingError(
            f"Too many arguments provided: {len(args)} > {len(mapping)}"
        )
    mapping = mapping[: len(args)]
    for arg, mapping in zip(args, mapping):
        key, type_ = mapping
        try:
            option.update({key: type_(arg)})
        except ValueError as e:
            raise MappingError(
                f"Invalid argument '{arg}'"
            ) from e
