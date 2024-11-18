class NoCarsSelected(Exception):
    # thrown in goal simulation when all cars are release and only bikes are selected
    self_defined = True
    pass


class NoSolutionFound(Exception):
    # thrown when no solutions found in Tabu search
    self_defined = True
    pass


class MetadataColumnError(Exception):
    self_defined = True


class MetadataRowInvalidError(Exception):
    self_defined = True


class MetadataFileError(Exception):
    self_defined = True
