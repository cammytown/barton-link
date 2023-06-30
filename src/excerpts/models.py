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

class Character(SoftDeleteModel):
    name = models.TextField()
    description = models.TextField()

    tags = models.ManyToManyField(Tag)

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

    characters = models.ManyToManyField(Character)
    
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

    # def save(self, *args, **kwargs):
    #     super(Excerpt, self).save(*args, **kwargs)

    #     # Create version if this is a new excerpt
    #     if not self.versions.exists():
    #         ExcerptVersion.objects.create(excerpt=self, content=self.content)

    def __str__(self):
        return self.content

class ExcerptVersion(models.Model):
    excerpt = models.ForeignKey(Excerpt, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.excerpt} - {self.created}"

class ExcerptSimilarity(models.Model):
    excerpt1 = models.ForeignKey(Excerpt, on_delete=models.CASCADE, related_name='excerpt1')
    excerpt2 = models.ForeignKey(Excerpt, on_delete=models.CASCADE, related_name='excerpt2')

    sbert_similarity = models.FloatField()
    # spacy_similarity = models.FloatField()

    def __str__(self):
        return f"{self.excerpt1} - {self.excerpt2}: {self.similarity}"

# class BartonConfig:
#     id = models.IntegerField(primary_key=True)
#     name = models.TextField()
#     value = models.TextField()
