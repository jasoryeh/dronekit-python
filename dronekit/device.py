from pymavlink import mavutil, mavwp

class Version(object):
    """
    Autopilot version and type.

    An object of this type is returned by :py:attr:`Vehicle.version`.

    The version number can be read in a few different formats. To get it in a human-readable
    format, just print `vehicle.version`.  This might print something like "APM:Copter-3.3.2-rc4".

    .. versionadded:: 2.0.3

    .. py:attribute:: major

        Major version number (integer).

    .. py:attribute::minor

        Minor version number (integer).

    .. py:attribute:: patch

        Patch version number (integer).

    .. py:attribute:: release

        Release type (integer). See the enum `FIRMWARE_VERSION_TYPE <http://mavlink.org/messages/common#http://mavlink.org/messages/common#FIRMWARE_VERSION_TYPE_DEV>`_.

        This is a composite of the product release cycle stage (rc, beta etc) and the version in that cycle - e.g. 23.

    """
    def __init__(self, raw_version, autopilot_type, vehicle_type):
        self.autopilot_type = autopilot_type
        self.vehicle_type = vehicle_type
        self.raw_version = raw_version
        if raw_version is None:
            self.major = None
            self.minor = None
            self.patch = None
            self.release = None
        else:
            self.major   = raw_version >> 24 & 0xFF
            self.minor   = raw_version >> 16 & 0xFF
            self.patch   = raw_version >> 8  & 0xFF
            self.release = raw_version & 0xFF

    def is_stable(self):
        """
        Returns True if the autopilot reports that the current firmware is a stable
        release (not a pre-release or development version).
        """
        return self.release == 255

    def release_version(self):
        """
        Returns the version within the release type (an integer).
        This method returns "23" for Copter-3.3rc23.
        """
        if self.release is None:
            return None
        if self.release == 255:
            return 0
        return self.release % 64

    def release_type(self):
        """
        Returns text describing the release type e.g. "alpha", "stable" etc.
        """
        if self.release is None:
            return None
        types = ["dev", "alpha", "beta", "rc"]
        return types[self.release >> 6]

    def __str__(self):
        prefix = ""

        if self.autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA:
            prefix += "APM:"
        elif self.autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_PX4:
            prefix += "PX4"
        else:
            prefix += "UnknownAutoPilot"

        if self.vehicle_type == mavutil.mavlink.MAV_TYPE_QUADROTOR:
            prefix += "Copter-"
        elif self.vehicle_type == mavutil.mavlink.MAV_TYPE_FIXED_WING:
            prefix += "Plane-"
        elif self.vehicle_type == mavutil.mavlink.MAV_TYPE_GROUND_ROVER:
            prefix += "Rover-"
        else:
            prefix += "UnknownVehicleType%d-" % self.vehicle_type

        if self.release_type() is None:
            release_type = "UnknownReleaseType"
        elif self.is_stable():
            release_type = ""
        else:
            # e.g. "-rc23"
            release_type = "-" + str(self.release_type()) + str(self.release_version())

        return prefix + "%s.%s.%s" % (self.major, self.minor, self.patch) + release_type


