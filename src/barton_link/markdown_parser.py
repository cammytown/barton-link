from .base_parser import BaseParser, ParserExcerpt

class MarkdownParser(BaseParser):
    last_indent_level = 0

    def parse_text(self, text, default_tags = []):
        """
        Parse Markdown text.
        """

        # Reset state
        self.reset_state()

        # Split file_content on "\n"
        lines = text.split("\n")

        # For each line in file_lines
        for line in lines:
            # Get indentation
            indent_level = self.get_indent_level(line)

            # Strip whitespace
            line = line.strip()

            # If line is empty
            if not line:
                # Skip
                continue

            # Check if header
            if line.startswith("#"):
                # Get heading and heading level
                heading = line.lstrip("#").strip()
                heading_level = len(line) - len(heading)

                # Update heading
                self.update_heading(heading, heading_level)

            # If line is page break
            #@REVISIT
            elif line.startswith("---") or line.startswith("==="):
                # Close heading
                self.close_heading()

            # If line is not a header
            else:
                # If line is list item (starts with "- ")
                if line.startswith("- "):
                    # Get excerpt
                    excerpt = line.lstrip("- ").strip()
                # If line is not a list item
                #@REVISIT just treating it as an excerpt
                else:
                    # Get excerpt
                    excerpt = line

                # Create Excerpt instance
                excerpt_instance = ParserExcerpt(excerpt=excerpt,
                                                 tags=default_tags[:],
                                                 indent_level=indent_level)

                self.add_excerpt(excerpt_instance, indent_level)

        # Close heading
        self.close_heading()

        # Return excerpts
        return self.state['excerpts']

    def get_indent_level(self, line):
        """
        Get indent level.
        """

        tab_size = 4
        #@REVISIT
        # tab_size = self.guess_tab_size(lines)

        indent_level = 0

        # Get leading whitespace
        leading_whitespace = line[:len(line) - len(line.lstrip())]

        # If leading whitespace is not empty
        if leading_whitespace:
            # Count tabs
            tab_count = leading_whitespace.count("\t")

            # Count spaces
            space_count = leading_whitespace.count(" ")

            indent_level = (tab_count * tab_size) + space_count

        return indent_level

    # def guess_tab_size(self, lines):
    #     """
    #     Guess tab size.
    #     """

    #     tab_size_guess = 4
    #     last_indent_level = 0

    #     # For each line in file_lines
    #     for line in lines:
    #         # If line starts with tabs
    #         if line.startswith("\t"):
    #             # Get tab count
    #             tab_count = len(line) - len(line.lstrip("\t"))
    #             last_indent_level = tab_count

    #         # If line starts with spaces
    #         if line.startswith(" "):
    #             # Get space count
    #             space_count = len(line) - len(line.lstrip(" "))

    #             # If space count is divisible by tab_size_guess
    #             if space_count % tab_size_guess == 0:
