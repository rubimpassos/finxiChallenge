from django.test.runner import DiscoverRunner


class PytestTestRunner(DiscoverRunner):
    """Runs pytest through managet test command"""

    def __init__(self, verbosity=1, failfast=False, keepdb=False, nomigration=False, summary=False, **kwargs):
        super(PytestTestRunner, self).__init__(**kwargs)
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb
        self.nomigration = nomigration
        self.summary = summary

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--summary', action='store_true', dest='summary',
            help='Show in summary failed and skipped tests',
        )
        parser.add_argument(
            '--nomigration', action='store_true', dest='nomigration',
            help='Skip migrations',
        )

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        """Run pytest and return the exitcode.

        It translates some of Django's test command option to pytest's.
        """
        import pytest

        argv = []
        if self.verbosity == 0:
            argv.append('--quiet')
        if self.verbosity == 2:
            argv.append('--verbose')
        if self.verbosity == 3:
            argv.append('-vv')
        if self.failfast:
            argv.append('--exitfirst')
        if self.keepdb:
            argv.append('--reuse-db')
        if self.nomigration:
            argv.append('--nomigration')
        if self.summary:
            argv += ['-r', 'sx']

        argv.extend(test_labels)
        return pytest.main(argv)
