#
# Copyright (c) 2017, Daniel Korn <korndaniel1@gmail.com>
#
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os

try:
    from manageiq_client.api import ManageIQClient
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False


def check_client(module):
    if not HAS_CLIENT:
        module.fail_json(
            msg='manageiq_client.api is required for this module'
        )


class ManageIQ(object):
    """
        class encapsulating ManageIQ API client
    """

    def __init__(self, module):
        # handle import errors
        check_client(module)

        # set defaults
        params = dict(
            url=os.environ.get('MIQ_URL', None),
            username=os.environ.get('MIQ_USERNAME', None),
            password=os.environ.get('MIQ_PASSWORD', None),
            verify_ssl=True,
            ca_bundle_path=None,
        )
        params.update(module.params['manageiq_connection'])

        for arg in ['url', 'username', 'password']:
            if params[arg] in (None, ''):
                module.fail_json(msg="missing required argument: manageiq_connection[{}]".format(arg))

        url = params['url']
        username = params['username']
        password = params['password']
        verify_ssl = params['verify_ssl']
        ca_bundle_path = params['ca_bundle_path']

        self.module = module
        self.api_url = url + '/api'
        self.client = ManageIQClient(self.api_url, (username, password), verify_ssl=verify_ssl, ca_bundle_path=ca_bundle_path)

    def find_collection_resource_by(self, collection_name, **params):
        """ Searches the collection resource by the collection name and the param passed

        Returns:
            the resource as an object if it exists in manageiq, None otherwise.
        """
        try:
            entity = self.client.collections.__getattribute__(collection_name).get(**params)
        except ValueError:
            return None
        except Exception as e:
            self.module.fail_json(msg="Failed to find resource {error}".format(error=e))
        return vars(entity)
