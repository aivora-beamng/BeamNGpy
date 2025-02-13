import pytest
import socket
from beamngpy import BeamNGpy, Vehicle, Scenario, ScenarioObject, setup_logging


@pytest.fixture()
def beamng():
    beamng = BeamNGpy('localhost', 64256)
    return beamng


def test_quats(beamng):
    with beamng as bng:
        setup_logging()

        scenario = Scenario('smallgrid', 'test_quat')

        blue_etk = Vehicle('ego_vehicle',
                      model='etk800',
                      color='Blue',
                      licence="angle")
        scenario.add_vehicle(blue_etk, pos=(0, 0, 0), rot=(0, 0, 0))

        blue_etk = Vehicle('ego_vehicle2',
                      model='etk800',
                      color='Green',
                      license="quat")
        rot_quat = (-0.00333699025, -0.00218820246, -0.689169466, 0.724589229)
        scenario.add_vehicle(blue_etk, pos=(5, 0, 0), rot_quat=rot_quat)

        rb = ScenarioObject(oid='roadblock',
                            name='sawhorse',
                            otype='BeamNGVehicle',
                            pos=(-10, -5, 0),
                            rot=(0, 0, 0),
                            scale=(1, 1, 1),
                            JBeam='sawhorse',
                            datablock="default_vehicle"
                            )
        scenario.add_object(rb)

        cn = ScenarioObject(oid='cones',
                            name='cones',
                            otype='BeamNGVehicle',
                            pos=(0, -5, 0),
                            rot=None,
                            rot_quat=(0, 0, 0, 1),
                            scale=(1, 1, 1),
                            JBeam='cones',
                            datablock="default_vehicle"
                            )
        scenario.add_object(cn)

        scenario.make(beamng)

        bng.load_scenario(scenario)
        bng.start_scenario()

        white_etk = Vehicle('ego_vehicle3', model='etk800', color='White')
        bng.spawn_vehicle(white_etk, (-10, 0, 0), (0, 0, 0))

        pickup = Vehicle('ego_vehicle4', model='pickup')
        pos = (-15, 0, 0)
        bng.spawn_vehicle(pickup, pos, None, rot_quat=(0, 0, 0, 1))
        resp = bng.get_current_vehicles()
        assert len(resp) == 6

        pickup.connect(bng)

        pickup.poll_sensors()
        pos_before = pickup.state['pos']
        bng.teleport_vehicle(pickup.vid, pos, rot=(0, 45, 0))
        pickup.poll_sensors()
        pos_after = pickup.state['pos']
        assert(pos_before != pos_after)

        pickup.poll_sensors()
        pos_before = pickup.state['pos']
        rot_quat = (-0.00333699025, -0.00218820246, -0.689169466, 0.724589229)
        bng.teleport_vehicle(pickup.vid, pos, rot_quat=rot_quat)
        pickup.poll_sensors()
        pos_after = pickup.state['pos']
        assert(pos_before != pos_after)

        try:
            bng.teleport_scenario_object(rb, (-10, 5, 0), rot=(-45, 0, 0))
            assert True
        except socket.timeout:
            assert False

        try:
            rot_quat = (-0.003337, -0.0021882, -0.6891695, 0.7245892)
            bng.teleport_scenario_object(rb, (-10, 5, 0), rot_quat=rot_quat)
            assert True
        except socket.timeout:
            assert False


if __name__ == '__main__':
    bng = BeamNGpy('localhost', 64256)
    test_quats(bng)
