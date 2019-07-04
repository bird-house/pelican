from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for, resource_file, get_output
from pelican.processes.wps_esgf_subset import PelicanSubset
import owslib.wps
from owslib_esgfwps import Domain, Variable, Dimension

NC_FILE_URL = resource_file('test.nc')

variable = Variable(var_name='meantemp', uri=NC_FILE_URL, name='test')
domain = Domain([
    Dimension('time', 0, 10, crs='indices'),
])


def test_wps_esgf_subset():
    client = client_for(Service(processes=[PelicanSubset()]))
    datainputs = "variable={variable};" \
                 "domain={domain}".format(variable=variable.value, domain=domain.value)
    resp = client.get(
        service='wps', request='execute', version='1.0.0',
        identifier='pelican_subset',
        datainputs=datainputs)
    assert_response_success(resp)
    out = get_output(resp.xml)
    assert out['preview'] != 'plot failed'