class Capabilities:
    """
    Autopilot capabilities (supported message types and functionality).

    An object of this type is returned by :py:attr:`Vehicle.capabilities`.

    See the enum
    `MAV_PROTOCOL_CAPABILITY <http://mavlink.org/messages/common#MAV_PROTOCOL_CAPABILITY_MISSION_FLOAT>`_.

    .. versionadded:: 2.0.3


    .. py:attribute:: mission_float

        Autopilot supports MISSION float message type (Boolean).

    .. py:attribute:: param_float

        Autopilot supports the PARAM float message type (Boolean).

    .. py:attribute:: mission_int

        Autopilot supports MISSION_INT scaled integer message type (Boolean).

    .. py:attribute:: command_int

        Autopilot supports COMMAND_INT scaled integer message type (Boolean).

    .. py:attribute:: param_union

        Autopilot supports the PARAM_UNION message type (Boolean).

    .. py:attribute:: ftp

        Autopilot supports ftp for file transfers (Boolean).

    .. py:attribute:: set_attitude_target

        Autopilot supports commanding attitude offboard (Boolean).

    .. py:attribute:: set_attitude_target_local_ned

        Autopilot supports commanding position and velocity targets in local NED frame (Boolean).

    .. py:attribute:: set_altitude_target_global_int

        Autopilot supports commanding position and velocity targets in global scaled integers (Boolean).

    .. py:attribute:: terrain

        Autopilot supports terrain protocol / data handling (Boolean).

    .. py:attribute:: set_actuator_target

        Autopilot supports direct actuator control (Boolean).

    .. py:attribute:: flight_termination

        Autopilot supports the flight termination command (Boolean).

    .. py:attribute:: compass_calibration

        Autopilot supports onboard compass calibration (Boolean).
    """
    def __init__(self, capabilities):
        self.mission_float                  = (((capabilities >> 0)  & 1) == 1)
        self.param_float                    = (((capabilities >> 1)  & 1) == 1)
        self.mission_int                    = (((capabilities >> 2)  & 1) == 1)
        self.command_int                    = (((capabilities >> 3)  & 1) == 1)
        self.param_union                    = (((capabilities >> 4)  & 1) == 1)
        self.ftp                            = (((capabilities >> 5)  & 1) == 1)
        self.set_attitude_target            = (((capabilities >> 6)  & 1) == 1)
        self.set_attitude_target_local_ned  = (((capabilities >> 7)  & 1) == 1)
        self.set_altitude_target_global_int = (((capabilities >> 8)  & 1) == 1)
        self.terrain                        = (((capabilities >> 9)  & 1) == 1)
        self.set_actuator_target            = (((capabilities >> 10) & 1) == 1)
        self.flight_termination             = (((capabilities >> 11) & 1) == 1)
        self.compass_calibration            = (((capabilities >> 12) & 1) == 1)


class VehicleMode(object):
    """
    This object is used to get and set the current "flight mode".

    The flight mode determines the behaviour of the vehicle and what commands it can obey.
    The recommended flight modes for *DroneKit-Python* apps depend on the vehicle type:

    * Copter apps should use ``AUTO`` mode for "normal" waypoint missions and ``GUIDED`` mode otherwise.
    * Plane and Rover apps should use the ``AUTO`` mode in all cases, re-writing the mission commands if "dynamic"
      behaviour is required (they support only a limited subset of commands in ``GUIDED`` mode).
    * Some modes like ``RETURN_TO_LAUNCH`` can be used on all platforms. Care should be taken
      when using manual modes as these may require remote control input from the user.

    The available set of supported flight modes is vehicle-specific (see
    `Copter Modes <http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/>`_,
    `Plane Modes <http://plane.ardupilot.com/wiki/flying/flight-modes/>`_,
    `Rover Modes <http://rover.ardupilot.com/wiki/configuration-2/#mode_meanings>`_). If an unsupported mode is set the script
    will raise a ``KeyError`` exception.

    The :py:attr:`Vehicle.mode` attribute can be queried for the current mode.
    The code snippet below shows how to observe changes to the mode and then read the value:

    .. code:: python

        #Callback definition for mode observer
        def mode_callback(self, attr_name):
            print "Vehicle Mode", self.mode

        #Add observer callback for attribute `mode`
        vehicle.add_attribute_listener('mode', mode_callback)

    The code snippet below shows how to change the vehicle mode to AUTO:

    .. code:: python

        # Set the vehicle into auto mode
        vehicle.mode = VehicleMode("AUTO")

    For more information on getting/setting/observing the :py:attr:`Vehicle.mode`
    (and other attributes) see the :ref:`attributes guide <vehicle_state_attributes>`.

    .. py:attribute:: name

        The mode name, as a ``string``.
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "VehicleMode:%s" % self.name

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other


class SystemStatus(object):
    """
    This object is used to get and set the current "system status".

    An object of this type is returned by :py:attr:`Vehicle.system_status`.

    .. py:attribute:: state

        The system state, as a ``string``.
    """

    def __init__(self, state):
        self.state = state

    def __str__(self):
        return "SystemStatus:%s" % self.state

    def __eq__(self, other):
        return self.state == other

    def __ne__(self, other):
        return self.state != other