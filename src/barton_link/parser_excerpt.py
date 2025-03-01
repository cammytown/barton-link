class ParserExcerpt:
    """
    A class representing a parsed excerpt of text with associated metadata.

    This class is used to store and manipulate excerpts of text extracted during parsing,
    along with metadata like tags, source information, and hierarchical relationships.
    It supports serialization to/from dictionaries and maintains a tree structure
    through parent-child relationships between excerpts.

    Attributes:
        content (str): The actual text content of the excerpt
        metadata (dict): Additional metadata about the excerpt like source, date etc.
        tags (list): List of tags/categories associated with the excerpt
        indent_level (int): The indentation level indicating hierarchy
        children (list): List of child ParserExcerpt objects
        is_duplicate (bool): Flag indicating if this excerpt is a duplicate
    """

    def __init__(self,
                 content,
                 metadata = None,
                 tags = None,
                 indent_level = 0,
                 is_duplicate = False
                 ):
        self.content = content

        self.children = []

        if tags is None:
            self.tags = []
        else:
            self.tags = tags

        self.metadata = metadata

        self.indent_level = indent_level
        self.is_duplicate = is_duplicate

    def __repr__(self):
        return "<Excerpt: {}>".format(self.content)

    def __str__(self):
        return self.content

    def to_dict(self):
        """
        Serializes the excerpt and its children to a dictionary format.
        """

        return {
            'excerpt': self.content,
            'metadata': self.metadata,
            'tags': self.tags,
            'children': [child.to_dict() for child in self.children],
            'indent_level': self.indent_level,
            'is_duplicate': self.is_duplicate
        }

    @staticmethod
    def from_dict(data):
        """
        Creates a ParserExcerpt instance from a dictionary representation.
        """

        excerpt = ParserExcerpt(data['excerpt'],
                                metadata = data['metadata'],
                                tags = data['tags'],
                                indent_level = data['indent_level'],
                                is_duplicate = data.get('is_duplicate', False)
                                )

        excerpt.children = [ParserExcerpt.from_dict(child)
                            for child in data['children']]

        return excerpt 