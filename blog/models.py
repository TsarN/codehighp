from django.db import models
from django.db.transaction import atomic
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from users.models import CustomUser


class PostVote(models.Model):
    class Meta:
        unique_together = (('post', 'user'),)

    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    delta = models.SmallIntegerField(default=0)


class Post(MPTTModel):
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True)
    title = models.CharField(max_length=255, default=None, blank=True, null=True)
    contents = models.TextField(default='')
    is_important = models.BooleanField(default=False, blank=True, db_index=True)
    is_published = models.BooleanField(default=True, blank=True, db_index=True)
    is_post = models.BooleanField(default=True, blank=True, db_index=True)
    rating = models.IntegerField(default=0)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        if self.is_post:
            return "Post '{}'".format(self.title)
        else:
            return "Comment by {} on {}".format(self.author, self.created_date)

    @atomic
    def vote(self, user_id, delta):
        vote, created = PostVote.objects.get_or_create(post_id=self.id, user_id=user_id)
        if created or vote.delta != delta:
            self.rating += delta - vote.delta
            vote.delta = delta
            vote.save()
            self.save()

    @property
    def cut_contents(self):
        return self.contents.split("[cut]")[0]

    @property
    def has_cut(self):
        return "[cut]" in self.contents

    @property
    def full_contents(self):
        return self.contents.replace("[cut]", "")
