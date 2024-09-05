# ovpn_converter
Tool for converting OpenVPN configs from visz to ovpn.

This quick and dirty tool will convert the visz format client config bundle
exported from the Clinet Export menu in OpnSense into an ovpn config that
has all the required keys and certs embedded in PEM format.  I found this
was the best format for importing the config into the OpenVPN client on
my phone.

If this tool helps you, awesome.

I don't have any current plans to support the other export formats.  This
works, and that's good enough for me.

If you have an issue with it, please feel free to open an issue on this repo.

Copyright 2024 - Chris Knight