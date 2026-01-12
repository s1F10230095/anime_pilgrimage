from django import forms
from .models import Post # <-- ここに Profile を追加

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'image']  # モデルに存在するフィールド名に合わせる

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['spot', 'text', 'image']
