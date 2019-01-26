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

from adjutant.actions.v1.base import BaseAction
from adjutant.actions.v1.base import UserNameAction
from adjutant.actions.v1.base import UserMixin
from adjutant.actions.v1.base import ProjectMixin
from adjutant.actions import user_store


def validate_steps(validation_steps):
    """Helper function for validation in actions

    Takes a list of validation functions or validation function results.
    If function, will call it first, otherwise checks if valid. Will break
    and return False on first validation failure, or return True if all valid.

    It is best to pass in the functions and let this call them so that it
    doesn't keep validating after the first invalid result.
    """
    for step in validation_steps:
        if callable(step):
            if not step():
                return False
        if not step:
            return False
    return True


class ExternalUserAction(UserNameAction, ProjectMixin, UserMixin):
    """
    Setup a new user with a role on the given project.
    Creates the user if they don't exist, otherwise
    if the username and email for the request match the
    existing one, will simply add the project role.
    """

    required = [
        'username',
        'email',
        'project_id',
        'roles',
        'domain_id',
    ]

    def _validate(self):
        self.action.valid = validate_steps([
            self._validate_role_permissions,
            self._validate_keystone_user,
            self._validate_domain_id,
            self._validate_project_id,
        ])
        self.action.save()

    def _pre_approve(self):
        self._validate()

        self.add_note("Pre, %s" % self.action.task.keystone_user['username'])

        self.set_auto_approve()

    def _post_approve(self):
        self.action.need_token = True
        self._validate()

    def _submit(self, token_data):
        self._validate()

        if not self.valid:
            return

        id_manager = user_store.IdentityManager()
        user = id_manager.find_user(self.username, None)
        roles = id_manager.get_roles(user, self.project_id)
        role_names = {role.name for role in roles}
        missing = set(self.roles) - role_names

        self.add_note("Accepted by %s" % self.action.task.keystone_user['username'])

        if not missing:
            self.add_note(
                'Existing user %s already had roles %s in project %s.'
                % (self.username, self.roles, self.project_id))
        else:
            self.roles = list(missing)
            self.grant_roles(user, self.roles, self.project_id)
            self.add_note(
                'Existing user %s has been given roles %s in project %s.'
                % (self.username, self.roles, self.project_id))


class ProjectRequestAction(ProjectMixin, UserMixin, BaseAction):

    required = [
        "email",
        "requested_project",
        "requested_service"
    ]

    @staticmethod
    def _validate_valid_service(service):
        return service in ['kaizen', 'openshift']

    def _get_email(self):
        return self.email

    def _pre_approve(self):
        self._validate_valid_service(self.requested_service)

    def _post_approve(self):
        # Set token field to be token

        # Send email
        pass

    def _submit(self):
        # Add user from token to approved project in requested service

        # Send welcome email

        pass
