from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render

from barton_link.barton_link import BartonLink
from ..models import Excerpt, ExcerptSimilarity, Tag, TagType

barton_link = BartonLink()
from barton_link.gdocs import GDocs

def analyze_similarities(request):
    """
    Analyze similarities between excerpts using NLP.
    """

    barton_link.load_nlp_models() #@REVISIT architecture

    created_count = 0

    # Get all excerpts, order by ascending id
    excerpts = Excerpt.objects.order_by("id")

    # For each excerpt
    for excerpt in excerpts:
        # Get excerpt text
        excerpt_text = excerpt.content

        # For each other excerpt
        for other_excerpt in excerpts[excerpt.id:]:
            # If other_excerpt is the same as excerpt
            #@REVISIT perhaps unnecessary with the excerpts[excerpt.id:] slice
            if other_excerpt == excerpt:
                # Skip
                continue

            #@REVISIT also should be unnecessary with excerpts[excerpt.id:]
            # The order is important for querying the database
            assert other_excerpt.id > excerpt.id

            # Get other_excerpt text
            other_excerpt_text = other_excerpt.content

            # Measure similarities
            sbert_similarity = barton_link.measure_excerpt_similarity_sbert(
                    excerpt_text,
                    other_excerpt_text
                    )

            # spacy_similarity = barton_link.measure_excerpt_similarity_spacy(
            #         excerpt_text,
            #         other_excerpt_text
            #         )

            threshold = 0.4

            # If similarity is below threshold
            if abs(sbert_similarity) < threshold:
                # Skip
                continue

            print(f"Similarity between {excerpt.id} and {other_excerpt.id} " \
                    + f" exceeds threshold < -{threshold} or > {threshold}")
            print(f"SBERT: {sbert_similarity}")
            # print(f"SpaCy: {spacy_similarity}")
            print(excerpt_text)
            print("-----")
            print(other_excerpt_text)
            print("===== (similarities added: " + str(created_count) + ")")

            # Check if similarity already exists
            similarity_entry = ExcerptSimilarity.objects.filter(
                    excerpt1=excerpt,
                    excerpt2=other_excerpt,
                    )

            if similarity_entry:
                # Check for differing similarity values
                if similarity_entry.sbert_similarity != sbert_similarity:
                    print(f"WARNING: SBERT similarity mismatch for " \
                            + "{excerpt.id} and {other_excerpt.id}:")
                    print(f"Existing: {similarity_entry.sbert_similarity}")
                    print(f"New: {sbert_similarity}")
                    print("Updating similarity value...")

                    # Update similarity value
                    similarity_entry.sbert_similarity = sbert_similarity

                    # Save similarity entry
                    similarity_entry.save()

                #@REVISIT do we care abouy spacy? probably not.

            # If similarity does not already exist
            else:
                # Create ExcerptSimilarity instance
                similarity_entry = ExcerptSimilarity(
                        excerpt1=excerpt,
                        excerpt2=other_excerpt,
                        sbert_similarity=sbert_similarity,
                        # spacy_similarity=spacy_similarity
                        )
                similarity_entry.save()

                created_count += 1

    return HttpResponse(f"Created {created_count} new ExcerptSimilarity entries.")

def import_excerpts(request):
    match request.method:
        case "GET":
            tags = Tag.objects.all()
            tag_types = TagType.objects.all()

            return render(request, "excerpts/import/import_page.html", {
                "tags": tags,
                "tag_types": tag_types,
                })

        case _:
            return HttpResponseNotFound()

def gdocs_test(request):
    # Initialize Google Docs API
    gdocs = GDocs()

    # Load credentials
    gdocs.load_credentials()

    # Load doc-ids.txt
    #@TODO-4 temporary
    with open("../data/debug/gdoc_ids.txt", "r") as f:
        document_ids = f.readlines()

    # Split document_ids on == (format is document_name == document_id)
    document_ids = [document_id.split(" == ")[1].strip() \
            for document_id in document_ids]

    response = f"Loaded {len(document_ids)} document ids."

    # Print all document_ids
    # for document_id in document_ids:
    #     response += f"\ndoc: {document_id}"

    # print(response)
    # exit()

    # Load and parse each Google Doc
    for document_id in document_ids:
        # Load document
        document = gdocs.get_document(document_id)
        excerpt_dicts = gdocs.parse_document(document)

        # Turn excerpt_dicts into Excerpt instances
        excerpt_objs = []
        for exc_idx, excerpt_dict in enumerate(excerpt_dicts):
            # Check if excerpt already exists in database
            if Excerpt.objects.filter(
                    excerpt=excerpt_dict["excerpt"],
                    metadata=excerpt_dict["metadata"],
                    ).exists():

                print("Excerpt already exists in database: " \
                        + f"{excerpt_dict['excerpt']}")

                excerpt_dict["excerpt_instance"] = None

                # Skip to next excerpt
                continue

            # If excerpt does not exist in database
            else:
                # print(f"Excerpt does not exist in database: {excerpt_dict['excerpt']}")

                # Create Excerpt instance
                #@REVISIT architecture
                excerpt_dict["excerpt_instance"] = Excerpt(
                    excerpt=excerpt_dict["excerpt"],
                    metadata=excerpt_dict["metadata"],
                )

                excerpt_objs.append(excerpt_dict["excerpt_instance"])

        # Insert excerpts into database
        excerpts = Excerpt.objects.bulk_create(excerpt_objs)

        # Create ExcerptVersion instances
        for excerpt_dict in excerpt_dicts:
            # If excerpt_instance is None
            if not excerpt_dict["excerpt_instance"]:
                # Skip to next excerpt
                #@REVISIT architecture
                continue

            excerpt = excerpt_dict["excerpt_instance"]

            # Create ExcerptVersion instance
            excerpt_version = ExcerptVersion(
                    excerpt=excerpt,
                    version=excerpt_dict["version"],
                    )

            # Save ExcerptVersion instance
            excerpt_version.save()

        # Add tags to excerpts
        for excerpt_dict in excerpt_dicts:
            if "excerpt_instance" not in excerpt_dict:
                raise Exception("Excerpt instance not found in excerpt_dict")

            # If excerpt_instance is None
            if not excerpt_dict["excerpt_instance"]:
                # Skip to next excerpt
                #@REVISIT architecture
                continue

            excerpt = excerpt_dict["excerpt_instance"]

            for tag_name in excerpt_dict["tags"]:
                tag = Tag.objects.get_or_create(name=tag_name)[0]
                excerpt.tags.add(tag)

        response += f"\nLoaded {len(excerpt_dicts)} excerpts from {document_id}."

    return HttpResponse(response)
