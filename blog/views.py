from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, View, FormView

from blog.forms import CommentForm
from blog.models import Post, PostVote


class IndexView(TemplateView):
    template_name = 'blog/post_list.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        posts = Post.objects.filter(is_important=True, is_post=True, is_published=True)\
            .select_related('author')\
            .order_by('-id')
        paginator = Paginator(posts, settings.POSTS_PER_PAGE)
        posts = paginator.get_page(self.request.GET.get('page'))
        votes = {i.post_id: i for i in PostVote.objects.filter(post__in=posts, user_id=self.request.user.id)}

        for post in posts:
            if post.id in votes:
                post.voted = votes[post.id].delta

        context['posts'] = posts
        return context


class PostView(FormView):
    template_name = 'blog/post_detail.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'), is_post=True, is_published=True)
        comments = post.get_descendants().filter(is_published=True).select_related('author').all()

        vote = PostVote.objects.filter(post_id=post.id, user_id=self.request.user.id)
        if vote.exists():
            post.voted = vote[0].delta

        votes = {i.post_id: i for i in PostVote.objects.filter(post__in=comments, user_id=self.request.user.id)}
        for comment in comments:
            if comment.id in votes:
                comment.voted = votes[comment.id].delta

        context['post'] = post
        context['comments'] = comments
        return context

    def get_form_kwargs(self):
        kwargs = super(PostView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(self.request.get_full_path())


class AjaxVoteView(View, ):
    ACTIONS = {
        'upvote': 1,
        'downvote': -1,
        'retract': 0
    }

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, is_published=True)
        action = request.GET.get('action')
        if action not in AjaxVoteView.ACTIONS or not request.user.is_authenticated:
            raise PermissionDenied
        post.vote(request.user.id, AjaxVoteView.ACTIONS[action])
        return HttpResponse(status=204)
