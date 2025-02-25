from __future__ import print_function

import json
import os.path
import appdirs

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base_parser import BaseParser
from .parser_excerpt import ParserExcerpt
# from .models import Excerpt, Tag

class GDocsParser(BaseParser):
    creds: Credentials = None
    scopes = ['https://www.googleapis.com/auth/documents.readonly']
    config_dir = appdirs.user_config_dir('barton-link', 'barton-link') + '/gdocs'
    cache_dir = appdirs.user_cache_dir('barton-link', 'barton-link')

    def __init__(self):
        super().__init__()

        # Create config directory
        os.makedirs(self.config_dir, exist_ok=True)

        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)

    def load_credentials(self):
        creds = self.creds

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(f'{self.config_dir}/token.json'):
            creds = Credentials.from_authorized_user_file(f'{self.config_dir}/token.json', self.scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                #@TODO we're getting an error when the token is expired that
                # shuts the whole show down. What I've been doing is deleting
                # the token.json file and re-running the script. Not clear on
                # how to handle this.
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f'{self.config_dir}/client_secret.json', self.scopes)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(f'{self.config_dir}/token.json', 'w') as token:
                token.write(creds.to_json())

        self.creds = creds

    def get_document(self, document_id):
        # Check for existence of cached document (gdoc-{document_id}.json)
        #@TODO-4 we don't always want to use the cached document— maybe only for
        # things like failed operations, or if the document hasn't changed since
        if os.path.exists(f'{self.cache_dir}/gdoc-{document_id}.json'):
            # Load cached document
            print('Loading cached document...')

            #@TODO use different path
            with open(f'{self.cache_dir}/gdoc-{document_id}.json', 'r') as f:
                document = json.loads(f.read())
                return document

        # If no cached document, retrieve document from Google Docs API
        else:
            # assert False, f'No cached document found at {self.cache_dir}/gdoc-{document_id}.json'

            try:
                print('Loading document from Google Docs API...')

                service = build('docs', 'v1', credentials=self.creds)

                # Retrieve the documents contents from the Docs service.
                document = service.documents().get(documentId=document_id).execute()

                # Cache document
                with open(f'{self.cache_dir}/gdoc-{document_id}.json', 'w') as f:
                    f.write(json.dumps(document))

                return document

            except HttpError as err:
                print(err)
                return None

    def parse_file_as_document(self, file_path):
        # Load file contents
        with open(file_path, 'r') as f:
            file_contents = f.read()

        # Parse file contents as JSON
        document = json.loads(file_contents)

        # Parse document
        self.parse_document(document)

    def parse_document(self, document, default_tags=[]):
        self.default_tags = default_tags

        doc_title = document.get('title')

        print(f'Parsing document: {doc_title}')

        # Get document title
        self.state['document_title'] = doc_title

        # Reset excerpts
        self.state['excerpts'] = []

        # Loop through document body components
        # offset = 400
        for idx, component in enumerate(document.get('body').get('content')):
            # if idx < offset:
            #     continue

            self.parse_component(component)

            # if idx > offset + 20: #@
            #     break

        self.close_heading()

        # # Remove trailing comma
        # self.state['working_insert'] = self.state['working_insert'][:-1]

        # return self.state['working_insert']
        return self.state['excerpts']

    #@REVISIT naming
    # def parse_document_into_insert_statement(self, document):
    #     doc_title = document.get('title')

    #     print(f'Parsing document: {doc_title}')

    #     # Get document title
    #     self.state['document_title'] = doc_title

    #     # Loop through document body components
    #     # for component in document.get('body').get('content'):
    #     # offset = 400
    #     for idx, component in enumerate(document.get('body').get('content')):
    #         # if idx < offset:
    #         #     continue

    #         self.parse_component(component)

    #         # if idx > offset + 20: #@
    #         #     break

    #     # Remove trailing comma
    #     self.state['working_insert'] = self.state['working_insert'][:-1]

    #     return self.state['working_insert']

    def parse_component(self, component):
        # Get content type (paragraph, table, etc.)
        content_type = None
        content_types = ['paragraph', 'table', 'tableOfContents', 'sectionBreak']
        for content_type in content_types:
            if component.get(content_type):
                content_type = content_type
                break

        # If not paragraph
        if content_type != 'paragraph':
            print(f'Ignoring {content_type}.')
            return

        excerpt = self.parse_paragraph(component)

        return excerpt

    def update_heading(self, heading, level = 1):
        # Reduce level by 1 (first gdocs heading is level 1, we want 0)
        level -= 1
        super().update_heading(heading, level)

    def parse_paragraph(self, component):
        # Get component type
        component_type = component.get('paragraph') \
                .get('paragraphStyle') \
                .get('namedStyleType')


        element_types = ['textRun',
                         'autoText',
                         'pageBreak',
                         'columnBreak',
                         'footnoteReference',
                         'horizontalRule',
                         'equation',
                         'inlineObjectElement',
                         'person',
                         'richLink',
                         ]

        # Get component text
        p_elements = component.get('paragraph').get('elements')
        component_text = ''
        for p_element in p_elements:
            element_type = None
            for type_key in element_types:
                if p_element.get(type_key):
                    element_type = type_key
                    break

            # If element_type is not textRun
            if element_type != 'textRun':
                print(f'Element type {element_type} not supported yet.')
                continue

            text = p_element.get('textRun').get('content')
            style = p_element.get('textRun').get('textStyle')

            # Apply styles
            if style.get('bold'):
                text = f'**{text}**'

            if style.get('italic'):
                text = f'*{text}*'

            if style.get('underline'):
                text = f'__{text}__'

            component_text += text

        # Trim surrounding whitespace
        component_text = component_text.strip()

        # Convert vertical tab to newline
        component_text = component_text.replace('\v', '\n')

        # Check if bullet
        nesting_level = 0
        bullet = component.get('paragraph').get('bullet')
        if bullet:
            # Get bullet nesting level
            nesting_level = bullet.get('nestingLevel')
            if nesting_level == None:
                nesting_level = 0

        # Check if heading (if starts within HEADING_*)
        if component_type.startswith('HEADING_'):
            # Get heading level
            level = int(component_type.split('_')[1])

            # Get heading text
            heading = component_text

            # Update heading hierarchy
            self.update_heading(heading, level)

        # Check if normal text
        elif component_type == 'NORMAL_TEXT':
            # If empty string, skip
            if not component_text:
                return

            # # If excerpt is nested under another
            # if nesting_level:
            #     # Add to previous excerpt
            #     #@REVISIT architecture
            #     self.state['category_excerpts'][-1].content += '\n===\n' \
            #             + component_text
            #     return

            excerpt = ParserExcerpt(content=component_text,
                                    # metadata=metadata,
                                    # tags=,
                                    indent_level=nesting_level)


            self.add_excerpt(excerpt, nesting_level)

            # Add document title as tag
            excerpt.tags.append(self.state['document_title'])

            # Add origin metadata
            #@TODO probably improve
            headers = [tag for tag in self.state['heading_hierarchy'] if tag]
            breadcrumbs = ' > '.join(headers)

            excerpt.metadata = {
                'origin': f'gdocs >> {self.state["document_title"]}' \
                        + f' >> {breadcrumbs}'
            }

        else:
            print(f'Unknown component type: {component_type}')

        # Print component type and text
        # print('Component type: {}'.format(component_type))
        # print('Component text: {}'.format(component_text))
        # print('Heading hierarchy: {}'.format(self.state['heading_hierarchy']))
        # print('Current heading: {}'.format(self.state['current_heading']))

    # def insert_excerpt(self, excerpt_text, tags, metadata):
    #     # If excerpt is empty
    #     if excerpt_text == '':
    #         # Skip excerpt
    #         return

    #     # Get Tag objects
    #     tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tags]

    #     excerpt = Excerpt(excerpt=excerpt_text, metadata=metadata)
    #     excerpt.save()

    #     # Add tags to excerpt
    #     excerpt.tags.add(*tags)

    #     # If excerpt is too long
    #     if len(excerpt['excerpt']) > 1000:
    #         # Skip excerpt
    #         print(f'WARNING: Excerpt too long: {excerpt["content"]}')
    #         return

    #     Escape single quotes
    #     excerpt['content'] = excerpt['content'].replace("'", "''")

    #     Build SQL insert statement
    #     insert_statement = 'INSERT INTO excerpts (excerpt, tags, metadata) VALUES ' \
    #             f"\n('{excerpt['content']}', " \
    #             f"'{json.dumps(excerpt['tags'])}', " \
    #             f"'{json.dumps(excerpt['metadata'])}');\n"

    # def build_insert_statement(self, excerpt):
    #     insert_statement = self.state['working_insert']

    #     # If an insert statement has not been started
    #     if insert_statement is None:
    #         # Begin SQL insert statement
    #         insert_statement = 'INSERT INTO excerpts (excerpt, tags, metadata) VALUES '

    #     # Validate excerpt for SQL
    #     # If excerpt is empty
    #     if excerpt['content'] == '':
    #         # Skip excerpt
    #         return

    #     # If excerpt is too long
    #     if len(excerpt['content']) > 1000:
    #         # Skip excerpt
    #         print(f'WARNING: Excerpt too long: {excerpt["content"]}')
    #         return

    #     # Escape single quotes
    #     excerpt['content'] = excerpt['content'].replace("'", "''")

    #     # Add excerpt to insert statement
    #     insert_statement += f"\n('{excerpt['content']}', " \
    #             f"'{json.dumps(excerpt['tags'])}', " \
    #             f"'{json.dumps(excerpt['metadata'])}'),"

    #     # Save working insert statement
    #     self.state['working_insert'] = insert_statement

    #     #@
    #     # # If insert statement is too long
    #     # if len(insert_statement) > 1000:

    #     return insert_statement

    # def print_document(self, document):
    #     print(document)
    #     print('The title of the document is: {}'.format(document.get('title')))
    #     print('The body of the document is: {}'.format(document.get('body')))
    #     print('The headers of the document are: {}'.format(document.get('headers')))

    #     # Write document body to file as pretty JSON
    #     body = document.get('body')
    #     body_pretty = json.dumps(body, indent=4)
    #     with open('testing.json', 'w') as f:
    #         f.write(body_pretty)

if __name__ == '__main__':
    gdocs = GDocsParser()
    gdocs.load_credentials()
    # gdocs.parse_file_as_document('testing.json')
    # document = gdocs.get_document('1bIMq-1G-Wzne1Rxu-ZOv5cFINq2pY9OVvnDntn_2Qb4')
    # gdocs.print_document(document)
