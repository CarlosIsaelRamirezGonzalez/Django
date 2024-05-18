from django.shortcuts import render
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from taggit.models import Tag
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False) # commit=False hace que no se guarde en la base de datos
        # Assign the post to the comment
        comment.post = post
        # Save in the database
        comment.save()
        
    return render(request, 'blog_app/post/comment.html', 
                            {'post': post,
                             'form': form, 
                             'comment': comment})
        

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST) # Obtenemos los valores del form que el usuario manda
        if form.is_valid():
            cleaned_data = form.cleaned_data # only the data that is valid
            post_url = request.build_absolute_uri(post.get_absolute_url()) # request.build_absolute_uri build a complete url incluiding the http schema and hostname    
            subject = f"{cleaned_data['name']} recommends you read {post.title}"
            message = f"Read {post.title} ar {post_url} \n\n {cleaned_data['name']}\'s comments: {cleaned_data['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER , [cleaned_data['to']])
            sent = True
    else:
        form = EmailPostForm()
    
    return render(request, 'blog_app/post/share.html', {'post': post,
                                                        'form': form, 
                                                        'sent': sent})        


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        
    
    # Pagination with 3 post per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1) # if the page parameter is not in GET we use the default value 1
    try:   
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver the last poge of results
        posts = paginator.page(paginator.num_pages)
        
    return render(request, 'blog_app/post/list.html', {'posts': posts})

# CBVs (Class based view)
class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = "posts" # Of that way we defined posts as the result from queryset attribute, instead of object_list that is the default.
    paginate_by = 3
    template_name = 'blog_app/post/list.html'
    
    
    


# FBVs (Function based view)
def post_detail(request, year, month, day, post ):
    # try: 
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No post found.")
    post = get_object_or_404(Post, 
                             status = Post.Status.PUBLISHED,
                             slug = post,
                             publish__year = year, 
                             publish__month = month,
                             publish__day = day)
    
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    
    
    return render(request, 'blog_app/post/detail.html', {'post':post,
                                                         'comments': comments,
                                                         'form': form,})