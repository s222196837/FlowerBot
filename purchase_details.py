import pandas as pd
import random
import time

class PurchaseDetails:
    def __init__(
        self,
        user: str = None,
        item: str = None,
        datetime: str = None,
        supported_flowers = None,
        unsupported_flowers = None,
    ):
        total_users = 128 # max
        if user is None:
            user = str(random.randint(1, total_users))
        self.user = user

        self.item = item

        if datetime is None:
            datetime = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
        self.datetime = datetime

        if supported_flowers is None:
           supported_flowers = self.load_catalog()
        self.supported_flowers = supported_flowers

        if unsupported_flowers is None:
            unsupported_flowers = ['dandelion'] # weed
        self.unsupported_flowers = unsupported_flowers

    def load_catalog(self):
        """ get plant identifiers from the catalog, returns dictionary """
        flowers = 'data/flowers.catalog'
        columns = ['item', 'name', 'group']
        catalog = pd.read_csv(flowers, header=None, names=columns)
        catalog = pd.DataFrame(catalog, columns=['item', 'name'])
        catalog = dict([(n,i) for n, i in zip(catalog.name, catalog.item)])
        return catalog

    def item_catalog(self, flower):
        """ lookup a flower in the catalog dictionary, returns item ID """
        if flower not in self.supported_flowers:
            return None
        return self.supported_flowers[flower]
