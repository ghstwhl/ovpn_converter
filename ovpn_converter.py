#!/usr/bin/env python
"""Tool for converting OpnSense exported .visz configs to .ovpn"""
import io
import os
import tarfile
import argparse
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

def cli():
    """Configure the command line options

    Returns:
        argparse.Namespace: Parsed data from command line options
    """
    parser = argparse.ArgumentParser(description='Convert .visz files to .ovpn')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output')
    return parser.parse_args()

def visz_decode(file_path):
    """Decode a .visz file into a dict of components.

    Args:
        file_path (str): File path for the exported visz config bundle
    """
    with tarfile.open(file_path) as zipped:
        data = {}
        for filepath, fileinfo in zip(zipped.getnames(), zipped.getmembers()):
            if not fileinfo.isfile():
                continue
            filename = filepath.split(os.path.sep)[-1]
            file_extension = re.fullmatch(r"^.*\.([^\.]+)$", filename).group(1)
            if 'conf' == file_extension:
                data['config'] = zipped.extractfile(filepath).read().decode('utf8').split('\n')
            elif 'key' == file_extension:
                data['tls_key'] = zipped.extractfile(filepath).read().decode('utf8').split('\n')
            elif 'p12' == file_extension:
                data['cert_bundle'] = {}
                private_key, certificate, additional_certificates = load_key_and_certificates(
                    zipped.extractfile(filepath).read(), None)

                data['cert_bundle']['key'] = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                    ).decode('utf8').split('\n')

                data['cert_bundle']['cert'] = certificate.public_bytes(
                    encoding=serialization.Encoding.PEM
                    ).decode('utf8').split('\n')

                data['cert_bundle']['ca'] = []
                for cert in additional_certificates:
                    pem = cert.public_bytes(
                        encoding=serialization.Encoding.PEM
                        ).decode('utf8').split('\n')
                    for line in pem:
                        data['cert_bundle']['ca'].append(line)
            else:
                data[filename] = zipped.extractfile(filepath).read()
        return data

def create_ovpn_text_bundle(config):
    """Convert the decoded visz config bundle into an in-line ovpn config

    Args:
        config (dict): dict of the config returned by visz_decode()
    """

    if 'config' in config:
        text_config = ['#-- Converted from OpnSense export with '
                         'https://github.com/ghstwhl/ovpn_converter --#']
        for config_line in config['config']:
            if 'tls-crypt' in config_line:
                text_config.append('<tls-crypt>')
                for key_line in config['tls_key']:
                    text_config.append(key_line)
                text_config.append('</tls-crypt>')
            elif 'pkcs12' in config_line:
                for block_name in config['cert_bundle']:
                    text_config.append(f"<{block_name}>")
                    for cert_line in config['cert_bundle'][block_name]:
                        text_config.append(cert_line)
                    text_config.append(f"</{block_name}>")
            elif 'Config Auto Generated for Viscosity' in config_line:
                pass
            else:
                text_config.append(config_line)

        return text_config

if __name__ == '__main__':
    args = cli()
    results = re.fullmatch(r"^(.*/|)([^\/]*)\.(visz)$", args.input)
    if results is not None:
        if 'visz' == results.group(len(results.groups())):
            config_bundle = create_ovpn_text_bundle(visz_decode(args.input))
            if args.output is not None:
                output_file = args.output
            else:
                output_file = results.group(1)
                for n in range(2,len(results.groups())):
                    output_file += results.group(n)
                output_file += ".ovpn"
            with io.open(output_file, 'w', encoding='utf-8') as out:
                out.write(str('\n'.join(config_bundle)))
            print(f"New config written:  {output_file}")

    else:
        results = re.fullmatch(r"^.*\.([^\.]+)$", args.input)
        print(f"{results.group(len(results.groups()))} is not a supported file type.")
