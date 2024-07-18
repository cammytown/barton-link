from datetime import datetime
from django.db import models

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super(SoftDeleteManager, self).get_queryset().filter(is_deleted=False)

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True) #@ do we care?

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.save()

    class Meta:
        abstract = True

class TagType(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name

class Tag(SoftDeleteModel):
    name = models.TextField()
    description = models.TextField()

    #@REVISIT on_delete i think is wrong:
    type = models.ForeignKey(TagType,
                             on_delete=models.CASCADE,
                             default=1,
                             related_name="tags")

    def __str__(self):
        return self.name

class RelationshipType(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name

class EntityRelationship(models.Model):
    # RELATIONSHIP_CHOICES = {
    #     "IS": "is",
    #     "HAS": "has",
    #     "CONTAINS": "contains",
    #     "PART_OF": "part of",
    # }

    entity_a = models.ForeignKey('Entity',
                                    on_delete=models.CASCADE,
                                    related_name='entity_a')

    entity_b = models.ForeignKey('Entity',
                                    on_delete=models.CASCADE,
                                    related_name='entity_b')

    relationship_type = models.ForeignKey('RelationshipType',
                                            on_delete=models.CASCADE)

    description = models.TextField()

    def __str__(self):
        return f"{self.entity_a} - {self.entity_b}: {self.relationship_type}"

class Entity(SoftDeleteModel):
    # ENTITY_TYPES = {
    #     "CHARACTER": "character",
    #     "PLACE": "place",
    #     "OBJECT": "object",
    #     # "EVENT": "event",
    #     # "OTHER": "other",
    # }

    name = models.TextField()

    description = models.TextField()

    tags = models.ManyToManyField(Tag)

    relationships = models.ManyToManyField('self',
                                            through='EntityRelationship',
                                            symmetrical=False,
                                            related_name='related_entities')

    def __str__(self):
        return self.name

class ExcerptTag(models.Model):
    excerpt = models.ForeignKey('Excerpt', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    is_autotag = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.excerpt} - {self.tag}"

class ExcerptRelationship(models.Model):
    parent = models.ForeignKey('Excerpt',
                               on_delete=models.CASCADE,
                               related_name='parent')
    child = models.ForeignKey('Excerpt',
                              on_delete=models.CASCADE,
                              related_name='child')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parent} - {self.child}"

class Excerpt(SoftDeleteModel):
    content = models.TextField()

    tags = models.ManyToManyField(Tag,
                                  through='ExcerptTag',
                                  related_name='excerpts')

    entities = models.ManyToManyField(Entity)
    
    parents = models.ManyToManyField('self',
                                     through='ExcerptRelationship',
                                     symmetrical=False,
                                     related_name='children')

    metadata = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def unused_tags(self):
        """
        Return all tags that are not associated with this excerpt.
        """

        return Tag.objects.exclude(excerpttag__excerpt=self)

    def similar_excerpts(self):
        """
        Return all ExcerptSimilarity objects that include this excerpt.
        """

        # Retrieve all ExcerptSimilarity objects that include this excerpt
        similarity_objects = ExcerptSimilarity.objects.filter(excerpt1=self) \
            | ExcerptSimilarity.objects.filter(excerpt2=self)

        # Order by similarity
        similarity_objects = similarity_objects.order_by('-sbert_similarity')

        similarities = []

        # For each matching similarity
        for similarity in similarity_objects:
            excerpt = None

            # Add the other excerpt to the list
            if similarity.excerpt1 == self:
                excerpt = similarity.excerpt2
            else:
                excerpt = similarity.excerpt1

            similarities.append({
                'excerpt': excerpt,
                'sbert_similarity': similarity.sbert_similarity,
                # 'spacy_similarity': similarity.spacy_similarity
            })

        return similarities

    def save(self, *args, **kwargs):
        super(Excerpt, self).save(*args, **kwargs)

        # Create version if this is a new excerpt
        #@REVISIT placement
        if not self.versions.exists():
            ExcerptVersion.objects.create(excerpt=self, content=self.content)

    def __str__(self):
        return self.content

class ExcerptVersion(models.Model):
    excerpt = models.ForeignKey(Excerpt,
                                on_delete=models.CASCADE,
                                related_name='versions')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.excerpt} - {self.created}"

class ExcerptSimilarity(models.Model):
    excerpt1 = models.ForeignKey(Excerpt,
                                 on_delete=models.CASCADE,
                                 related_name='excerpt1')
    excerpt2 = models.ForeignKey(Excerpt,
                                 on_delete=models.CASCADE,
                                 related_name='excerpt2')

    sbert_similarity = models.FloatField()
    # spacy_similarity = models.FloatField()

    def __str__(self):
        return f"{self.excerpt1} - {self.excerpt2}: {self.sbert_similarity}"

class ExcerptAutoTag(models.Model):
    excerpt = models.ForeignKey(Excerpt,
                                on_delete=models.CASCADE,
                                related_name='autotags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    sbert_similarity = models.FloatField()

    def __str__(self):
        return f"{self.excerpt} - {self.tag}: {self.sbert_similarity}"

class Concept(models.Model):
    # name = models.TextField()
    description = models.TextField()

    # type

    # def __str__(self):
    #     return self.name

class Job(models.Model):
    name = models.TextField()
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    progress = models.IntegerField(default=0)
    subprogress = models.IntegerField(default=0)
    total = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# class BartonConfig:
#     id = models.IntegerField(primary_key=True)
#     name = models.TextField()
#     value = models.TextField()


