from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError

from blog.models import Post


class CommentForm(forms.Form):
    parent_id = forms.IntegerField(widget=forms.HiddenInput())
    comment_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    text = forms.CharField(widget=forms.Textarea(), required=True)

    def __init__(self, user=None, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.user = user

    def clean_comment_id(self):
        comment_id = self.cleaned_data['comment_id']
        if not comment_id:
            return None
        comment = Post.objects.filter(id=comment_id)
        if not comment.exists() or comment[0].author_id != self.user.id:
            raise ValidationError("Cannot edit this comment")
        return comment_id

    def clean_parent_id(self):
        parent_id = self.cleaned_data['parent_id']
        if not Post.objects.filter(id=parent_id).exists():
            raise ValidationError("Parent post/comment does not exist")
        return parent_id

    def save(self):
        id = self.cleaned_data['comment_id']
        parent_id = self.cleaned_data['parent_id']
        contents = self.cleaned_data['text']
        kw = dict(author_id=self.user.id,
                  contents=contents, is_published=True,
                  is_post=False, parent_id=parent_id)
        if id:
            comment = Post.objects.get(pk=id)
            comment.contents = contents
            comment.save()
        else:
            comment = Post(**kw)
            comment.save()
