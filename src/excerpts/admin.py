from django.contrib import admin
from .models import Dataset, Excerpt, Tag, TagType, Entity, ExcerptSimilarity, Job

# Register your models here.
admin.site.register(Dataset)
admin.site.register(Excerpt)
admin.site.register(Tag)
admin.site.register(TagType)
admin.site.register(Entity)
admin.site.register(ExcerptSimilarity)
admin.site.register(Job)
