from typing import Optional
# import spacy
from sentence_transformers import SentenceTransformer, util
from .gdocs_parser import GDocsParser

gdocs: Optional[GDocsParser] = None
# spacy_model: Optional[spacy.Language] = None
sbert: Optional[SentenceTransformer] = None

# def load_spacy(self):
#     if not self.spacy_model:
#         print("Loading NLP model...")
#         self.spacy_model = spacy.load("en_core_web_lg")
#         # self.nlp = spacy.load("en_core_web_trf")

def load_sbert():
    global sbert
    if not sbert:
        try:
            # Load the SentenceTransformer model
            print("Loading SentenceTransformer model...")
            # self.sbert = SentenceTransformer("all-mpnet-base-v2")
            sbert = SentenceTransformer("all-MiniLM-L6-v2")

        except Exception as e:
            #@REVISIT
            print(e)
            print("Failed to load SentenceTransformer model.")
            return

def measure_excerpt_similarity(excerpt1, excerpt2, engine="sbert"):
    """
    Measure the similarity between two excerpts.
    """

    if engine == "sbert":
        return measure_excerpt_similarity_sbert(excerpt1, excerpt2)

    elif engine == "spacy":
        return measure_excerpt_similarity_spacy(excerpt1, excerpt2)

    else:
        raise ValueError("Invalid engine.")

# def measure_excerpt_similarity_spacy(excerpt1, excerpt2):
#     # Process the text
#     assert spacy_model is not None

#     doc1 = spacy_model(excerpt1)
#     doc2 = spacy_model(excerpt2)

#     # Measure the similarity
#     similarity = doc1.similarity(doc2)

#     # Return the similarity
#     return similarity

def measure_excerpt_similarity_sbert(excerpt1, excerpt2):
    if not sbert:
        load_sbert()

    # Compute embeddings
    embeddings1 = sbert.encode(excerpt1)
    embeddings2 = sbert.encode(excerpt2)

    # Compute cosine-similarities
    #@TODO move to GPU when possible and desired
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    
    return cosine_scores[0][0]

def compare_lists_sbert(a, b): #@REVISIT naming
    if not sbert:
        load_sbert()

    # Compute embeddings
    embeddings1 = sbert.encode(a, convert_to_tensor=True)
    embeddings2 = sbert.encode(b, convert_to_tensor=True)

    # Compute cosine-similarities
    #@TODO move to GPU when possible and desired
    cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)

    return cosine_scores

def load_google_doc(document_id):
    if not gdocs:
        # Initialize Google Docs API
        gdocs = GDocsParser()

        # Load credentials
        gdocs.load_credentials()

    # Load document
    document = gdocs.get_document(document_id)
