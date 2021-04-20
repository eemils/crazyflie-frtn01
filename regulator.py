import logging
import time
import numpy as np
import transformations as trans
from PController import PController
import threading
from threading import Thread

import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig


logging.basicConfig(level=logging.ERROR)


class Regulator(threading.Thread):

    def __init__(self, link_uri):
        Thread.__init__(self)
        """Setting up some paramters"""
        self.set_up_controllers()
        self.set_up_limits()

        """ Initialize with the specified link_uri """

        self.cf = Crazyflie(rw_cache='./cache')

        # add a bunch of callbacks to initialize logging or
        # print out connection problems
        self.cf.connected.add_callback(self._connected)
        self.cf.disconnected.add_callback(self._disconnected)
        self.cf.connection_failed.add_callback(self._connection_failed)
        self.cf.connection_lost.add_callback(self._connection_lost)

        # Control period. [ms]
        self.period_in_ms = 20  # a random number
        # Pose estimate from the Kalman filter
        self.pos = np.r_[0.0, 0.0, 0.0]
        self.vel = np.r_[0.0, 0.0, 0.0]
        self.attq = np.r_[0.0, 0.0, 0.0, 1.0]
        self.R = np.eye(3)

        # Attitide (roll, pitch, yaw) from stabilizer
        self.stab_att = np.r_[0.0, 0.0, 0.0]

        # This makes Python exit when this is the only thread alive.
        self.daemon = True

        # Start connection with drone!
        print('Trying to connect to %s' % link_uri)
        self.cf.open_link(link_uri)

    def set_up_controllers(self):
        """ Setting up controllers """
        self.thrust_controller = PController()

    def set_up_limits(self):
        """ Setting up limits for signals """
        self.thrust_limit = [0,65535] # 65535 corresponding to 2g


    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        log_stab_att = LogConfig(name='Stabilizer', period_in_ms=self.period_in_ms)
        log_stab_att.add_variable('stabilizer.roll', 'float')
        log_stab_att.add_variable('stabilizer.pitch', 'float')
        log_stab_att.add_variable('stabilizer.yaw', 'float')
        self.cf.log.add_config(log_stab_att)

        log_pos = LogConfig(name='Kalman Position', period_in_ms=self.period_in_ms)
        log_pos.add_variable('kalman.stateX', 'float')
        log_pos.add_variable('kalman.stateY', 'float')
        log_pos.add_variable('kalman.stateZ', 'float')
        self.cf.log.add_config(log_pos)

        log_vel = LogConfig(name='Kalman Velocity', period_in_ms=self.period_in_ms)
        log_vel.add_variable('kalman.statePX', 'float')
        log_vel.add_variable('kalman.statePY', 'float')
        log_vel.add_variable('kalman.statePZ', 'float')
        self.cf.log.add_config(log_vel)

        log_att = LogConfig(name='Kalman Attitude',
                            period_in_ms=self.period_in_ms)
        log_att.add_variable('kalman.q0', 'float')
        log_att.add_variable('kalman.q1', 'float')
        log_att.add_variable('kalman.q2', 'float')
        log_att.add_variable('kalman.q3', 'float')
        self.cf.log.add_config(log_att)

        if log_stab_att.valid and log_pos.valid and log_vel.valid and log_att.valid:
            log_stab_att.data_received_cb.add_callback(self._log_data_stab_att)
            log_stab_att.error_cb.add_callback(self._log_error)
            log_stab_att.start()

            log_pos.data_received_cb.add_callback(self._log_data_pos)
            log_pos.error_cb.add_callback(self._log_error)
            log_pos.start()

            log_vel.error_cb.add_callback(self._log_error)
            log_vel.data_received_cb.add_callback(self._log_data_vel)
            log_vel.start()

            log_att.error_cb.add_callback(self._log_error)
            log_att.data_received_cb.add_callback(self._log_data_att)
            log_att.start()
        else:
            raise RuntimeError('One or more of the variables in the configuration was not'
                               'found in log TOC. Will not get any position data.')
        # Start a separate thread to run the example
        # Do not hijack the calling thread!
        Thread(target=self._run).start()

    def _disconnected(self, link_uri):
        print('Disconnected from %s' % link_uri)

    def _connection_failed(self, link_uri, msg):
        print('Connection to %s failed: %s' % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _log_data_stab_att(self, timestamp, data, logconf):
        self.stab_att = np.r_[data['stabilizer.roll'],
                              data['stabilizer.pitch'],
                              data['stabilizer.yaw']]

    def _log_data_pos(self, timestamp, data, logconf):
        self.pos = np.r_[data['kalman.stateX'],
                         data['kalman.stateY'],
                         data['kalman.stateZ']]

    def _log_data_vel(self, timestamp, data, logconf):
        vel_bf = np.r_[data['kalman.statePX'],
                       data['kalman.statePY'],
                       data['kalman.statePZ']]
        self.vel = np.dot(self.R, vel_bf)

    def _log_data_att(self, timestamp, data, logconf):
        # NOTE q0 is real part of Kalman state's quaternion, but
        # transformations.py wants it as last dimension.
        self.attq = np.r_[data['kalman.q1'], data['kalman.q2'],
                          data['kalman.q3'], data['kalman.q0']]
        # Extract 3x3 rotation matrix from 4x4 transformation matrix
        self.R = trans.quaternion_matrix(self.attq)[:3, :3]
        #r, p, y = trans.euler_from_quaternion(self.attq)

    def _log_error(self, logconf, msg):
        print('Error when logging %s: %s' % (logconf.name, msg))

    def make_position_sanity_check(self):
        # We assume that the position from the LPS should be
        # [-20m, +20m] in xy and [0m, 5m] in z
        if np.max(np.abs(self.pos[:2])) > 20 or self.pos[2] < 0 or self.pos[2] > 5:
            raise RuntimeError('Position estimate out of bounds', self.pos)

    def reset_estimator(self):
        self.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        self.cf.param.set_value('kalman.resetEstimation', '0')
        # Sleep a bit, hoping that the estimator will have converged
        # Should be replaced by something that actually checks...
        time.sleep(1.5)

    def _run(self):

        print('Waiting for position estimate to be good enough...')
        self.reset_estimator()
        self.make_position_sanity_check();
        #first command has to be null for safety
        self.cf.commander.send_setpoint(0, 0, 0, 0)


        while True:
            # send setpoint as (roll, pitch, yaw, thrust)
            # thrust is in the range [0,65535] corresponding to 0 thrust
            # and 2g of vertical thrust
            tid = time.time()
            tidCurr = tid
            while tidCurr<(tid+10):
                self.cf.commander.send_setpoint(0, 0, 0, 30000)
                tidCurr = time.time()
                print(self.pos)
                time.sleep(0.1)


            self.cf.commander.send_setpoint(0, 0, 0, 15000)

            # print position estimate for 10 seconds
            # the variable self.pos is updated periodically
            # according tothe variable period_in_ms
            for i in range(5):
                print(self.pos)
                time.sleep(0.1)

            # Make sure that the last packet leaves before the link is closed
            # since the message queue is not flushed before closing
            time.sleep(0.1)
        self.cf.close_link()


if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    # needed to use the crazyradio
    cflib.crtp.init_drivers(enable_debug_driver=False)

    # create SimpleExample object and run it!
    le = SimpleExample(URI)
