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

from adjutant.api.v1.models import register_taskview_class
from adjutant.actions.v1.models import register_action_class
from adjutant.actions.v1.serializers import NewUserSerializer

from adjutant_moc import actions
from adjutant_moc import tasks

register_action_class(actions.ExternalUserAction, NewUserSerializer)
register_taskview_class(r'^actions/InviteUser/?$', tasks.InviteExternalUser)

register_taskview_class(
    r'^openstack/users/?$', tasks.InviteExternalUser)  # this handles both invite and list