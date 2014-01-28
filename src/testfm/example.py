__author__ = 'linas'

import pandas as pd
import numpy as np
import testfm
from testfm.evaluation.evaluator import Evaluator
from testfm.models.baseline_model import Popularity, RandomModel, IdModel
from testfm.models.ensemble_models import LinearEnsemble
from testfm.models.tensorCoFi import TensorCoFi, TensorCoFiByFile
from testfm.models.content_based import LSIModel
from pkg_resources import resource_filename

#prepare the data
df = pd.read_csv(resource_filename(testfm.__name__,'data/movielenshead.dat'),
    sep="::", header=None, names=['user', 'item', 'rating', 'date', 'title'])
print df.head()
training, testing = testfm.split.holdoutByRandomFast(df, 0.9)

print len(training), len(testing)
#tell me what models we want to evaluate
models = [RandomModel(),
            Popularity(),
            IdModel(),
            #LinearEnsemble([RandomModel(), Popularity()], weights=[0.5, 0.5]),
            #LSIModel('title'),
            #TensorCoFi(),
            TensorCoFiByFile()
          ]

#evaluate
items = training.item.unique()
evaluator = Evaluator()

print "\n\n Multiprocessing"
for m in models:
    m.fit(training)
    print m.getName().ljust(50), \
        list(evaluator.evaluate_model_multiprocessing(m,
            testing, all_items=items))

print "\n\nMultithread"
for m in models:
    m.fit(training)
    print m.getName().ljust(50), \
        list(evaluator.evaluate_model(m, testing, all_items=items))
