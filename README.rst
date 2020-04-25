==============
gs_pip_install
==============


.. image:: https://img.shields.io/pypi/v/gs_pip_install.svg
        :target: https://pypi.python.org/pypi/gs_pip_install

.. image:: https://img.shields.io/travis/lucidsushi/gs_pip_install.svg
        :target: https://travis-ci.org/lucidsushi/gs_pip_install

.. image:: https://readthedocs.org/projects/gs-pip-install/badge/?version=latest
        :target: https://gs-pip-install.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/lucidsushi/gs_pip_install/shield.svg
     :target: https://pyup.io/repos/github/lucidsushi/gs_pip_install/
     :alt: Updates


 [ ~ Dependencies scanned by PyUp.io ~ ]


Pip Install Packages Stored in Google Cloud Buckets

.. code-block:: bash

        gs_pip_install --bucket_url gs://python-package-location --package_name google_cloud_utils==1.0.1

        gs_pip_install --bucket_url gs://python-package-location --package_name google_cloud_utils --target_dir .

        gs_pip_install --bucket_url gs://python-package-location --r bucket_only_requirements.txt



* Free software: MIT license
* Documentation: https://gs-pip-install.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
