#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 PickNik Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the PickNik Inc. nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Usage: python moveit/moveit/scripts/create_readme_table.py > /tmp/table.md
# First update supported_distro_ubuntu_dict below!


from __future__ import print_function

import os
import sys

from catkin_pkg.packages import find_packages
import requests


def create_header(ros_ubuntu_dict):
    ros_distros = sorted(ros_ubuntu_dict.keys())
    section_header = "### ROS Buildfarm\n"
    header = "MoveIt Package"
    header_lines = "-" * len(header)
    for ros in ros_distros:
        source = " ".join([ros.capitalize(), "Source"])
        debian = " ".join([ros.capitalize(), "Debian"])
        header = " | ".join([header, source, debian])
        header_lines = " | ".join([header_lines, "-" * len(source), "-" * len(debian)])
    return "\n".join([section_header, header, header_lines])


def define_urls(target, params):
    if target == "src":
        params["job"] = "{R}src_u{U}__{package}__ubuntu_{ubuntu}__source".format(
            **params
        )
        params["url"] = "{base_url}/view/{R}src_u{U}/job/{job}".format(**params)
    elif target == "bin":
        params["job"] = (
            "{R}bin_u{U}64__{package}__ubuntu_{ubuntu}_amd64__binary".format(**params)
        )
        params["url"] = "{base_url}/view/{R}bin_u{U}64/job/{job}".format(**params)


def create_line(package, ros_ubuntu_dict):
    ros_distros = sorted(ros_ubuntu_dict.keys())
    line_format = " | [![Build Status]({base_url}/buildStatus/icon?job={job})]({url})"
    line = "\n" + package
    print(package, file=sys.stderr)
    for ros in ros_distros:
        ubuntu = ros_ubuntu_dict[ros]
        params = {
            "R": ros[0].upper(),
            "U": ubuntu[0].upper(),
            "ubuntu": ubuntu.lower(),
            "package": package,
            "base_url": "https://build.ros.org",
        }
        for target in ["src", "bin"]:
            define_urls(target, params)
            response = requests.get(params["url"]).status_code
            # we want to show a particular OS's badges to indicate they are not
            # released / working yet
            if response < 400 or ubuntu == "focal":  # success
                line += line_format.format(**params)
            else:  # error
                line += " | "
                print(
                    "  {}: {} {}".format(ros, response, params["url"]), file=sys.stderr
                )

    return line


def create_moveit_buildfarm_table():
    """Create MoveIt buildfarm badge table."""
    # Update the following dictionary with the appropriate ROS-Ubuntu
    # combinations for supported distribitions. For instance, in Noetic,
    # remove {"indigo":"trusty"} and add {"noetic":"fbuntu"} with "fbuntu"
    # being whatever the 20.04 distro is named
    supported_distro_ubuntu_dict = {
        "melodic": "bionic",
        "noetic": "focal",
    }

    all_packages = sorted(
        package.name for _, package in find_packages(os.getcwd()).items()
    )
    moveit_packages = []
    other_packages = []
    for package in all_packages:
        if package.startswith("moveit"):
            moveit_packages.append(package)
        else:
            other_packages.append(package)
    moveit_packages.extend(other_packages)

    buildfarm_table = create_header(supported_distro_ubuntu_dict)
    for package in moveit_packages:
        buildfarm_table += create_line(package, supported_distro_ubuntu_dict)
    print(buildfarm_table)


if __name__ == "__main__":
    sys.exit(create_moveit_buildfarm_table())
