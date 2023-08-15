from barton_link import barton_link

from ..models import Excerpt,\
    ExcerptAutoTag,\
    Tag,\
    Job

from .service import Service

class AutotagService(Service):
    """
    Service for autotagging excerpts.
    """

    def __init__(self):
        super().__init__("autotag")

    def run(self):
        job = self.get_job()

        if job == None:
            job = Job.objects.create(
                name="autotag",
                total=Excerpt.objects.count(),
            )

        current_progress = job.progress
        # tag_index = job.subprogress

        # Get all excerpts, order by ascending id
        #@TODO optimization; is Django loading all excerpts into memory?
        excerpts = Excerpt.objects.order_by("id")[current_progress:]

        # If url is /autotag/<excerpt_id>
        # if excerpt_id:
        #     # Get excerpt with id
        #     excerpts = Excerpt.objects.filter(id=excerpt_id)

        #     # If no excerpt with id
        #     if len(excerpts) == 0:
        #         # Return 404
        #         return HttpResponseNotFound()

        # # If url is simply /autotag
        # else:
        #     # Get all excerpts, order by ascending id
        #     excerpts = Excerpt.objects.order_by("id")[:10]
        #     # excerpts = Excerpt.objects.order_by("id")

        # Build list of excerpt texts
        # excerpt_texts = [excerpt.content for excerpt in excerpts]

        # Get all existing tags
        tags = Tag.objects.all()
        tag_names = [tag.name for tag in tags]

        # Semantically compare excerpts to tags
        print(f"Comparing {len(excerpts)} excerpts to {len(tags)} tags...")
        # scores = barton_link.compare_lists_sbert(excerpt_texts, tag_names)

        for excerpt in excerpts:
            # autotag_obj = {
            #     "excerpt": excerpt,
            #     "tag_scores": [],
            # }

            # Update job progress
            job.progress = excerpt.id
            job.save()

            # Measure similarities between excerpt and tags
            #@TODO only score unscored tags
            tag_scores = barton_link.compare_lists_sbert([excerpt.content],
                                                         tag_names)

            for j, tag in enumerate(tags):
                # If service is no longer running
                if self.running == False:
                    return

                # If tag is already on excerpt
                # if tag in excerpt.tags.all():
                #     continue

                # sbert_score = scores[i][j]
                sbert_score = tag_scores[0][j]

                # If score exceeds threshold
                #@REVISIT do we want negative scores?
                if sbert_score >= 0.5 or sbert_score <= -0.5:
                    print(f"Excerpt {excerpt.id} is similar to tag {tag.id} " \
                            + f"with score {sbert_score}")

                    # Check if autotag entry already exists
                    autotag = ExcerptAutoTag.objects.filter(
                        excerpt=excerpt,
                        tag=tag,
                    ).first()

                    # If autotag entry already exists
                    if autotag:
                        # Update score
                        autotag.sbert_similarity = sbert_score
                        autotag.save()

                    # If autotag entry does not exist
                    else:
                        # Create autotag entry
                        autotag = ExcerptAutoTag(
                            excerpt=excerpt,
                            tag=tag,
                            sbert_similarity=sbert_score,
                        )
                        autotag.save()
