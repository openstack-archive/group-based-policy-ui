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
        .config(novaApiPatcher);

    novaApiPatcher.$inject = ['$provide'];

    function novaApiPatcher($provide) {
        $provide.decorator(
            'horizon.app.core.openstack-service-api.nova',
            ['$delegate', 'gbpui.group-member.gbp-api',
            function($delegate, gbpApi) {
                var createServer = $delegate.createServer;

                $delegate.createServer = function(newServer) {
                    return gbpApi.createServer(newServer);
                };

                return $delegate
            }]
        );
    }
})();