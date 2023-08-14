import django
from threading import Thread

from ..models import Excerpt,\
        ExcerptSimilarity,\
        Job

from barton_link import barton_link

class SimilarityAnalysisService:
    running = False

    def start(self):
        """
        Start similarity analysis.
        """

        # If similarity analysis is already running, return
        if self.running == True:
            return

        # Set running to True
        self.running = True

        # Create thread and run analysis
        thread = Thread(target=self.run)
        thread.start()

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
        #@ outlined at https://www.sbert.net/docs/usage/semantic_textual_similarity.html

        #@REVISIT redundant w/ start_similarity_analysis
        # Check for existence of similarity analysis Job in database
        try:
            job = Job.objects.get(name="similarity_analysis")

        # If no Job exists, create one
        except Job.DoesNotExist:
            job = Job.objects.create(
                name="similarity_analysis",
                total=Excerpt.objects.count(),
            )

        #@SCAFFOLDING
        # If job.total is 0, set it to the number of excerpts
        if job.total == 0:
            job.total = Excerpt.objects.count()
            job.save()

        similarities_stored = 0

        current_progress = job.progress
        compare_progress = job.subprogress

        # Get all excerpts, order by ascending id, starting from current_progress
        excerpts = Excerpt.objects.order_by('id')[current_progress:]

        # For each excerpt
        for excerpt in excerpts:
            # Get excerpt text
            excerpt_text = excerpt.content

            # For each other excerpt
            for other_excerpt in excerpts[compare_progress:]:
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

                # Update job progress every 25 excerpts
                #@REVISIT don't do this constantly
                if other_excerpt.id % 25 == 0:
                    job.subprogress = other_excerpt.id
                    job.save()

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

            # Reset compare_progress
            #@REVISIT weird; triple check that + 1 is correct
            compare_progress = excerpt.id + 1

            # Update job progress
            job.progress = excerpt.id
            job.save()

        return HttpResponse(f"Created {similarities_stored} new ExcerptSimilarity entries.")

    def get_status(self):
        """
        Get similarity analysis status.
        """

        # Check for existence of similarity analysis Job in database
        try:
            job = Job.objects.get(name="similarity_analysis")
        # If no Job exists
        except Job.DoesNotExist:
            job = None
            # return HttpResponseNotFound("No similarity analysis job found.")

        return {
            "running": self.running,
            "job": job if job else None,
            "progress": job.progress if job else None,
            "subprogress": job.subprogress if job else None,
            "total": job.total if job else None,
            "percent": round(job.progress / job.total * 100, 2) if job else None,
        }

    def stop(self):
        """
        Stop similarity analysis.
        """

        # Set running to False
        self.running = False
