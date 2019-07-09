from pywps import ComplexInput, ComplexOutput, FORMATS
from pywps.validator.mode import MODE


def esgf_api(F):
    inputs = [
        ComplexInput('variable', 'variable',
                     abstract="",
                     supported_formats=[FORMATS.JSON],
                     min_occurs=1, max_occurs=1,
                     mode=MODE.SIMPLE
                     ),
        ComplexInput('domain', 'domain',
                     abstract="",
                     supported_formats=[FORMATS.JSON],
                     min_occurs=1, max_occurs=1,
                     mode=MODE.SIMPLE
                     ),
        ComplexInput('operation', 'operation',
                     abstract="",
                     supported_formats=[FORMATS.JSON],
                     min_occurs=0, max_occurs=1,
                     mode=MODE.SIMPLE
                     ),
    ]

    outputs = [
        ComplexOutput('output', 'Output',
                      as_reference=False,
                      supported_formats=[FORMATS.JSON], ),
    ]

    def wrapper(self):
        F(self)
        self.profile.append('ESGF-API')
        self.inputs.extend(inputs)
        self.outputs.extend(outputs)
    return wrapper
