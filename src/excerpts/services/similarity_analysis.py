import django

from barton_link import barton_link

from ..models import Excerpt,\
        ExcerptSimilarity,\
        Job

from .service import Service

class SimilarityAnalysisService(Service):
    """
    Service for analyzing similarities between excerpts using NLP.
    """

    def __init__(self):
        super().__init__("similarity_analysis")

    def run(self):
        """
        Analyze similarities between excerpts using NLP.
        """

        print("Running similarity analysis...")

        # Close any old database connections
        #@REVISIT is this necessary?
        django.db.connections.close_all()

        #@REVISIT we have chosen to individually compare each excerpt to every
        #@ other excerpt so that progress can be easily tracked. an obvious
        #@ improvement would be to do batches in a manner similar to what is
        #@ outlined at
        #@ https://www.sbert.net/docs/usage/semantic_textual_similarity.html

        #@REVISIT redundant w/ start_similarity_analysis
        # Check for existence of similarity analysis Job in database

        job = self.get_job()

        if job == None:
            job = Job.objects.create(
                name="similarity_analysis",
                total=Excerpt.objects.count(),
            )

        similarities_stored = 0

        current_progress = job.progress
        compare_cursor = job.subprogress

        # Get all excerpts, order by ascending id, starting from current_progress
        #@TODO optimization; is Django loading all excerpts into memory?
        excerpts = Excerpt.objects.order_by('id')[current_progress:]

        # For each excerpt
        for excerpt in excerpts:
            # Get excerpt text
            excerpt_text = excerpt.content

            # Update job progress
            job.progress = excerpt.id
            job.save()

            # For each other excerpt
            for other_excerpt in excerpts[compare_cursor:]:
                # Update job progress every 25 excerpts
                #@REVISIT
                if other_excerpt.id % 25 == 0:
                    job.subprogress = other_excerpt.id
                    job.save()

                if self.running == False:
                    return

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
                print("===== (similarities added: " + str(similarities_stored) + ")")

                # Check if similarity already exists
                similarity_entry = ExcerptSimilarity.objects.filter(
                    excerpt1=excerpt,
                    excerpt2=other_excerpt,
                ).first()

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

                    similarities_stored += 1

            # Move compare_cursor to next excerpt (id is next excerpt's index)
            compare_cursor = excerpt.id

        # return HttpResponse(
        #     f"Created {similarities_stored} new ExcerptSimilarity entries."
        # )
