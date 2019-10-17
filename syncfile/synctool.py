# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
import argparse
import yaml
from collections import namedtuple
from paramiko import SSHClient, SFTPClient, AutoAddPolicy

_log = logging.getLogger(__name__)


def get_files(opt, sync_options, file_options):
	opt_dict = vars(opt)
	arg_dict = {}
	file_patterns = []
	for k, v in opt_dict.items():
		if k in sync_options:
			arg_dict[k] = v
			continue
		if k in file_options:
			if v:
				file_patterns.append(v)
	files = []
	for pattern in file_patterns:
		_log.debug("pattern=%r, arg_dict=%r", pattern, arg_dict)
		f = pattern.format(**arg_dict)
		files.append(f)
	return files


def parse_options(pattern_dict, sync_options, argv):
	parser = argparse.ArgumentParser()
	arg_opions = []
	if sync_options:
		for opt, description in sync_options.items():
			option = '--{opt}-arg'.format(opt=opt)
			arg_opions.append('{opt}'.format(opt=opt))
			parser.add_argument(option, dest=opt, help=description)
	file_options = []
	for opt, pattern in pattern_dict.items():
		option = '--{opt}-file'.format(opt=opt)
		file_options.append('{opt}_file'.format(opt=opt))
		parser.add_argument(option, action='store_const', const=pattern, default=None, help='pattern: %r' % pattern)
	opt = parser.parse_args(argv)
	return get_files(opt, arg_opions, file_options)


HostInfo = namedtuple('HostInfo', ('ip', 'port', 'key', 'user'))


def parse_configure(cfg_path):
	cfg_path = os.path.join('etc', 'sync-cfg.yaml')

	with open(cfg_path) as fp:
		cfg = yaml.safe_load(fp)

	sync_file_dict = cfg['sync-files']
	sync_options = cfg.get('sync-options')
	host_info = HostInfo(cfg['host-ip-dest'], cfg.get('port', 22), cfg['ssh-key'], cfg['user-name'])
	_log.debug("host_info=%r", host_info)
	return host_info, sync_file_dict, sync_options


def run_scp(host_info, src, dest):
	""" connect to host and send srouce file to destination """
	try:
		ssh_client = SSHClient()
		ssh_client.set_missing_host_key_policy(AutoAddPolicy())
		ssh_client.connect(host_info.ip, host_info.port, host_info.user, key_filename=host_info.key)
		sftp_client = SFTPClient.from_transport(ssh_client.get_transport())
		sftp_client.put(src, dest)
		sftp_client.close()
	except Exception as e:
		raise e


def sync_file(host_info, source, destination):
	_log.info('Src: %r, Dest: %r', source, destination)
	if not os.path.isfile(source):
		_log.info("New file: %r", source)
		with open(source, 'w') as fp:
			fp.write('%s' % datetime.datetime.now())
	if not os.path.isfile(source):
		raise ValueError("Error source file not exist: %r" % source)
	run_scp(host_info, source, destination)


def main():
	cfg_path = os.path.join('etc', 'sync-cfg.yaml')
	host_info, pattern_dict, sync_options = parse_configure(cfg_path)
	files = parse_options(pattern_dict, sync_options, sys.argv[1:])
	for f in files:
		if not os.path.isfile(f):
			_p, file_name = os.path.split(f)
			src = '/tmp/{f}'.format(f=file_name)
			dest = f
			sync_file(host_info, src, dest)
		else:
			sync_file(host_info, f, f)


if __name__ == "__main__":
	main()
