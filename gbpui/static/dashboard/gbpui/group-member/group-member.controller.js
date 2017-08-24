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

(function() {
    angular
        .module('gbpui.group-member')
        .controller('GBPController', gbpController);


    gbpController.$inject = [
        '$scope',
        'horizon.dashboard.project.workflow.launch-instance.modal.service',
        'gbpui.group-member.launch-context.service'
    ];

    function gbpController(
        $scope, launchInstanceModalService, launchContextService)
    {
        var ctrl = this;

        ctrl.launchContext = launchContextService.launchContext;
        ctrl.inputIPs = {

        };

        ctrl.tableHelp = {
            noneAllocText: gettext('Select a group-member from the table below'),
            availHelpText: gettext('Select one or more groups'),
            noneAvailText: gettext('No groups available'),
        };

        ctrl.tableLimits = {
            maxAllocation: -1
        };

        ctrl.addFixedIp = function(row) {
            var ipAddress = ctrl.inputIPs[row.id];
            row.fixed_ip = ipAddress;
        };

        ctrl.removeFixedIp = function(row) {
            delete row['fixed_ip'];
        };

        ctrl.tableData = {
            available: $scope.model.group_policy_targets,
            allocated: $scope.model.allocated_group_policy_targets,
            displayedAvailable: [],
            displayedAllocated: [],
            minItems: 1
        };
    }
})();