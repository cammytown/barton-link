import sys

from barton_link.barton_link import BartonLink

# Initialize BartonLink
barton_link = BartonLink()

assert len(sys.argv) == 2, "Please provide a document_id as an argument"

# Retrieve document_id arg
document_id = sys.argv[1]

# Load and parse a Google Doc
barton_link.load_google_doc(document_id)
