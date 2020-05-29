from haystack.indexes import SearchIndex, Indexable, CharField
from .models import User
class UserSearchIndex(SearchIndex, Indexable):
    text = CharField(document=True, use_template=True)
    def get_model(self):
        return User
def index_queryset(self, using=None):
    return self.get_model().objects.all()