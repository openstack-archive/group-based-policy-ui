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
    'use strict';

    angular
        .module('gbpui.group-member')
        .config(launchInstanceModelPatcher);

    launchInstanceModelPatcher.$inject = ['$provide'];

    function launchInstanceModelPatcher($provide) {
        $provide.decorator(
            'launchInstanceModel',
            ['$delegate', 'gbpui.group-member.gbp-api', '$q',
                'gbpui.group-member.launch-context.service',
                function($delegate, gbpApi, $q, launchContextService) {

                var createInstance = $delegate.createInstance;
                $delegate.createInstance = function() {
                    // This is a workaround for new instance initalization
                    // inside 'launchInstanceModel' done by functions not
                    // exposed by the $delegate
                    $delegate.newInstanceSpec.group_policy_targets =
                        $delegate.allocated_group_policy_targets;
                    return createInstance();
                };

                $delegate.group_policy_targets = [];
                $delegate.allocated_group_policy_targets = [];

                var initialize = $delegate.initialize;

                $delegate.initialize = function(deep) {
                    $delegate.group_policy_targets.length = 0;
                    $delegate.allocated_group_policy_targets.length = 0;

                    $q.all([gbpApi.getPolicyTargetGroups().then(function(data){
                            var defaults =
                                launchContextService.launchContext.defaults;

                            angular.forEach(data.data, function(value, index) {
                                $delegate.group_policy_targets.push(value);

                                if(defaults.indexOf(value.id) > -1) {
                                    $delegate.allocated_group_policy_targets
                                        .push(value);
                                }
                            });
                        }), initialize(deep)
                    ]);
                };

                return $delegate
            }]
        )
    }

})();