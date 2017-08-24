/**
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

(function () {
    angular
        .module('gbpui.group-member')
        .factory('gbpui.group-member.gbp-api', gbpApi);

    gbpApi.$inject = [
        'horizon.framework.util.http.service',
        'horizon.framework.widgets.toast.service'
    ];

    function gbpApi(apiService, toastService) {

        function getPolicyTargetGroups() {
            return apiService.get('project/policytargets/policy_target_groups')
                .error(function () {
                    toastService.add('error', gettext('Unable to retrieve Policy Target Groups'))
                });
        }

        function createServer(newServer) {
            return apiService
                .post('project/policytargets/launch_instance/', newServer)
                .error(function () {
                    toastService.add('error', gettext('Unable to create Instance'))
                })
        }

        return {
            getPolicyTargetGroups: getPolicyTargetGroups,
            createServer: createServer
        };
    }
})();
