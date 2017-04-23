import re
import unittest

import mock
import numpy
import six

import chainer
from chainer import testing
from chainer.training import extensions


@testing.parameterize(
    {'statistics': {'min': numpy.min},
     'links': chainer.links.Linear(10, 10),
     'expect': 4},
    {'statistics': {'mean': numpy.mean, 'std': numpy.std},
     'links': chainer.links.Linear(10, 10),
     'expect': 8},
    {'statistics': extensions.ParameterStatistics.default_statistics,
     'links': chainer.links.Linear(10, 10),
     'expect': 48},
    {'statistics': {},
     'links': chainer.links.Linear(10, 10),
     'expect': 0}
)
class TestParameterStatistic(unittest.TestCase):

    def setUp(self):
        self.trainer = mock.MagicMock()
        self.reporter = chainer.Reporter()

    def test_report(self):
        extension = extensions.ParameterStatistics(self.links,
                                                   statistics=self.statistics)
        with self.reporter:
            extension(self.trainer)
            self.assertEqual(len(self.reporter.observation), self.expect)

    def test_report_late_register(self):
        extension = extensions.ParameterStatistics(self.links, statistics={})
        for name, function in six.iteritems(self.statistics):
            extension.register_statistics(name, function)
        with self.reporter:
            extension(self.trainer)
            self.assertEqual(len(self.reporter.observation), self.expect)

    def test_report_key_pattern(self):
        extension = extensions.ParameterStatistics(self.links)
        pattern = r'^(.+/){2,}(data|grad)/.+[^/]$'
        with self.reporter:
            extension(self.trainer)
            for name in six.iterkeys(self.reporter.observation):
                self.assertTrue(re.match(pattern, name))


@testing.parameterize(
    {'statistics': {'one': lambda x: 1.0},
     'links': chainer.links.Linear(10, 10),
     'expect': 1.0}
)
class TestParameterStatisticsCustomFunction(unittest.TestCase):

    def setUp(self):
        self.trainer = mock.MagicMock()
        self.reporter = chainer.Reporter()
        self.extension = extensions.ParameterStatistics(
            self.links, statistics=self.statistics)

    def test_custom_function(self):
        with self.reporter:
            self.extension(self.trainer)
            for value in six.itervalues(self.reporter.observation):
                self.assertEqual(value, self.expect)


@testing.parameterize(
    {'statistics': extensions.ParameterStatistics.default_statistics,
     'links': chainer.links.Linear(10, 10)}
)
class TestParameterStatisticsArguments(unittest.TestCase):

    def setUp(self):
        self.trainer = mock.MagicMock()
        self.reporter = chainer.Reporter()

    def test_skip_params(self):
        extension = extensions.ParameterStatistics(
            self.links, statistics=self.statistics, report_params=False)
        with self.reporter:
            extension(self.trainer)
            for name in six.iterkeys(self.reporter.observation):
                self.assertIn('grad', name)
                self.assertNotIn('data', name)

    def test_skip_grads(self):
        extension = extensions.ParameterStatistics(
            self.links, statistics=self.statistics, report_grads=False)
        with self.reporter:
            extension(self.trainer)
            for name in six.iterkeys(self.reporter.observation):
                self.assertIn('data', name)
                self.assertNotIn('grad', name)

    def test_report_key_prefix(self):
        extension = extensions.ParameterStatistics(
            self.links, statistics=self.statistics, prefix='prefix')
        with self.reporter:
            extension(self.trainer)
            for name in six.iterkeys(self.reporter.observation):
                self.assertTrue(name.startswith('prefix'))


testing.run_module(__name__, __file__)