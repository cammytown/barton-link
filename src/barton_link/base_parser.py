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
    """

    def __init__(self,
                 content,
                 metadata = None,
                 tags = None,
                 indent_level = 0,
                 # is_duplicate = False
                 ):
        self.content = content

        self.children = []

        if tags is None:
            self.tags = []
        else:
            self.tags = tags

        self.metadata = metadata

        self.indent_level = indent_level
        # self.is_duplicate = is_duplicate

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
            # 'is_duplicate': self.is_duplicate
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
                                # is_duplicate = data['is_duplicate']
                                )

        excerpt.children = [ParserExcerpt.from_dict(child)
                            for child in data['children']]

        return excerpt

class BaseParser:
    """
    Base parser.
    """

    def __init__(self):
        self.reset_state()
        self.default_tags = [] #@REVISIT should this just be part of state?

    def close_heading(self):
        # Reverse category_excerpts and add to excerpts
        #@TODO-3 this is specific to our purposes of vaguely attempting to
        # vaguely add entries in the order we added them to the document
        # self.state['excerpts'] += self.state['category_excerpts'][::-1]

        # Reset category_excerpts
        self.state['category_excerpts'] = []

    def update_heading(self, heading, level = 1):
        """
        Updates the parser's heading hierarchy state when encountering a new heading.
        
        This method manages a hierarchical structure of headings (like h1, h2, h3 in HTML or
        #, ##, ### in Markdown) which are used as tags for excerpts. When a new heading is 
        encountered:
        
        1. It closes any previous heading section
        2. For level 0, it resets the entire hierarchy to just this heading
        3. For levels > 0:
           - If the new heading is deeper than current (e.g. h1 -> h3), it pads intermediate
             levels with empty strings
           - If the new heading is shallower or same level (e.g. h3 -> h2), it truncates deeper
             headings and adds the new one
        
        The heading hierarchy is maintained as state and automatically added as tags to any
        excerpts created under those headings.
        
        Args:
            heading (str): The text content of the heading
            level (int, optional): The heading's level in hierarchy (0-based). Defaults to 1.
        """
        self.close_heading()

        # If level is 0, reset heading hierarchy
        if level == 0:
            self.state['heading_hierarchy'] = [heading]
            self.state['current_heading'] = heading
            self.state['current_heading_level'] = level

        # If level is > 0
        elif level > 0:
            cur_level = len(self.state['heading_hierarchy']) - 1
            diff = level - cur_level

            # If level is greater than current heading level
            if diff > 0:
                # Pad empty heading levels
                self.state['heading_hierarchy'] += [''] * diff

            # If level is less than or equal to current heading level
            else:
                # Remove trailing headings
                self.state['heading_hierarchy'] = \
                        self.state['heading_hierarchy'][:level + 1]

            # Update heading hierarchy
            self.state['heading_hierarchy'][level] = heading

    def add_excerpt(self,
                    excerpt: ParserExcerpt,
                    level = 0):

        # Pad working_excerpts with empty excerpts if necessary
        diff = level - len(self.state['working_excerpts']) + 1
        if diff > 0:
            self.state['working_excerpts'] += [None] * diff

        # Insert excerpt into working_excerpts
        self.state['working_excerpts'][level] = excerpt

        # Add default tags to excerpt
        excerpt.tags += self.default_tags

        # Add heading hierarchy to excerpt tags; remove empty tags
        excerpt.tags += [tag for tag in self.state['heading_hierarchy'] if tag]

        # Get parent excerpt
        parent_excerpt = None
        parent_level = level - 1
        while parent_excerpt is None and parent_level >= 0:
            parent_excerpt = self.state['working_excerpts'][parent_level]
            parent_level -= 1

        # If parent excerpt exists, add excerpt to parent excerpt
        if parent_excerpt is not None:
            parent_excerpt.children.append(excerpt)

        # If parent excerpt does not exist, add excerpt to excerpts
        else:
            self.state['excerpts'].append(excerpt)

        # # Add excerpt to working_excerpts stack
        # self.state['working_excerpts'].append(excerpt)

    def reset_state(self):
        self.state = {
            # 'document_id': None,
            'document_title': None,
            'heading_hierarchy': [],
            'current_heading': None,
            'current_heading_level': 1,
            'excerpts': [],
            'category_excerpts': [],
            'working_excerpts': []
        }
