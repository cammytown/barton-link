from typing import Optional

import spacy
from sentence_transformers import SentenceTransformer, util

# from .database import Database
from .gdocs import GDocs

class BartonLink:
    # db: Database
    gdocs: Optional[GDocs] = None
    spacy_model: Optional[spacy.Language] = None
    sbert: Optional[SentenceTransformer] = None

    def __init__(self):
        # Initialize the database
        # self.db = Database()
        # self.db.connect_to_database()

        # self.db.test_database()
        # self.db.close_database()

        self.load_nlp_models()

    def load_nlp_models(self):
        print("Loading NLP model...")

        # Load the NLP model
        self.spacy_model = spacy.load("en_core_web_lg")
        # self.nlp = spacy.load("en_core_web_trf")

        print("Loading SentenceTransformer model...")
        # Load the SentenceTransformer model
        # self.sbert = SentenceTransformer("all-mpnet-base-v2")
        self.sbert = SentenceTransformer("all-MiniLM-L6-v2")

    def measure_excerpt_similarity(self, excerpt1, excerpt2, engine="sbert"):
        """
        Measure the similarity between two excerpts.
        """

        if engine == "sbert":
            return self.measure_excerpt_similarity_sbert(excerpt1, excerpt2)

        elif engine == "spacy":
            return self.measure_excerpt_similarity_spacy(excerpt1, excerpt2)

        else:
            raise ValueError("Invalid engine.")

    def measure_excerpt_similarity_spacy(self, excerpt1, excerpt2):
        # Process the text
        assert self.spacy_model is not None

        doc1 = self.spacy_model(excerpt1)
        doc2 = self.spacy_model(excerpt2)

        # Measure the similarity
        similarity = doc1.similarity(doc2)

        # Return the similarity
        return similarity

    def measure_excerpt_similarity_sbert(self, excerpt1, excerpt2):
        # Use SentenceTransformer to measure similarity
        assert self.sbert is not None

        # Compute embeddings
        embeddings1 = self.sbert.encode(excerpt1)
        embeddings2 = self.sbert.encode(excerpt2)

        # Compute cosine-similarities
        #@TODO move to GPU when possible and desired
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        
        return cosine_scores[0][0]

    def load_google_doc(self, document_id):
        if not self.gdocs:
            # Initialize Google Docs API
            self.gdocs = GDocs()

            # Load credentials
            self.gdocs.load_credentials()

        # Load document
        document = self.gdocs.get_document(document_id)

        # # Parse document
        # insert_statement = self.gdocs.parse_document_into_insert_statement(document)
        
        # # Insert document into database
        # self.db.c.execute(insert_statement)
        # rowcount = self.db.c.rowcount
        # self.db.conn.commit() #@REVISIT

        # # Print rowcount
        # print(f"Inserted {rowcount} rows into database.")

if __name__ == '__main__':
    barton_link = BartonLink()
