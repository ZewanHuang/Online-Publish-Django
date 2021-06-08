## OPS Backend

### 部署过程

将 django3/urls.py 中修改为

```python
urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include(('user.urls', 'user'), namespace="user")),
    path('api/', include(('author_review.urls', 'author_review'), namespace="author_review")),
]
```

将 django3/settings.py 中修改为

```python
WEB_ROOT = 'https://zewan.top/api'
```