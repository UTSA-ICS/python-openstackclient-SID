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

"""Sid action implementations"""
import traceback

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateSid(show.ShowOne):
    """Create new sid"""

    log = logging.getLogger(__name__ + '.CreateSid')

    def get_parser(self, prog_name):
        parser = super(CreateSid, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<sid-name>',
            help='New sid name',
        )
        parser.add_argument(
            '--members',
            metavar='<sid-members>',
            help='Sid member domains(name or ID)',
        )
        parser.add_argument(
            '--description',
            metavar='<sid-description>',
            help='New sid description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable sid',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable sid',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add for this sid '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

	#print("openstack client: parsed_args.members=", parsed_args.members)
        if parsed_args.members:
	    members_list=[]
	    members_list=parsed_args.members.split(',')
	    #print("openstack client: members_list=", members_list)
	    members_id_list=[]
	    for element in members_list:
                member_id = utils.find_resource(
                    identity_client.domains,
                    element,
                ).id
		members_id_list.append(member_id)
	    members = members_id_list
        else:
            members = None

	#print("openstack client: members_id_list=", members_id_list)

        enabled = True
        if parsed_args.disable:
            enabled = False
        kwargs = {}
        if parsed_args.property:
            kwargs = parsed_args.property.copy()

        sid = identity_client.sids.create(
            name=parsed_args.name,
            members=members,
            description=parsed_args.description,
            enabled=enabled,
            **kwargs
        )

        info = {}
        info.update(sid._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteSid(command.Command):
    """Delete sid"""

    log = logging.getLogger(__name__ + '.DeleteSid')

    def get_parser(self, prog_name):
        parser = super(DeleteSid, self).get_parser(prog_name)
        parser.add_argument(
            'sid',
            metavar='<sid>',
            help='Sid to delete (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        sid = utils.find_resource(
            identity_client.domains,
            parsed_args.sid,
        )

        identity_client.sids.delete(sid.id)
        return


class ListSid(lister.Lister):
    """List sids"""
    #traceback.print_stack()

    log = logging.getLogger(__name__ + '.ListSid')

    def get_parser(self, prog_name):
        parser = super(ListSid, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--members',
            metavar='<sid-members>',
            help='Filter by a specific members',
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
        if parsed_args.members:
            kwargs['members'] = utils.find_resource(
                identity_client.memberss,
                parsed_args.members,
            ).id
        data = identity_client.sids.list(**kwargs)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetSid(command.Command):
    """Set sid properties"""

    log = logging.getLogger(__name__ + '.SetSid')

    def get_parser(self, prog_name):
        parser = super(SetSid, self).get_parser(prog_name)
        parser.add_argument(
            'sid',
            metavar='<sid>',
            help='Sid to change (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<new-sid-name>',
            help='New sid name',
        )
        parser.add_argument(
            '--members',
            metavar='<sid-members>',
            help='New members owning the sid (name or ID)',
        )
        parser.add_argument(
            '--description',
            metavar='<sid-description>',
            help='New sid description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable sid',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable sid',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add for this sid '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if (not parsed_args.name
                and not parsed_args.description
                and not parsed_args.members
                and not parsed_args.enable
                and not parsed_args.property
                and not parsed_args.disable):
            return

        sid = utils.find_resource(
            identity_client.sids,
            parsed_args.sid,
        )

        kwargs = sid._info
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.members:
            kwargs['members'] = utils.find_resource(
                identity_client.memberss,
                parsed_args.members,
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
        if 'members_id' in kwargs:
            # Hack around borken Identity API arg names
            kwargs.update(
                {'members': kwargs.pop('members_id')}
            )

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
            help='Name or ID of sid to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        sid = utils.find_resource(identity_client.sids,
                                      parsed_args.sid)

        info = {}
        info.update(sid._info)
        return zip(*sorted(six.iteritems(info)))
