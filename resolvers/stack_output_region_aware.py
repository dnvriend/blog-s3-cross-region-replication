import os, json
from sceptre.resolvers.stack_output import StackOutput
from sceptre.connection_manager import ConnectionManager
from sceptre.environment import Environment

class StackOutputRegionAware(StackOutput):

    def __init__(self, *args, **kwargs):
        super(StackOutputRegionAware, self).__init__(*args, **kwargs)
        self.real_stack_output_resolver = super(StackOutputRegionAware, self).resolve

    def resolve(self):
        source_stack_path = self.dependency_stack_name
        paths = source_stack_path.split('/')
        source_env_path = '/'.join(paths[0:-1])
        source_stack_name = paths[-1]

        options = None
        if 'user_variables' in self.environment_config:
            options = {'user_variables': self.environment_config['user_variables']}
        environment = Environment(self.environment_config.sceptre_dir, source_env_path, options=options)
        source_stack = environment.stacks[source_stack_name]

        region = source_stack.environment_config['region']
        profile = source_stack.environment_config['profile']

        old_connection_manager = self.connection_manager
        if self.connection_manager.region != region or self.connection_manager.profile != profile:
            print(f"Source stack '{source_stack}' located in '{profile}/{region}', making sure underying CloudFormation stack is descibed in this region and not in '{self.connection_manager.profile}/{self.connection_manager.region}' where resolving the output")

            self.connection_manager = ConnectionManager(
                region=region, iam_role=self.connection_manager.iam_role,
                profile=profile)
        else:
            print(f"Source stack '{source_stack_path}' is located in the same region as where resolving the output: '{region}'")

        output_value = self.real_stack_output_resolver()
        self.connection_manager = old_connection_manager

        print(f"OutputValue fetched: {output_value}")

        return output_value
