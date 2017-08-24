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
        .module('gbpui.transfer-table-bridge')
        .directive('dTable', ['gbpui.basePath', function(basePath){
            return {
                restrict: 'E',
                scope: true,
                templateUrl: basePath +
                    "transfer-table-bridge/transfer-table-bridge.html",
                transclude: true,
                link: function($scope, $elem, $attrs, $ctrl, $transclude) {

                    var initial = [];
                    var available = [];

                    var transcluded = $transclude();

                    transcluded.each(function(index, element) {
                        if(element.localName=="option") {
                            var val = {
                                'id': $(element).attr('value'),
                                'name': $(element).text()
                            };
                            available.push(val);

                            if($(element).prop('selected')) {
                                initial.push(val);
                            }
                        }
                    });
                    $scope.initial = initial;

                    var allocated = [];

                    $scope.tableData = {
                        available: available,
                        allocated: allocated,
                        displayedAvailable: [],
                        displayedAllocated: [],
                        minItems: -1
                    };

                    var maxAllocation =  "maxItems" in $attrs
                        ? Number($attrs["maxItems"])
                        : -1;
                    $scope.tableLimits = {
                        maxAllocation: maxAllocation
                    };

                    $scope.tableHelpText = {
                        allocHelpText: $attrs['allocatedHelpText'],
                        availHelpText: $attrs['availableHelpText'],
                        noAllocText: $attrs['noAllocatedText'],
                        noAvailText: $attrs['noAvailableText']
                    };

                    $scope.facets = [{
                            label: gettext("Name"),
                            name: "name",
                            singleton: true
                    }];

                    if("addItemLink" in $attrs) {
                        $scope.addItemLink = $attrs["addItemLink"];
                    }

                    if("allocatedFilter" in $attrs) {
                        $scope.allocatedFilter = true;
                    }

                    $scope.id = $attrs["id"];
                    $scope.name = $attrs["name"];

                }
            }
        }])

})();