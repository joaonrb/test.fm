__author__ = "mumas"

import unittest
from math import sqrt

from testfm.evaluation.evaluator import Evaluator, MAPMeasure
from testfm.models.baseline_model import ConstantModel, IdModel
from testfm.models.tensorcofi import PyTensorCoFi
import pandas as pd


class TestEvaluator(unittest.TestCase):

    def test_rmse(self):
        eval = Evaluator()

        model = ConstantModel(constant=3.0)
        testing = pd.DataFrame([{"user": 10, "item": 100, "rating": 3},
                                {"user": 10, "item": 110, "rating": 1},
                                {"user": 12, "item": 100, "rating": 4}])
        rmse = eval.evaluate_model_rmse(model, testing)
        self.assertEqual(sqrt((0+4+1)/3.0), rmse)

    def test_default(self):
        mapm = MAPMeasure()
        model = IdModel()
        evaluation = Evaluator()
        df = pd.DataFrame({"user": [1, 1, 3, 4], "item": [1, 2, 3, 4], "rating": [5, 3, 2, 1],
                           "date": [11, 12, 13, 14]})
        e = evaluation.evaluate_model(model, df, non_relevant_count=2, measures=[mapm])
        assert len(e) == 1, "Evaluator result is not what is expected"
        #r = mapm.measure([])
        #assert not r, "MAPMeasure for empty list is not returning NAN (%f, %s)" % (r, type(r))
        r = mapm.measure([(True, 0.)])
        assert r == 1., "MAPMeasure for 1 entry (True, 0.) list is not returning 1. (%f)" % r
        r = mapm.measure([(False, 0.)])
        assert r == 0., "MAPMeasure for 1 entry (False, 0.) list is not returning 0. (%f)" % r
        r = mapm.measure([(False, 0.01), (True, 0.00)])
        assert r == 0.5, "MAPMeasure for 2 entries (False, 0.01) and (True, 0.) list is not returning 0.5 (%f)" % r
        r = mapm.measure([(False, 0.9), (True, 0.8), (False, 0.7), (False, 0.6), (True, 0.5), (True, 0.4), (True, 0.3), 
                          (False, 0.2), (False, 0.1), (False, 0)])
        assert r == 0.4928571428571428, "Measure should be around 0.4928571428571428 (%f)" % r

    def test_nogil_against_std(self):
        import testfm
        from pkg_resources import resource_filename
        import numpy as np
        from scipy.stats import f as F
        from tabulate import tabulate
        df = pd.read_csv(resource_filename(testfm.__name__, 'data/movielenshead.dat'),
                         sep="::", header=None, names=['user', 'item', 'rating', 'date', 'title'])
        model = PyTensorCoFi()
        ev = Evaluator(False)
        ev_nogil = Evaluator()
        results = {"nogil": [], "measure": []}
        for i in range(5):
            training, testing = testfm.split.holdoutByRandom(df, 0.5)
            model.fit(training)
            results["nogil"].append(1), results["measure"].append(ev_nogil.evaluate_model(model, testing)[0])
            results["nogil"].append(0), results["measure"].append(ev.evaluate_model(model, testing)[0])

        #####################
        # ANOVA over result #
        #####################
        data = pd.DataFrame(results)
        means_models = data.groupby("nogil").agg({"measure": np.mean})["measure"]
        grand_mean = data["measure"].mean()

        n = len(data)
        n_models = len(means_models)

        # Degrees of freedom
        df_models = n_models - 1  # Numerator
        df_error = n - n_models  # Denominator
        df_total = df_models + df_error

        # Sum of Squares
        ss_total = sum(data["measure"].map(lambda x: (x-grand_mean)**2))
        ss_error = sum(data.apply(lambda x: (x["measure"]-means_models[x["nogil"]])**2, axis=1))
        #ss_models = ss_total - ss_error
        ss_models = sum(means_models.map(lambda x: (x-grand_mean)**2)*(n/n_models))

        # Mean Square (Variance)
        ms_models = ss_models / df_models
        ms_error = ss_error / df_error

        # F Statistic
        f = ms_models / ms_error

        p = 1. - F.cdf(f, df_models, df_error)
        alpha = 0.05
        assert p >= alpha, "Theres is statistic evidence to confirm that the measure and the std measure is " \
                           "quite diferent:\n %s\n\nANOVA table\n%s" % (data, tabulate([
            ["Source of Variation", "DF", "SS", "MS", "F", "p-value"],
            ["Model", "%d" % df_models, "%.4f" % ss_models, "%.4f" % ms_models, "%.4f" % f, "%.4f" % p],
            ["Error", "%d" % df_error, "%.4f" % ss_error, "%.4f" % ms_error, "", ""],
            ["Total", "%d" % df_total, "%.4f" % ss_total, "", "", ""]
        ]))
