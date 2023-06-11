from django.db import models

class Tag(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.TextField()
    description = models.TextField()

    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name

class Character(models.Model):
    name = models.TextField()
    description = models.TextField()

    projects = models.ManyToManyField(Project)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name

class Excerpt(models.Model):
    excerpt = models.TextField()

    tags = models.ManyToManyField(Tag)
    characters = models.ManyToManyField(Character)
    projects = models.ManyToManyField(Project)

    metadata = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def unused_tags(self):
        return Tag.objects.exclude(excerpt__id=self.id)

    def unused_projects(self):
        return Project.objects.exclude(excerpt__id=self.id)

    def __str__(self):
        return self.excerpt

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
