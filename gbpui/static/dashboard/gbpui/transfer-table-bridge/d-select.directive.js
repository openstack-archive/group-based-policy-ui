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
        .directive('dSelect', function () {
            return {
                restrict: 'A',
                scope: true,
                link: function ($scope, $elem, $attrs, $ctrl) {


                    $.each($scope.tableData.available, function (index, optionObject) {
                        var option = $("<option></option>");
                        option.attr("value", optionObject.id);
                        option.append(optionObject.name);
                        $elem.append(option);
                    });

                    // This change listener watches for changes to the raw
                    // HTML select element; since the select should be hidden,
                    // the only possible change is the creation of a new
                    // option using the horizon add button.
                    $elem.change(function () {
                        // Find the last option in the select, since the
                        // addition is done by Horizon appending the a new
                        // option element
                        var option = $(this).find("option").last();

                        // Create a valid option object and make it available
                        // at the end of the available list
                        var val = {
                            'id': option.attr('value'),
                            'name': option.text()
                        };
                        $scope.tableData.available.push(val);

                        // Deallocate all the objects using the built in
                        // transfer table controller deallocation method
                        var toDeallocate = $scope.tableData.allocated.slice();
                        $.each(toDeallocate, function (index, object) {
                            $scope.trCtrl.deallocate(object);
                        });
                        // Notify the scope of the deallocations
                        $scope.$apply();

                        // Allocate the new option; this mimicks te behaviour
                        // of the normal Horizon based adding
                        $scope.trCtrl.allocate(val);

                        // Notify the scope of the allocation changes
                        $scope.$apply();
                    });

                    // The directive watches for a changes in the allocated
                    // list to dynamically set values for the hidden element.
                    $scope.$watchCollection(
                        function (scope) {
                            return $scope.tableData.allocated;
                        },
                        function (newValue, oldValue) {
                            var values = $.map(
                                newValue, function (value, index) {
                                    return value.id;
                                });
                            $elem.val(values);
                        }
                    );

                    // Sets initial values as allocated when appropriate
                    $.each($scope.initial, function (index, initialObject) {
                        $scope.trCtrl.allocate(initialObject);
                    });


                }
            }
        });
})();
