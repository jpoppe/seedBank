#!/bin/bash -x

# Copyright 2011, Jasper Poppe <jpoppe@ebay.com>, Lex van Roon
# <lvanroon@ebay.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

while ! virsh list | grep ${1} > /dev/null; do
	sleep 1
done

virt-manager --connect=qemu:///system --show-domain-console $(virsh domuuid ${1} | head -n1)


#displays=$(disper -l | grep display | wc -l)
#
#if [[ $displays == 1 ]]; then
#	sleep 3
#
#	CURRENT_VP=$(wmctrl -d | awk '{print $6}')
#	x=${CURRENT_VP%%,*}
#	y=${CURRENT_VP##*,}
#
#	wmctrl -r "Virtual Machine Manager" -e 0,$(( 0 - ${x} )),$(( 2700 - ${y} )),560,1080
#	wmctrl -r "overlord001 Virtual Machine" -e 0,$(( 560 - ${x} )),$(( 2160 - ${y} )),960,640
#fi
