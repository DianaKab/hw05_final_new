from django import forms

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        group = forms.ModelChoiceField(
            queryset=Group.objects.all(),
            to_field_name='group_name',
        )
        text = forms.CharField
        fields = ('text', 'group', 'image')
        labels = {
            'text': "Текст поста",
            'group': "Группа"
        }
        help_texts = {
            'text': "Текст нового поста",
            'group': "Группа, к которой будет относиться пост"
        }
        widgets = {
            'text': forms.Textarea(attrs={'cols': 150, 'row': 100, })
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        text = forms.CharField
        fields = ('text',)
