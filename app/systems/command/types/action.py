from django.conf import settings
from django.core.management.base import CommandError

from systems.command import base, args, messages
from systems.command.mixins import command, log
from systems.api import client
from utility.runtime import Runtime
from utility import display

import threading
import time
import logging
import copy


logger = logging.getLogger(__name__)


class ActionResult(object):

    def __init__(self, messages = []):
        self.stream = messages
        self.named = {}
        self.errors = []

        self.add(messages)


    @property
    def active_user(self):
        return self.get_named_data('active_user')


    def add(self, messages):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        for msg in messages:
            self.stream.append(msg)

            if msg.name:
                self.named[msg.name] = msg

            if msg.type == 'ErrorMessage':
                self.errors.append(msg)


    @property
    def aborted(self):
        return len(self.errors) > 0

    def error_message(self):
        messages = []
        for msg in self.errors:
            messages.append(msg.format())

        return "\n".join(messages)


    def get_named_data(self, name):
        msg = self.named.get(name, None)
        if msg:
            return msg.data
        return None


class ActionCommand(
    command.ExecMixin,
    log.LogMixin,
    base.AppBaseCommand
):
    def get_action_result(self, messages = []):
        return ActionResult(messages)


    def parse_base(self):
        super().parse_base()

        if not Runtime.api():
            self.parse_local()


    def parse_local(self):
        self.parse_flag('local', '--local', "force command to run in local environment")

    @property
    def local(self):
        return self.options.get('local', False)


    def confirm(self):
        # Override in subclass
        pass

    def _exec_wrapper(self):
        try:
            if self.verbosity > 1:
                self.data("> active user", self.active_user.name, 'active_user')
                self.info('-----------------------------------------')

            self.exec()

        except Exception as e:
            if not isinstance(e, CommandError):
                self.error(e,
                    terminate = False,
                    traceback = display.format_exception_info()
                )
        finally:
            self.flush()


    def exec(self):
        # Override in subclass
        pass

    def exec_local(self, name, options = {}):
        command = base.find_command(name, self)
        success = True

        options = command.format_fields(copy.deepcopy(options))
        command.set_options(options)

        log_entry = self.log_exec(name, command.options.export())
        try:
            command.exec()
        except Exception as e:
            success = False
            raise e
        finally:
            log_entry.messages = command.get_messages(True)
            log_entry.set_status(success)
            log_entry.save()

    def exec_remote(self, env, name, options = {}, display = True):
        result = self.get_action_result()
        command = base.find_command(name, self)
        success = True

        options = {
            key: options[key] for key in options if key not in (
                'local',
                'no_color',
                'version'
            )
        }
        log_entry = self.log_exec(name, options)

        def message_callback(data):
            msg = self.create_message(data, decrypt = True)

            if display and (self.verbosity > 0 or isinstance(msg, messages.ErrorMessage)):
                msg.display()

            result.add(msg)
            command.queue(msg)

        try:
            api = client.API(env.host, env.port, env.user, env.token,
                params_callback = command.preprocess_handler,
                message_callback = message_callback
            )
            api.execute(name, options)
            command.postprocess_handler(result)

            if result.aborted:
                success = False
                raise CommandError()
        finally:
            log_entry.messages = command.get_messages(True)
            log_entry.set_status(success)
            log_entry.save()

        return result


    def preprocess(self, params):
        # Override in subclass
        pass

    def preprocess_handler(self, params):
        self.preprocess(params)

    def postprocess(self, result):
        # Override in subclass
        pass

    def postprocess_handler(self, result):
        if not result.aborted:
            self.postprocess(result)


    def handle(self, options):
        env = self.get_env()
        self.set_options(options)

        if not self.local and env and env.host and self.server_enabled() and self.remote_exec():
            if self.verbosity > 1:
                self.data("> environment ({})".format(self.warning_color(env.host)), env.name)
                self.info('=========================================')

            self.confirm()
            self.exec_remote(env, self.get_full_name(), options, display = True)
        else:
            if env and self.verbosity > 1:
                self.data('> environment', env.name)
                self.info('=========================================')

            self.confirm()

            success = True
            log_entry = self.log_exec(
                self.get_full_name(),
                self.options.export()
            )
            try:
                self.exec()
            except Exception as e:
                success = False
                raise e
            finally:
                log_entry.messages = self.get_messages(True)
                log_entry.set_status(success)
                log_entry.save()


    def handle_api(self, options):
        env = self.get_env()
        self.set_options(options)

        success = True
        log_entry = self.log_exec(
            self.get_full_name(),
            self.options.export()
        )
        action = threading.Thread(target = self._exec_wrapper)
        action.start()

        while True:
            time.sleep(0.25)
            logger.debug("Checking messages")

            for data in iter(self.messages.get, None):
                log_entry.messages.append(data)

                msg = self.create_message(data, decrypt = False)
                if isinstance(msg, messages.ErrorMessage):
                    success = False

                package = msg.to_package()
                logger.debug("Processing message: {}".format(package))
                yield package

            if not action.is_alive():
                logger.debug("Command thread is no longer active")
                break

        log_entry.set_status(success)
        log_entry.save()
