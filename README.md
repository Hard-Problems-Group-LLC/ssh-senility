# ssh-senility

Getting older?

Not sleeping as much as you should?

Put a 1989 Mark I MR2 into a telephone pole at 87 miles per hour?

Found "the good" party at a cybersecurity convention, where all of the
whiskey came in by diplomatic pouch?

Dating a professional actor or actress?


There are a number of reasons someone can lose track of which of their SSH
keys are authoritative on a particular remote server.  ssh-senility
is a utility to rapidly determine which of your SSH keys are recognized as
valid for a particular user and remote host.


BASIC USAGE:
============

Run:

    ssh-senility.py <username> <hostname>


Simple as that!  The program will produce a well-formatted table showing you
which of your keys worked, if any, similar to the following:


./ssh-senility.py jdoe thegibson

[*] Target       : jdoe@thegibson
[*] Key Directory: /home/jdoe/.ssh
[*] Delay Range  : 1.0s to 3.0s
--------------------------------------------------
[*] Found 4 potential private keys to test.

[1/4] Testing key: id_ed25519_home_jdoe_grannymac_17OCT2025... Failed. ❌
    Sleeping for 1.37 seconds...
[2/4] Testing key: id_ed25519_work_jdoe_dellofsadness_30JUL2025... Failed. ❌
    Sleeping for 2.92 seconds...
[3/4] Testing key: id_namingconventionyoutotallyforgotabout... SUCCESS! ✅
    Sleeping for 2.30 seconds...
[4/4] Testing key: id_ed25519_cyberbus_jdoe_c64ofdoom_13FEB2026... Failed. ❌

[*] Audit Complete. Summary of Results:
┌─────────────────────────────────────────────┬──────────┐
│ Key File                                    │ Status   │
├─────────────────────────────────────────────┼──────────┤
│ id_ed25519_home_jdoe_grannymac_30JUL2025    │ Failed   │
│ id_ed25519_work_jdoe_dellofsadness_17OCT2025│ Failed   │
│ id_namingconventionyoutotallyforgotabout    │ Success  │
│ id_ed25519_cyberbus_jdoe_c64ofdoom_13FEB2026│ Failed   │
└─────────────────────────────────────────────┴──────────┘



ADVANCED USAGE:
===============

Run:

    ssh-senility.py --help

...to see the latest handy options and features available!


LICENSE
=======
The MIT License (MIT)

Copyright © 2026 Hard Problems Group, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

