# ovpn_converter.py
Tool for converting OpenVPN configs from visz to ovpn.

This quick and dirty tool will convert the zip compressed visz client config
bundle, as exported from the Client Export menu in OpnSense, into an ASCII
ovpn config that has all the required keys and certs embedded in PEM format.
I found this was the best format for importing the config into the OpenVPN
client on my phone.

I don't have any current plans to support the other export formats.  This
works, and that's good enough for me.  I spent far more time writing this
stupid script than I did hand converting from the .zip format into .ovpn
format.  

If this tool helps you, awesome.  That would make the extra time I put into
this worth it for somebody.

If you have a problem with it, please feel free to open an issue on this repo.

It is recommended that you use the included Pipfile and Pipfile.lock to set
up a pipenv for running this tool.

Copyright 2024 - [Chris Knight](https://www.ghostwheel.com/)
