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
        .config(launchInstancePatcher);

    launchInstancePatcher.$inject = ["$provide", 'gbpui.basePath'];

    function launchInstancePatcher($provide, basePath) {
       $provide.decorator(
           'horizon.dashboard.project.workflow.launch-instance.workflow',
           ["$delegate", 'horizon.app.core.workflow.factory',
            'gbpui.group-member.launch-context.service',
               function($delegate, dashboardWorkflow, launchContextService)
               {
                var steps = $delegate.steps;
                var gbstep = {
                    id: 'gbp',
                    title: gettext('GBP'),
                    templateUrl: basePath + 'group-member/group-member.html',
                    helpUrl: basePath + 'group-member/group-member.help.html',
                    formName: 'gbpForm'
                };

                // This check can be potentially made more restrictive to specifically
                // check if policy_target is in the URL
                if (launchContextService.launchContext.successUrl != '/dashboard/project/instances/') {
                    // Finds and replaces the Network and Port wizard pages with
                    // the GBP wizard page
                    var networkIndex = -1;
                    var portIndex = -1;
                    angular.forEach(steps, function (step) {
                        if(step.id == 'networks') {
                            networkIndex = steps.indexOf(step)
                        } else if(step.id == 'ports') {
                            portIndex = steps.indexOf(step);
                        }
                    });

                    if(networkIndex > -1) {
                        steps.splice(networkIndex, 1, gbstep);
                    }

                    if(portIndex > -1) {
                        steps.splice(portIndex, 1);
                    }
                }

                var result = dashboardWorkflow($delegate);
                return result;
           }]
       );
    }

})();
