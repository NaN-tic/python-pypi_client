# The COPYRIGHT file at the top level of this repository contains the full 
# copyright notices and license terms.
"""PyPi Client"""
__author__ = 'Guillem Barba <guillem@nan-tic.com>'
__copyright__ = 'Copyright 2012 NaN Projectes de Programari Lliure, S.L.'
__license__ = 'GPL'

from datetime import datetime, timedelta
import jsonpickle
import logging
#import pprint
#import simplejson
import xmlrpclib

PYPI_XMLRPC_URL = 'http://pypi.python.org/pypi'


def configure_logger(name):
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("[%(asctime)s][%(name)s] %(levelname)s: "
            "%(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger

logger = configure_logger("pypi.client")

class PypiPackage(object):
    name = ''
    last_release = ''
    releases = None
    roles = None

    def __init__(self, name, last_release=False):
        self.name = name
        self.releases = {}
        self.roles = {}
        if last_release:
            self.last_release = last_release
            self.add_release(last_release)
            

    def __str__(self):
        ret_str = 'PypiPackage "%s"\n' % self.name
        ret_str += '    name="%s"\n' % self.name
        ret_str += '    last_release="%s"\n' % self.last_release
        if False and self.releases:
            ret_str += '    releases={\n'
            for r_version in sorted(self.releases.keys()):
                ret_str += '      \'%s\': %s\n' % (r_version,
                        self.releases[r_version].__str__().replace('\n', '\n      '))
            ret_str += '      }\n'
        else:
            ret_str += '    releases={}\n'
        if False and self.roles:
            ret_str += '    roles={\n'
            for role_item in self.roles.items():
                ret_str += '      \'%s\': %s\n' \
                        % role_item.__str__().replace('\n', '\n      ')
            ret_str += '      }'
        else:
            ret_str += '    roles={}'
        return ret_str

    def __repr__(self):
        return self.__str__()

    def update_last_release(self, release_version):
        if not release_version:
            logger.warning("update_last_release(): "
                    "empty 'release_version'")
            return False
        if not self.last_release or self.last_release < release_version:
            self.last_release = release_version
            return True
        return False

    def add_release(self, release_version):
        """
        Add an empty release to 'releases'.
        If package doesn't have 'last_release' or it is smaller than supplied
        version, updates 'last_release'
        ;return: True if release is new, otherwise False
        """
        if release_version in self.releases:
            return False
        self.releases[release_version] = PypiRelease(self.name,
                release_version)
        self.update_last_release(release_version)
        return True

    def get_local_release(self, release_version, default=None):
        if not release_version:
            logger.error("get_local_release(): empty required "
                    "'release_version' parameter")
            return False
        if release_version in self.releases:
            return self.releases[release_version]
        if default:
            if release_version != default.version:
                logger.error("get_local_release(): The 'release_version' "
                        "parameter ('%s') doesn't match with the version of "
                        "'default' parameter ('%s')"
                        % (release_version, default.version))
                return False
            self.releases[release_version] = default
            logger.info("get_local_release(): release '%s' not in local, "
                    "but default release supplied so added and returned"
                    % release_version)
            self.update_last_release(release_version)
            return self.releases[release_version]
        # No package in local list nor default supplied
        return False

    def add_role(self, role, user):
        role = self.roles.setdefault(role, [])
        if user in role:
            return False
        role.append(user)
        return True


class PypiRelease(object):
    name = ''
    version = ''
    author = ''
    author_email = ''
    package_url = ''
    release_url = ''
    home_page = ''
    download_url = ''
    docs_url = ''
    bugtrack_url = ''
    summary = ''
    classifiers = None
    description = ''
    keywords = None
    license = ''
    stable_version = None
    maintainer = ''
    maintainer_email = ''
    platform = ''
    requires_python = None
    urls = None

    def __init__(self, package, version):
        self.name = package
        self.version = version
        self.classifiers = []
        self.urs = {}

    def __str__(self):
        ret_str = 'PypiRelease "%s %s"\n' % (self.name, self.version)
        ret_str += '    author="%s"\n' % self.author
        ret_str += '    author_email="%s"\n' % self.author_email
        ret_str += '    package_url="%s"\n' % self.package_url
        ret_str += '    release_url="%s"\n' % self.release_url
        ret_str += '    home_page="%s"\n' % self.home_page
        ret_str += '    download_url="%s"\n' % self.download_url
        ret_str += '    docs_url="%s"\n' % self.docs_url
        ret_str += '    bugtrack_url="%s"\n' % self.bugtrack_url
        ret_str += '    summary="%s"\n' % self.summary
        if True or not self.classifiers:
            ret_str += '    classifiers=[]\n'
        else:
            ret_str += '    classifiers=[\n'
            for category in self.classifiers:
                ret_str += '      %s\n' % category
            ret_str += '      ]\n'
        ret_str += '    description="%s"\n' % self.description
        ret_str += '    keywords="%s"\n' % self.keywords
        ret_str += '    license="%s"\n' % self.license
        ret_str += '    stable_version="%s"\n' % self.stable_version
        ret_str += '    maintainer="%s"\n' % self.maintainer
        ret_str += '    maintainer_email="%s"\n' % self.maintainer_email
        ret_str += '    platform="%s"\n' % self.platform
        ret_str += '    requires_python="%s"\n' % self.requires_python
        if True or not self.urls:
            ret_str += '    urls={}\n'
        else:
            ret_str += '    urls={\n'
            for f_name in sorted(self.urls.keys()):
                ret_str += '      \'%s\': %s\n' % (f_name,
                        self.urls[f_name].__str__().replace('\n', '\n      '))
                ret_str += '      }\n'
        return ret_str

    def __repr__(self):
        return self.__str__()

    def add_download(self, filename, downloads):
        if filename not in self.urls:
            self.urls[filename] = PypiReleaseUrl(filename, downloads)
            return True
        self.urls[filename].downloads = int(downloads)
        return False

    def add_url(self, filename, vals):
        new = (filename not in self.urls)
        url = self.urls.setdefault(filename, PypiReleaseUrl(filename))
        url.update_data(vals)
        return new

    def update_data(self, vals):
        updated = False
        for fieldname in vals:
            if fieldname == 'filename':
                continue
            field_value = vals[fieldname]
            if isinstance(field_value, xmlrpclib.DateTime):
                field_value = datetime.strptime(field_value.value,
                        "%Y%m%dT%H:%M:%S")
            if hasattr(self, fieldname):
                try:
                    curr_val = getattr(self, fieldname)
                    #print "value of %s: %s" % (fieldname, curr_val)
                    if curr_val == field_value:
                        continue
                except:
                    pass
            setattr(self, fieldname, field_value)
            updated = True
        return updated


class PypiReleaseUrl(object):
    filename = ''
    url = ''
    md5_digest = ''
    has_sig = False
    size = 0
    upload_time = None
    downloads = 0
    packagetype = ''
    python_version = ''
    comment_text = ''

    def __init__(self, filename, downloads=False):
        self.filename = filename
        if downloads is not False:
            self.downloads = int(downloads)

    def __str__(self):
        ret_str = 'pypi_client.ReleaseUrl "%s"\n' % self.filename
        ret_str += '    filename="%s"\n' % self.filename
        ret_str += '    url="%s"\n' % self.url
        ret_str += '    md5_digest="%s"\n' % self.md5_digest
        ret_str += '    has_sig="%s"\n' % self.has_sig
        ret_str += '    size="%s"\n' % self.size
        ret_str += '    upload_time="%s"\n' % self.upload_time
        ret_str += '    downloads="%s"\n' % self.downloads
        ret_str += '    packagetype="%s"\n' % self.packagetype
        ret_str += '    python_version="%s"\n' % self.python_version
        ret_str += '    comment_text="%s"\n' % self.comment_text
        return ret_str

    def __repr__(self):
        return self.__str__()

    def update_data(self, vals):
        updated = False
        for fieldname in vals:
            if fieldname == 'filename':
                continue
            field_value = vals[fieldname]
            if isinstance(field_value, xmlrpclib.DateTime):
                field_value = datetime.strptime(field_value.value,
                        "%Y%m%dT%H:%M:%S")
            try:
                curr_val = getattr(self, fieldname)
                if curr_val and curr_val == field_value:
                    continue
            except:
                pass
            setattr(self, fieldname, field_value)
            updated = True
        return updated


class PypiClient(object):
    """
    http://wiki.python.org/moin/PyPiXmlRpc
    """
    server_url = ''
    package_list = None
    client = None
    last_list_update = None
    cache_delta = timedelta(days=3)

    def __init__(self, server_url=None):
        self.server_url = server_url is None and PYPI_XMLRPC_URL or server_url
        self.client = xmlrpclib.ServerProxy(self.server_url)
        self.package_list = {}

    def __str__(self):
        ret_str = 'PypiClient "%s"\n' % self.server_url
        #ret_str += '    server_url="%s"\n' % self.server_url
        if True or not self.package_list:
            ret_str += '    package_list={}\n'
        else:
            ret_str += '    package_list\n'
            for p_name in sorted(self.package_list.keys()):
                package_str = str(self.package_list[p_name])
                package_str.replace("\n", "\n      ")
                ret_str += '       %s\n' % package_str
        ret_str += '    last_list_update="%s"\n' % self.last_list_update
        ret_str += '    cache_delta="%s"\n' % self.cache_delta
        return ret_str

    def __repr__(self):
        return self.__str__()

    def dump(self):
        open_client = False
        if self.client is not None:
            self.client = None
        pickled = jsonpickle.encode(self)
        if open_client:
            self.client = xmlrpclib.ServerProxy(self.server_url)
        return pickled

    def save(self, output_filename):
        pickled = self.dump()
        with open(output_filename, 'w') as output_file:
            output_file.write(pickled)
        return True

    @staticmethod
    def load(pickled):
        new_client = jsonpickle.decode(pickled)
        new_client.client = xmlrpclib.ServerProxy(new_client.server_url)
        return new_client

    @staticmethod
    def open(input_filename):
        with open(input_filename, 'r') as input_file:
            input_str = input_file.read()
        return PypiClient.load(input_str)

    def get_package_list(self):
        last_update_delta = (self.last_list_update and
                datetime.now() - self.last_list_update or None)
        if not last_update_delta or last_update_delta > self.cache_delta:
            self.update_package_list("Framework :: Tryton")
        return [self.package_list[k] for k in sorted(self.package_list.keys())]

    def update_package_list(self, categories):
        """
        Found packages belong in 'categories', update 'package_list' with new
        package or update last release of existing package.
        It uses the 'browse()' method of XML-RPC interface
        ;return (#FOUND_PACKAGES, #NEW_PACKAGES, #UPDATED_PACKAGES)
        """
        if not categories:
            logger.error("get_package_list(categories): Parameter "
                    "'categories' is empty")
            return False
        if isinstance(categories, str):
            categories = [categories]
        elif not isinstance(categories, list):
            logger.error("get_package_list(categories): Parameter "
                    "categories must be a list")
            return False
        p_list = self.client.browse(categories)
        if not p_list:
            logger.info("Any package found in categories: %s"
                    % ", ".join(categories))
            return False
        updated = 0
        new = 0
        for p_name, p_version in p_list:
            if p_name in self.package_list:
                if self.package_list[p_name].update_last_release(p_version):
                    self.package_list[p_name].add_release(p_version)
                    updated += 1
                continue
            package = PypiPackage(p_name, p_version)
            self.package_list[p_name] = package
            new += 1
        self.last_list_update = datetime.now()
        return len(p_list), new, updated

    def get_package(self, package_name, nofetch=False):
        local_package = self.get_local_package(package_name)
        if local_package or nofetch:
            return local_package
        local_package
        # TODO: fetch
        return None

    def get_local_package(self, package_name, default=None):
        if not package_name:
            raise Exception("get_local_package(package_name, default=None): "
                    "package_name not supplied")
        if package_name in self.package_list:
            logger.debug("get_local_package(): Package '%s' found in "
                    "local list. Returning it" % package_name)
            return self.package_list[package_name]
        if default:
            self.package_list[package_name] = default
            logger.info("get_local_package(): package '%s' not in local "
                    "list, but default package supplied so added and returned"
                    % package_name)
            return self.package_list[package_name]
        # No package in local list nor default supplied
        logger.debug("get_local_package(): Package '%s' NOT found in "
                "local list. No default supplied, return False" % package_name)
        return False

    def get_package_releases(self, package_name, show_hidden=False):
        """
        Found releases for this package and update package information in local
        list.
        It uses the 'package_release(package_name, show_hidden)' method of
        XML-RPC interface
        ;return (#FOUND_RELEASES, #NEW_RELEASES)
        """
        package = self.get_local_package(package_name,
                PypiPackage(package_name))

        r_list = self.client.package_releases(package_name, show_hidden)
        if not r_list:
            logger.info("Any release found for package: %s"
                    % package_name)
            return False
        new = 0
        for release_version in r_list:
            if package.add_release(release_version):
                new += 1
        return (len(r_list), new)

    def get_package_roles(self, package_name):
        package = self.get_local_package(package_name,
                PypiPackage(package_name))

        r_list = self.client.package_roles(package_name)
        if not r_list:
            logger.info("Any role found for package: %s" % package_name)
            return False
        new = 0
        for role, user in r_list:
            if package.add_role(role, user):
                new += 1
        return (len(r_list), new)

    def get_release_downloads(self, package_name, release_version):
        package = self.get_local_package(package_name,
                PypiPackage(package_name))
        release = package.get_local_release(release_version,
                PypiRelease(package_name, release_version))

        d_list = self.client.release_downloads(package_name, release_version)
        if not d_list:
            logger.info("Any download found for release '%s' of package "
                    "'%s'" % (release_version, package_name))
            return False
        new = 0
        for filename, downloads in d_list:
            if release.add_download(filename, downloads):
                new += 1
        return (len(d_list), new)

    def get_release_urls(self, package_name, release_version):
        package = self.get_local_package(package_name,
                PypiPackage(package_name))
        release = package.get_local_release(release_version,
                PypiRelease(package_name, release_version))

        u_list = self.client.release_urls(package_name, release_version)
        if not u_list:
            logger.info("Any URL found for release '%s' of package "
                    "'%s'" % (release_version, package_name))
            return False
        new = 0
        for url_vals in u_list:
            if release.add_url(url_vals['filename'], url_vals):
                new += 1
        return (len(u_list), new)

    def get_release_data(self, package_name, release_version):
        package = self.get_local_package(package_name,
                PypiPackage(package_name))
        release = package.get_local_release(release_version,
                PypiRelease(package_name, release_version))

        r_data = self.client.release_data(package_name, release_version)
        if not r_data:
            logger.info("No data found release '%s' of package "
                    "'%s'" % (release_version, package_name))
            return False
        return release.update_data(r_data)

    # TODO: pending XML-RPC methods: search(spec[, operator]) and
    # changelog(since)


