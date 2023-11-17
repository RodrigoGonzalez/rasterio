"""Implementation of Apache VFS schemes and URLs."""

import os

from rasterio.compat import urlparse


# NB: As not to propagate fallacies of distributed computing, Rasterio
# does not support HTTP or FTP URLs via GDAL's vsicurl handler. Only
# the following local filesystem schemes are supported.
SCHEMES = {'gzip': 'gzip', 'zip': 'zip', 'tar': 'tar', 'https': 'curl',
           'http': 'curl', 's3': 's3'}


def parse_path(uri, vfs=None):
    """Parse a URI or Apache VFS URL into its parts

    Returns: tuple
        (path, archive, scheme)
    """
    archive = scheme = None
    path = uri
    if vfs:
        parts = urlparse(vfs)
        scheme = parts.scheme
        archive = parts.path
        if parts.netloc and parts.netloc != 'localhost':  # pragma: no cover
            archive = parts.netloc + archive
    else:
        parts = urlparse(path)
        scheme = parts.scheme
        path = parts.path
        if parts.netloc and parts.netloc != 'localhost':
            path = parts.netloc + path
        # There are certain URI schemes we favor over GDAL's names.
        if scheme in SCHEMES:
            parts = path.split('!')
            path = parts.pop() if parts else None
            archive = parts.pop() if parts else None
        elif scheme not in (None, '', 'file'):
            archive = scheme = None
            path = uri

    return path, archive, scheme


def vsi_path(path, archive=None, scheme=None):
    """Convert a parsed path to a GDAL VSI path."""
    # If a VSF and archive file are specified, we convert the path to
    # a GDAL VSI path (see cpl_vsi.h).
    if scheme and scheme.startswith('http'):
        return "/vsicurl/{0}://{1}".format(scheme, path)
    elif scheme and scheme == 's3':
        return "/vsis3/{0}".format(path)
    elif scheme and scheme != 'file':
        return (
            '/vsi{0}/{1}/{2}'.format(scheme, archive, path.lstrip('/'))
            if archive
            else '/vsi{0}/{1}'.format(scheme, path.lstrip('/'))
        )
    else:
        return path
