# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='gs.group.member.add',
    version=version,
    description="The pages that are required to add people to "
      "GroupServer groups, without an invitation",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux"
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='sign up, registration, profile, user, join',
    author='Richard Waid',
    author_email='richard@iopen.net',
    url='http://groupserver.org',
    license='ZPL 2.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.group', 'gs.group.member'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
        'Zope2',
        'zope.cachedescriptors',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'gs.content.form',
        'gs.content.layout',
        'gs.group.base',
        'gs.group.member.base',
        'gs.group.member.invite',
        'gs.group.member.join',
        'gs.group.member.list',
        'gs.group.member.viewlet',
        'gs.group.messages.topics',  # The notification has a list of topics
        'gs.help',
        'gs.profile.email.base',
        'gs.profile.notify',
        'gs.profile.password',
        'Products.CustomUserFolder',
        'Products.GSAuditTrail',
        'Products.GSGroup',
        'Products.GSProfile',
        'Products.XWFCore',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,)
