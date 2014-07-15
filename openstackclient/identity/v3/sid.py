#   Copyright 2012-2013 OpenStack Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Identity v3 Sid action implementations"""

import logging
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateSid(show.ShowOne):
    """Create sid command"""

    log = logging.getLogger(__name__ + '.CreateSid')

    def get_parser(self, prog_name):
        parser = super(CreateSid, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<sid-name>',
            help='New sid name',
        )
        parser.add_argument(
            '--description',
            metavar='<sid-description>',
            help='New sid description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable sid')
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable sid')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        sid = identity_client.sids.create(
            name=parsed_args.name,
            description=parsed_args.description,
            enabled=parsed_args.enabled,
        )

        return zip(*sorted(six.iteritems(sid._info)))


class DeleteSid(command.Command):
    """Delete sid command"""

    log = logging.getLogger(__name__ + '.DeleteSid')

    def get_parser(self, prog_name):
        parser = super(DeleteSid, self).get_parser(prog_name)
        parser.add_argument(
            'sid',
            metavar='<sid>',
            help='Name or ID of sid to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        sid = utils.find_resource(identity_client.sids,
                                     parsed_args.sid)
        identity_client.sids.delete(sid.id)
        return


class ListSid(lister.Lister):
    """List sid command"""

    log = logging.getLogger(__name__ + '.ListSid')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        columns = ('ID', 'Name', 'Enabled', 'Description')
        data = self.app.client_manager.identity.sids.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetSid(command.Command):
    """Set sid command"""

    log = logging.getLogger(__name__ + '.SetSid')

    def get_parser(self, prog_name):
        parser = super(SetSid, self).get_parser(prog_name)
        parser.add_argument(
            'sid',
            metavar='<sid>',
            help='Name or ID of sid to change',
        )
        parser.add_argument(
            '--name',
            metavar='<new-sid-name>',
            help='New sid name',
        )
        parser.add_argument(
            '--description',
            metavar='<sid-description>',
            help='New sid description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable sid (default)',
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable sid',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        sid = utils.find_resource(identity_client.sids,
                                     parsed_args.sid)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if 'enabled' in parsed_args:
            kwargs['enabled'] = parsed_args.enabled

        if not kwargs:
            sys.stdout.write("Sid not updated, no arguments present")
            return
        identity_client.sids.update(sid.id, **kwargs)
        return


class ShowSid(show.ShowOne):
    """Show sid command"""

    log = logging.getLogger(__name__ + '.ShowSid')

    def get_parser(self, prog_name):
        parser = super(ShowSid, self).get_parser(prog_name)
        parser.add_argument(
            'sid',
            metavar='<sid>',
            help='Name or ID of sid to display',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        sid = utils.find_resource(identity_client.sids,
                                     parsed_args.sid)

        return zip(*sorted(six.iteritems(sid._info)))
