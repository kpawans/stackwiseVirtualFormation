'''
ls.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pyats-support-ext@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import logging
from pyats import aetest
# create a logger for this module
logger = logging.getLogger(__name__)
from svlservices.svlservice import StackWiseVirtual
from pyats.aetest.steps import Steps

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        '''
        establishes connection to all your testbed devices.
        '''
        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        #initilize StackWiseVirtual Class
        svl_handle = StackWiseVirtual(testbed)
        print(svl_handle)
        self.parent.parameters['svl_handle'] = svl_handle

class svlformation(aetest.Testcase):
    '''svlformation

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self,svl_handle):
        svl_handle.get_device_pairs()

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test_pre_check_stackwise_virtual_links(self,svl_handle):
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Link Precheck",continue_= True) as step:
                if not svl_handle.check_links(stackpair):
                    Logger.error("The devices provided to be paired into SVL does not have any links connected to eachothers")
                    result=False
                    step.failed("The Prechecks failed. Fix Links before script run", goto = ['CommonCleanup'])
        if not result:
            self.failed("Precheck for links correctness failed on some of the Stackwise Virtual Pairs")

    @aetest.test
    def test_validate_console_connectivity_to_switches(self,svl_handle):
        '''
            This is a precheck test to check if connesol connectivity is established with teh devoces
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of console connectivity on Stackwise Virtual device pairs",continue_= True) as step:
                if not svl_handle.connect_to_stackpair(stackpair):
                    result=False
                    step.failed("Could not connect to devices, Can not proceed. for stackwise virtual pair :{}".format(stackpair))
        if not result:
            self.failed("Console connectivity to some or all of the devices could not  be established", goto = ['CommonCleanup'])

    @aetest.test
    def test_preches_validate_platform_and_version_match_and_minimum_version_req(self,svl_handle):
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Platform and Version req precheck",continue_= True) as step:
                if not svl_handle.check_min_version_req(stackpair):
                    result=False
                    step.failed("Minimum Version and platform pre-check failed ", goto = ['CommonCleanup'])
        if not result:
            self.failed("Minimum Version and Platform check failed.", goto = ['CommonCleanup'])

    @aetest.test
    def test_configure_stackwise_virtual_configs_and_validate(self,svl_handle):
        '''
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Stackwise Virtual config") as step:
                if not svl_handle.configure_svl_step1(stackpair):
                    result=False
                    step.failed("Step1 Configure the step 1 config, switch number and domain configs on switches, failed")

                if not svl_handle.save_config_and_reload(stackpair):
                    result=False
                    step.failed("Step2 Save config and reload the switches, failed")

                if not svl_handle.configure_svl_step2_svllinkconfig(stackpair):
                    result=False
                    step.failed("Step3 Config stackwise Virtual links on switches, failed.")

                if not svl_handle.save_config_and_reload(stackpair):
                    result=False
                    step.failed("Step4 Save config and reload the switches, failed.")

                if not svl_handle.configure_svl_step3_dad_linkconfig(stackpair):
                    result=False
                    step.failed("Step5 Configuring stackwise Virtual Dual Active Detection Links, failed.")

                if not svl_handle.save_config_and_reload(stackpair):
                    result=False
                    step.failed("Step6 Save config and reload the switches, failed.")

                if not svl_handle.configure_svl_step4_validate_svl(stackpair):
                    result=False
                    step.failed("Step7 Validate Stackwise Virtual, failed.")

        if not result:
            self.failed("Minimum Version and Platform check failed.")

    @aetest.cleanup
    def cleanup(self):
        pass
    
class CommonCleanup(aetest.CommonCleanup):
    '''CommonCleanup Section

    < common cleanup docstring >

    '''

    # uncomment to add new subsections
    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass

if __name__ == '__main__':
    # for stand-alone execution
    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed',
                        help = 'testbed YAML file',
                        type = topology.loader.load,
                        default = None)

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed = args.testbed)

