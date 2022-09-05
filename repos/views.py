from rest_framework import viewsets

from .models import Repo
from .serializers import RepoSerializer

class RepoViewSet(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer