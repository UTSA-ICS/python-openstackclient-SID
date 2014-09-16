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

"""Sip action implementations"""
import traceback

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateSip(show.ShowOne):
    """Create new sip"""

    log = logging.getLogger(__name__ + '.CreateSip')

    def get_parser(self, prog_name):
        parser = super(CreateSip, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<sip-name>',
            help='New sip name',
        )
        parser.add_argument(
            '--sid',
            metavar='<sip-sid>',
            help='Domain owning the sip (name or ID)',
        )
        parser.add_argument(
            '--description',
            metavar='<sip-description>',
            help='New sip description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable sip',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable sip',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add for this sip '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.sid:
            sid = utils.find_resource(
                identity_client.domains,
                parsed_args.sid,
            ).id
        else:
            sid = None

        enabled = True
        if parsed_args.disable:
            enabled = False
        kwargs = {}
        if parsed_args.property:
            kwargs = parsed_args.property.copy()

        sip = identity_client.projects.create(
            name=parsed_args.name,
            domain=sid,
            description=parsed_args.description,
            enabled=enabled,
            **kwargs
        )

        info = {}
        info.update(sip._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteSip(command.Command):
    """Delete sip"""

    log = logging.getLogger(__name__ + '.DeleteSip')

    def get_parser(self, prog_name):
        parser = super(DeleteSip, self).get_parser(prog_name)
        parser.add_argument(
            'sip',
            metavar='<sip>',
            help='Sip to delete (name or ID)',
        )
#        parser.add_argument(
#            '--sid',
#            metavar='<sip-sid>',
#            help='Filter by a specific sid',
#        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

#        if parsed_args.sid:
#            sid = utils.find_resource(
#                identity_client.domains,
#                parsed_args.sid,
#            ).id
#        else:
#            sid = None

        sip = utils.find_resource(
            identity_client.projects,
            parsed_args.sip,
        )

        identity_client.projects.delete(sip.id)
        return


class ListSip(lister.Lister):
    """List sips"""
    #traceback.print_stack()

    log = logging.getLogger(__name__ + '.ListSip')

    def get_parser(self, prog_name):
        parser = super(ListSip, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--sid',
            metavar='<sip-sid>',
            help='Filter by a specific sid',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        if parsed_args.long:
            columns = ('ID', 'Name', 'Domain ID', 'Description', 'Enabled')
        else:
            columns = ('ID', 'Name')
        kwargs = {}
        if parsed_args.sid:
            kwargs['sid'] = utils.find_resource(
                identity_client.domains,
                parsed_args.sid,
            ).id
        data = identity_client.projects.list(**kwargs)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetSip(command.Command):
    """Set sip properties"""

    log = logging.getLogger(__name__ + '.SetSip')

    def get_parser(self, prog_name):
        parser = super(SetSip, self).get_parser(prog_name)
        parser.add_argument(
            'sip',
            metavar='<sip>',
            help='Sip to change (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<new-sip-name>',
            help='New sip name',
        )
        parser.add_argument(
            '--sid',
            metavar='<sip-sid>',
            help='New sid owning the sip (name or ID)',
        )
        parser.add_argument(
            '--description',
            metavar='<sip-description>',
            help='New sip description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable sip',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable sip',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add for this sip '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if (not parsed_args.name
                and not parsed_args.description
                and not parsed_args.sid
                and not parsed_args.enable
                and not parsed_args.property
                and not parsed_args.disable):
            return

        sip = utils.find_resource(
            identity_client.projects,
            parsed_args.sip,
        )

        kwargs = sip._info
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.sid:
            kwargs['sid'] = utils.find_resource(
                identity_client.sids,
                parsed_args.sid,
            ).id
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False
        if parsed_args.property:
            kwargs.update(parsed_args.property)
        if 'id' in kwargs:
            del kwargs['id']
        if 'sid_id' in kwargs:
            # Hack around borken Identity API arg names
            kwargs.update(
                {'sid': kwargs.pop('domain_id')}
            )

        identity_client.projects.update(sip.id, **kwargs)
        return


class ShowSip(show.ShowOne):
    """Show sip command"""

    log = logging.getLogger(__name__ + '.ShowSip')

    def get_parser(self, prog_name):
        parser = super(ShowSip, self).get_parser(prog_name)
        parser.add_argument(
            'sip',
            metavar='<sip>',
            help='Name or ID of sip to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        sip = utils.find_resource(identity_client.projects,
                                      parsed_args.sip)

        info = {}
        info.update(sip._info)
        return zip(*sorted(six.iteritems(info)))
