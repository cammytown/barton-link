import spacy
from typing import Optional

from .database import Database
from .gdocs import GDocs

class BartonLink:
    db: Database
    gdocs: Optional[GDocs] = None

    def __init__(self):
        # Initialize the database
        self.db = Database()
        self.db.connect_to_database()

        # self.db.test_database()
        # self.db.close_database()

    def load_nlp_model(self):
        # Load the NLP model
        nlp = spacy.load("en_core_web_trf")

        # Process the text
        doc = nlp("Apple is looking at buying U.K. startup for $1 billion.")

        # For each token
        for token in doc:
            # Print the token text, part-of-speech tag, and dependency label
            print(token.text, token.pos_, token.dep_, token.head.text)

    def load_google_doc(self, document_id):
        if not self.gdocs:
            # Initialize Google Docs API
            self.gdocs = GDocs()

            # Load credentials
            self.gdocs.load_credentials()

        # Load document
        document = self.gdocs.get_document(document_id)

        # Parse document
        insert_statement = self.gdocs.parse_document_into_insert_statement(document)
        
        # Insert document into database
        self.db.c.execute(insert_statement)
        rowcount = self.db.c.rowcount
        self.db.conn.commit() #@REVISIT

        # Print rowcount
        print(f"Inserted {rowcount} rows into database.")

if __name__ == '__main__':
    barton_link = BartonLink()
