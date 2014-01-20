# -*- coding: utf-8 -*-
'''
Created on 20 January 2014

Evaluation measures for the list wise (i.e., precision) and point wise (i.e., RMSE) recommendations.
All of the measures will get a SORTED list of items with ground truth for the user and will
compute their measures based on it.

The error measure gets a SORTED (descending order or prediction) list. The 0 element of the list
 has highest prediction and is top of the recommendation list. The ground true can be either
 float or the boolean. If it is float, it means the rating and the relevance threshold should be provided in order
 to compute the ranking measure. If it is boolean, True=relevant, False=irrelevant.
[(True, 0.9), (False, 0.55), (True, 0.4), (True, 0.2)]

Now we can compute the ranking error measure. For example Precision@2 = 0.5.

.. moduleauthor:: linas <linas.baltrunas@gmail.com>
'''

__author__ = 'linas'

class Measure(object):

    def measure(self, recs):
        '''
        Each class of the Measure has to implement this method. It basically knows how to compute the
        performance measure such as MAP, P@k, etc.

        recs - a list of tuples of ground truth and score.
            Example: [(True, 0.92), (False, 0.55), (True, 0.41), (True, 0.2)]
        '''
        raise NotImplementedError

class MAP_measure(Measure):
    '''
    Implementation of Mean Average Precision.
    '''

    def measure(self, recs):
        '''
        Example of how to use map and the input format.
        >>> map = MAP_measure()
        >>> map.measure([])
        nan

        >>> map.measure([(True, 0.00)]) #this is a perfect ranking of a single relevant item
        1.0

        >>> map.measure([(False, 0.00)])
        0.0

        >>> map.measure([(False, 0.01), (True, 0.00)])
        0.5

        The following example is taken from wikipedia (as far as I remember)
        >>> map.measure([(False, 0.9), (True, 0.8), (False, 0.7), (False, 0.6), (True, 0.5), \
        (True, 0.4), (True, 0.3), (False, 0.2), (False, 0.1), (False, 0)])
        0.4928571428571428
        '''

        if not recs or not isinstance(recs, list) or len(recs) < 1:
            return float('nan')

        map = 0.0
        relevant = 0.0

        for i, r in enumerate(recs):
            ground_truth, prediction = r
            if isinstance(ground_truth, bool) and ground_truth is True:
                relevant += 1
                map += relevant / (i+1)
        if relevant == 0:
            return 0.0
        else:
            return map/relevant


class Precision_measure(Measure):

    def measure(self, recs):
        '''
        Example of map:
        >>> p = Precision_measure()
        >>> p.measure([])
        nan

        >>> p.measure([(True, 0.00)])
        1.0

        >>> p.measure([(False, 0.00)])
        0.0

        >>> p.measure([(False, 0.01), (True, 0.00)])
        0.5

        >>> p.measure([(False, 0.9), (True, 0.8), (False, 0.7), (False, 0.6), (True, 0.5), \
        (True, 0.4), (True, 0.3), (False, 0.2), (False, 0.1), (False, 0)])
        0.4
        '''

        map = 0.0
        relevant = 0.0

        if not recs or not isinstance(recs, list) or len(recs) < 1:
            return float('nan')
        #compute number of relevant items in the list
        relevant = float(len([gt for gt, _ in recs if gt]))

        if relevant == 0:
            return 0.0
        else:
            return relevant/len(recs)

if __name__ == '__main__':
    '''
    For Testing this code I will use doctests as the code is quite minimalistic
    '''
    import doctest
    doctest.testmod()
