import os
import json

import xarray as xr

from pywps import Process
from pywps import ComplexInput, ComplexOutput, FORMATS, Format
from pywps.inout.basic import SOURCE_TYPE
from pywps.validator.mode import MODE
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError
from owslib_esgfwps import Variables, Domains, Outputs, Output

from .base import esgf_api
from pelican.tools import subset, simple_plot_preview

import logging
LOGGER = logging.getLogger("PYWPS")


class PelicanSubset(Process):
    """
    Notes
    -----

    subset netcdf files
    """
    @esgf_api
    def __init__(self):
        inputs = []
        outputs = [
            ComplexOutput('nc', 'NetCDF',
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF], ),
            ComplexOutput('preview', 'Preview',
                          abstract='Preview of subsetted Dataset.',
                          as_reference=True,
                          supported_formats=[Format('image/png')],),
        ]
        super(PelicanSubset, self).__init__(
            self._handler,
            identifier='pelican_subset',
            title='xarray.subset',
            abstract="subset netcdf files",
            version='2.0.0',
            metadata=[
                Metadata('ESGF Compute API', 'https://github.com/ESGF/esgf-compute-api'),
                Metadata('ESGF Compute WPS', 'https://github.com/ESGF/esgf-compute-wps'),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True)

    def _handler(self, request, response):
        # subsetting
        response.update_status('PyWPS Process started.', 0)
        # get variable and domain from json input
        variable = Variables.from_json(json.loads(request.inputs['variable'][0].data)).variables[0]
        domain = Domains.from_json(json.loads(request.inputs['domain'][0].data)).domains[0]

        output_file = None
        # TODO: Use chunks for parallel processing with dask.distributed
        try:
            output_file = subset(variable.uri, variable.var_name, domain.dimensions, self.workdir)
            response.outputs['nc'].file = output_file
            response.outputs['output'].data = Outputs([Output(uri='http://test.nc')]).json
            response.update_status('subsetting done.', 70)
        except Exception:
            LOGGER.exception('subsetting failed')
            raise ProcessError("subsetting failed.")
        # plot preview
        try:
            response.outputs['preview'].file = simple_plot_preview(
                output_file,
                variable.var_name,
                self.workdir)
            response.update_status('plot done.', 80)
        except Exception:
            LOGGER.exception('plot failed')
            response.outputs['preview'].data = 'plot failed'
            response.update_status('plot failed.', 80)
        # done
        response.update_status('PyWPS Process completed.', 100)
        return response
