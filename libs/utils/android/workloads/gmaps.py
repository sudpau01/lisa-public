# SPDX-License-Identifier: Apache-2.0
#
# Copyright (C) 2015, ARM Limited and contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
import os
import logging

from time import sleep

from android import Screen, System
from android.workload import Workload


class GMaps(Workload):
    """
    Android GMaps workload
    """

    # Package required by this workload
    package = 'com.google.android.apps.maps'
    action = 'android.intent.action.VIEW'

    def __init__(self, test_env):
        super(GMaps, self).__init__(test_env)
        self._log = logging.getLogger('GMaps')
        self._log.debug('Workload created')

        # Set of output data reported by GMaps
        self.db_file = None

    def run(self, out_dir, location_search, swipe_count=5, collect=''):
        """
        Run single Gmaps workload.

        :param out_dir: Path to experiment directory where to store results.
        :type out_dir: str

        :param location_search: Search string to be used in GMaps
        :type location_search: str

        :param swipe_count: Number of sets of (left, right, up, down) swipes to do
        :type swipe_count: int

        :param collect: Specifies what to collect. Possible values:
            - 'energy'
            - 'systrace'
            - 'ftrace'
            - any combination of the above
        :type collect: list(str)
        """

        # Keep track of mandatory parameters
        self.out_dir = out_dir
        self.collect = collect

        # Set min brightness
        Screen.set_brightness(self._target, auto=False, percent=0)
        # Unlock device screen (assume no password required)
        System.menu(self._target)
        # Press Back button to be sure we run the video from the start
        System.back(self._target)

        # Use the monkey tool to start GMaps
        # This allows to subsequently set the screen orientation to LANDSCAPE
        # and to reset the frame statistics.
        System.monkey(self._target, self.package)

        # Force screen in PORTRAIT  mode
        Screen.set_orientation(self._target, portrait=True)

        System.gfxinfo_reset(self._target, self.package)
        sleep(1)

        # Start GMaps on the target device
        loc_url = 'geo:0,0?q='
        loc_url += '+'.join(location_search.split())
        System.start_action(self._target, self.action, loc_url)
        # Allow the activity to start
        sleep(1)

        self.tracingStart()
        self._log.info('Opening GMaps to [%s]', loc_url)
        # Let GMaps zoom in on the location
        sleep(2)

        for i in range(swipe_count):
            System.hswipe(self._target, 20, 80, 100, True)
            sleep(.5)
            System.hswipe(self._target, 20, 80, 100, False)
            sleep(.5)
            System.vswipe(self._target, 40, 60, 100, True)
            sleep(.5)
            System.vswipe(self._target, 40, 60, 100, False)
            sleep(.5)

        self.tracingStop()

        # Get frame stats
        self.db_file = os.path.join(out_dir, "framestats.txt")
        System.gfxinfo_get(self._target, self.package, self.db_file)

        # Close the app without clearing the local data to
        # avoid the dialog to select the account at next start
        System.force_stop(self._target, self.package, clear=False)

        # Go back to home screen
        System.home(self._target)

        # Set brightness back to auto
        Screen.set_brightness(self._target, auto=True)

        # Switch back to screen auto rotation
        Screen.set_orientation(self._target, auto=True)

# vim :set tabstop=4 shiftwidth=4 expandtab
