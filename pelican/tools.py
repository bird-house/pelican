import os

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy import config

from netCDF4 import Dataset

import xarray as xr

from subprocess import check_output, CalledProcessError

import logging
LOGGER = logging.getLogger("PYWPS")


def ncdump(dataset):
    '''
    Returns the metadata of the dataset

    Code taken from https://github.com/ioos/compliance-checker-web
    '''

    try:
        output = check_output(['ncdump', '-h', dataset])
        if not isinstance(output, str):
            output = output.decode('utf-8')
        lines = output.split('\n')
        # replace the filename for safety
        dataset_id = os.path.basename(dataset)  # 'uploaded-file'
        lines[0] = 'netcdf {} {{'.format(dataset_id)
        # decode to ascii
        filtered_lines = ['{}\n'.format(line) for line in lines]
    except Exception as err:
        LOGGER.error("Could not generate ncdump: {}".format(err))
        return "Error: generating ncdump failed"
    return filtered_lines


def plot_preview(dataset, variable, title=None, output_dir='.'):
    ds = Dataset(dataset)
    timestep = 0
    # values
    values = ds.variables[variable][timestep, :, :]
    lats = ds.variables['lat'][:]
    lons = ds.variables['lon'][:]
    # axxis
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    ax.set_global()
    # plot
    plt.contourf(lons, lats, values, 60, transform=ccrs.PlateCarree())
    # Save the plot by calling plt.savefig() BEFORE plt.show()
    plot_name = os.path.basename(dataset)
    title = title or plot_name
    output = os.path.join(output_dir, plot_name[:-3] + ".png")
    plt.title(title)
    plt.savefig(output)
    plt.show()
    plt.close()
    return output


def simple_plot_preview(dataset, variable, output_dir='.'):
    """Plot map of first time step."""
    fn = os.path.join(output_dir, 'preview.png')
    with xr.open_dataset(dataset, decode_cf=False) as ds:
        da = ds[variable]
        fig, ax = plt.subplots(1, 1)
        da.isel(time=0).plot(ax=ax)
        fig.savefig(fn)
        plt.close()
    return fn


def subset(dataset, variable, dimensions, output_dir='.'):
    output_file = os.path.join(output_dir, 'out.nc')
    with xr.open_dataset(dataset, decode_cf=False) as ds:
        da = ds[variable]
        sl = {}
        for dim_name, dim in dimensions.items():
            sl = {dim_name: slice(dim.start, dim.end, dim.step)}
            if dim.crs == 'values':
                da = da.sel(**sl)
            elif dim.crs == 'indices':
                da = da.isel(**sl)
        if 0 in da.shape:
            raise ValueError("Subsetting operation yields no values for `{}` dimension.".
                             format(da.dims[da.shape.index(0)]))

        da.to_netcdf(output_file)
    return output_file
