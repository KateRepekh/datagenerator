from django.urls import path
from fakecsv import views

app_name = 'fakecsv'
urlpatterns = [
    path('', views.SchemaListView.as_view()),
    path('schemas', views.SchemaListView.as_view(), name='schemas'),
    path('schema/<int:pk>', views.SchemaDetailView.as_view(),
         name='schema_detail'),
    path('schema/create', views.SchemaCreateView.as_view(),
         name='schema_create'),
    path('schema/<int:pk>/delete', views.SchemaDeleteView.as_view(),
         name='schema_delete'),
    path('dataset/<int:pk>', views.DatasetDownloadView.as_view(),
         name='dataset_download'),
]
