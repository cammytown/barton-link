class ParserExcerpt:
    """
    Parser excerpt.
    """

    def __init__(self,
                 excerpt,
                 metadata = None,
                 tags = [],
                 indent_level = 0,
                 # is_duplicate = False
                 ):
        self.excerpt = excerpt
        self.children = []
        self.tags = tags
        self.metadata = metadata
        self.indent_level = indent_level
        # self.is_duplicate = is_duplicate

    def __repr__(self):
        return "<Excerpt: {}>".format(self.excerpt)

    def __str__(self):
        return self.excerpt

    def to_dict(self):
        """
        To dict.
        """

        return {
            'excerpt': self.excerpt,
            'metadata': self.metadata,
            'tags': self.tags,
            'children': [child.to_dict() for child in self.children],
            'indent_level': self.indent_level,
            # 'is_duplicate': self.is_duplicate
        }

    @staticmethod
    def from_dict(data):
        """
        From dict.
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

    def close_heading(self):
        # Reverse category_excerpts and add to excerpts
        #@TODO-3 this is specific to our purposes of vaguely attempting to
        # vaguely add entries in the order we added them to the document
        # self.state['excerpts'] += self.state['category_excerpts'][::-1]

        # Reset category_excerpts
        self.state['category_excerpts'] = []

    def update_heading(self, heading, level = 1):
        # Reduce level by 1 (first gdocs heading is level 1, we want 0)
        level -= 1

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

        # Add heading hierarchy to excerpt tags; remove empty tags
        excerpt.tags += [tag for tag in self.state['heading_hierarchy'] if tag]

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
