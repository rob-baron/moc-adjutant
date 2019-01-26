# Copyright 2018 Mass Open Cloud
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.utils import timezone

from rest_framework.response import Response

from adjutant.api.v1 import tasks
from adjutant.api.v1 import openstack
from adjutant.api.v1.utils import create_notification, add_task_id_for_roles
from adjutant.api import utils


class InviteExternalUser(openstack.UserList):

    task_type = "invite_external_user"

    default_actions = ['ExternalUserAction', ]

    @utils.mod_or_admin
    def get(self, request):
        return super(InviteExternalUser, self).get(request)

    @utils.mod_or_admin
    def post(self, request, format=None):
        """
        Invites a user to the current tenant.

        This endpoint requires either Admin access or the
        request to come from a project_admin|project_mod.
        As such this Task is considered pre-approved.
        """
        self.logger.info("(%s) - New AttachUser request." % timezone.now())

        # Default project_id to the keystone user's project
        if ('project_id' not in request.data
                or request.data['project_id'] is None):
            request.data['project_id'] = request.keystone_user['project_id']

        processed, status = self.process_actions(request)

        errors = processed.get('errors', None)
        if errors:
            self.logger.info("(%s) - Validation errors with task." %
                             timezone.now())

            return Response({'errors': errors}, status=status)

        response_dict = {'notes': processed['notes']}

        add_task_id_for_roles(request, processed, response_dict, ['admin'])

        return Response(response_dict, status=status)
