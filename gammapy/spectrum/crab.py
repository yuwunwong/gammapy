# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from astropy import units as u
from .models import PowerLaw, LogParabola, ExponentialCutoffPowerLaw, SpectralModel

__all__ = ["create_crab_spectral_model"]

# HESS publication: 2006A&A...457..899A
hess_pl = {
    "amplitude": 3.45e-11 * u.Unit("1 / (cm2 s TeV)"),
    "index": 2.63,
    "reference": 1 * u.TeV,
}

hess_ecpl = {
    "amplitude": 3.76e-11 * u.Unit("1 / (cm2 s TeV)"),
    "index": 2.39,
    "lambda_": 1 / (14.3 * u.TeV),
    "reference": 1 * u.TeV,
}

# HEGRA publication : 2004ApJ...614..897A
hegra = {
    "amplitude": 2.83e-11 * u.Unit("1 / (cm2 s TeV)"),
    "index": 2.62,
    "reference": 1 * u.TeV,
}

# MAGIC publication: 2015JHEAp...5...30A
# note that in the paper the beta of the LogParabola is given as negative in
# Table 1 (pag. 33), but should be positive to match gammapy LogParabola expression
# Also MAGIC uses log10 in the LogParabola expression, gammapy uses ln, hence
# the conversion factor
magic_lp = {
    "amplitude": 3.23e-11 * u.Unit("1 / (cm2 s TeV)"),
    "alpha": 2.47,
    "beta": 0.24 / np.log(10),
    "reference": 1 * u.TeV,
}

magic_ecpl = {
    "amplitude": 3.80e-11 * u.Unit("1 / (cm2 s TeV)"),
    "index": 2.21,
    "lambda_": 1 / (6.0 * u.TeV),
    "reference": 1 * u.TeV,
}


class MeyerCrabModel(SpectralModel):
    """Meyer 2010 log polynomial Crab spectral model.

    See 2010A%26A...523A...2M, Appendix D.
    """

    coefficients = np.array([-0.00449161, 0, 0.0473174, -0.179475, -0.53616, -10.2708])

    @staticmethod
    def evaluate(energy):
        polynomial = np.poly1d(MeyerCrabModel.coefficients)
        log_energy = np.log10(energy.to_value("TeV"))
        log_flux = polynomial(log_energy)
        flux = u.Quantity(np.power(10, log_flux), "erg / (cm2 s)", copy=False)
        return flux / energy ** 2


def create_crab_spectral_model(reference="meyer"):
    """Create the Crab nebula spectral model depending of the reference given.

    The Crab nebula is often used as a standard candle in gamma-ray astronomy.
    Fluxes and sensitivities are often quoted relative to the Crab spectrum.

    The following references are available:

    * 'meyer', https://ui.adsabs.harvard.edu/abs/2010A%26A...523A...2M, Appendix D
    * 'hegra', https://ui.adsabs.harvard.edu/abs/2000ApJ...539..317A
    * 'hess_pl' and 'hess_ecpl': https://ui.adsabs.harvard.edu/abs/2006A%26A...457..899A
    * 'magic_lp' and 'magic_ecpl': https://ui.adsabs.harvard.edu/abs/2015JHEAp...5...30A

    Parameters
    ----------
    reference : {'meyer', 'hegra', 'hess_pl', 'hess_ecpl', 'magic_lp', 'magic_ecpl'}
        Which reference to use for the spectral model.

    Examples
    --------
    Let's first import what we need::

        import astropy.units as u
        from gammapy.spectrum import create_crab_spectral_model
        from gammapy.spectrum.models import PowerLaw

    Plot the 'hess_ecpl' reference Crab spectrum between 1 TeV and 100 TeV::

        crab_hess_ecpl = create_crab_spectral_model('hess_ecpl')
        crab_hess_ecpl.plot([1, 100] * u.TeV)

    Use a reference crab spectrum as unit to measure a differential flux (at 10 TeV)::

        >>> pwl = PowerLaw(index=2.3, amplitude=1e-12 * u.Unit('1 / (cm2 s TeV)'), reference=1 * u.TeV)
        >>> crab = create_crab_spectral_model('hess_pl')
        >>> energy = 10 * u.TeV
        >>> dnde_cu = (pwl(energy) / crab(energy)).to('%')
        >>> print(dnde_cu)
        6.19699156377 %

    And the same for integral fluxes (between 1 and 10 TeV)::

        >>> # compute integral flux in crab units
        >>> emin, emax = [1, 10] * u.TeV
        >>> flux_int_cu = (pwl.integral(emin, emax) / crab.integral(emin, emax)).to('%')
        >>> print(flux_int_cu)
        3.5350582166 %
    """

    if reference == "meyer":
        model = MeyerCrabModel()
    elif reference == "hegra":
        model = PowerLaw(**hegra)
    elif reference == "hess_pl":
        model = PowerLaw(**hess_pl)
    elif reference == "hess_ecpl":
        model = ExponentialCutoffPowerLaw(**hess_ecpl)
    elif reference == "magic_lp":
        model = LogParabola(**magic_lp)
    elif reference == "magic_ecpl":
        model = ExponentialCutoffPowerLaw(**magic_ecpl)
    else:
        fmt = "Invalid reference: {!r}. Choices: {!r}"
        references = [
            "meyer",
            "hegra",
            "hess_pl",
            "hess_ecpl",
            "magic_lp",
            "magic_ecpl",
        ]
        raise ValueError(fmt.format(reference, references))

    return model
