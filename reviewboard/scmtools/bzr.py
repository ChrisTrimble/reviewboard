import calendar
from datetime import datetime, timedelta
import os
import time
import urlparse

try:
    from bzrlib import bzrdir, config, revisionspec
    from bzrlib.errors import NotBranchError
except ImportError:
    pass

from reviewboard.scmtools import sshutils
from reviewboard.scmtools.core import SCMTool, PRE_CREATION
from reviewboard.scmtools.errors import RepositoryNotFoundError, SCMError


# Register these URI schemes so we can handle them properly.
urlparse.uses_netloc.append('bzr+ssh')
urlparse.uses_netloc.append('bzr')
sshutils.ssh_uri_schemes.append('bzr+ssh')


# BZRTool: An interface to Bazaar SCM Tool (http://bazaar-vcs.org/)

class BZRTool(SCMTool):
    name = "Bazaar"
    dependencies = {
        'modules': ['bzrlib'],
    }

    # Timestamp format in bzr diffs.
    # This isn't totally accurate: there should be a %z at the end.
    # Unfortunately, strptime() doesn't support %z.
    DIFF_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

    # "bzr diff" indicates that a file is new by setting the old
    # timestamp to the epoch time.
    PRE_CREATION_TIMESTAMP = '1970-01-01 00:00:00 +0000'

    def __init__(self, repository):
        SCMTool.__init__(self, repository)

    def get_file(self, path, revision):
        if revision == BZRTool.PRE_CREATION_TIMESTAMP:
            return ''

        revspec = self._revspec_from_revision(revision)
        filepath = self._get_full_path(path)

        branch = None
        try:
            try:
                tree, branch, relpath = bzrdir.BzrDir.open_containing_tree_or_branch(filepath)
                branch.lock_read()
                fileid = tree.path2id(relpath)
                revtree = revisionspec.RevisionSpec.from_string(revspec).as_tree(branch)
                contents = revtree.get_file_text(fileid)
            except Exception, e:
                raise SCMError(e)
        finally:
            if branch:
                branch.unlock()

        return contents

    def parse_diff_revision(self, file_str, revision_str):
        if revision_str == BZRTool.PRE_CREATION_TIMESTAMP:
            return (file_str, PRE_CREATION)

        return file_str, revision_str

    def get_fields(self):
        return ['basedir', 'diff_path']

    def get_diffs_use_absolute_paths(self):
        return False

    def _get_full_path(self, path, basedir=None):
        """Returns the full path to a file."""
        parts = [self.repository.path.strip("/")]

        if basedir:
            parts.append(basedir.strip("/"))

        parts.append(path.strip("/"))

        return "/".join(parts)

    def _revspec_from_revision(self, revision):
        """Returns a revspec based on the revision found in the diff.

        In addition to the standard date format from "bzr diff", this
        function supports the revid: syntax provided by the bzr diff-revid plugin.
        """

        if revision.startswith('revid:'):
            revspec = revision
        else:
            revspec = 'date:' + str(self._revision_timestamp_to_local(revision))

        return revspec

    def _revision_timestamp_to_local(self, timestamp_str):
        """When using a date to ask bzr for a file revision, it expects
        the date to be in local time. So, this function converts a
        timestamp from a bzr diff file to local time.
        """

        timestamp = datetime(*time.strptime(timestamp_str[0:19], BZRTool.DIFF_TIMESTAMP_FORMAT)[0:6])

        # Now, parse the difference to GMT time (such as +0200)
        # If only strptime() supported %z, we wouldn't have to do this manually.
        delta = timedelta(hours=int(timestamp_str[21:23]), minutes=int(timestamp_str[23:25]))
        if timestamp_str[20] == '+':
            timestamp -= delta
        else:
            timestamp += delta

        # convert to local time
        return datetime.fromtimestamp(calendar.timegm(timestamp.timetuple()))

    @classmethod
    def check_repository(cls, path, username=None, password=None):
        """
        Performs checks on a repository to test its validity.

        This should check if a repository exists and can be connected to.
        This will also check if the repository requires an HTTPS certificate.

        The result is returned as an exception. The exception may contain
        extra information, such as a human-readable description of the problem.
        If the repository is valid and can be connected to, no exception
        will be thrown.
        """
        super(BZRTool, cls).check_repository(path, username, password)

        try:
            tree, branch, relpath = \
                bzrdir.BzrDir.open_containing_tree_or_branch(path)
        except NotBranchError, e:
            raise RepositoryNotFoundError()
        except Exception, e:
            raise SCMError(e)
