from django.urls import path
from . import views

app_name = 'gitapp'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('repository_list/', views.repository_list, name='repos'),
    path('logout/', views.logout_page, name='logout'),
    path('<name>/reposit_details/', views.reposit_details, name='repos_details'),
    path('<name>/data/', views.data, name='data'),
    path('<name>/create_branch/', views.create_branch, name='create_branch'),
    path("<name>/file/", views.file, name="file"),
    path("<name>/file_details/", views.file_details, name='file_details'),
    path("<name>/pull_request/", views.pull_req, name="pull_req"),
    path("<name>/pull_details/", views.pull_details, name="pull_details"),
    path("<name>/merging/", views.merging, name="merging"),
    path("<name>/merge/", views.merge, name="merge"),
    path("<name>/del_branch/", views.del_branch, name="del_branch"),
    path("<name>/delete/", views.delete, name="delete"),
]
