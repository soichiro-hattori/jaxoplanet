import jax.numpy as jnp
import pytest
from jaxoplanet import light_curves, orbits
from jaxoplanet.test_utils import assert_allclose


def test_keplerian_basic():
    t = jnp.linspace(-1.0, 10.0, 1000)

    mstar = 0.98
    rstar = 0.93
    ld = [0.1, 0.3]

    time_transit = jnp.array([0.0, 0.5])
    period = jnp.array([1, 4.5])
    b = jnp.array([0.5, 0.2])
    r = jnp.array([0.1, 0.3])

    host_star = orbits.KeplerianCentral.init(mass=mstar, radius=rstar)
    orbit_both = orbits.KeplerianOrbit.init(
        central=host_star,
        time_transit=time_transit,
        period=period,
        impact_param=b,
        radius=r,
    )
    lc_both = light_curves.QuadLightCurve(ld[0], ld[1]).light_curve(orbit_both, t)

    for n in range(2):
        orbit = orbits.KeplerianBody.init(
            central=host_star,
            time_transit=time_transit[n],
            period=period[n],
            impact_param=b[n],
            radius=r[n],
        )
        lc = light_curves.QuadLightCurve(ld[0], ld[1]).light_curve(orbit, t)
        assert_allclose(lc, lc_both[n])


@pytest.mark.parametrize("radius", [0.01, 0.1, 1.0, 1.5])
@pytest.mark.parametrize("ld_order", [0, 1, 2])
def test_quad_limb_dark_consistency(radius, ld_order):
    t = jnp.linspace(-1.0, 10.0, 1000)

    mstar = 0.98
    rstar = 0.93

    time_transit = jnp.array([0.0, 0.5])
    period = jnp.array([1, 4.5])
    b = jnp.array([0.5, 0.2])

    host_star = orbits.KeplerianCentral.init(mass=mstar, radius=rstar)
    orbit = orbits.KeplerianOrbit.init(
        central=host_star,
        time_transit=time_transit,
        period=period,
        impact_param=b,
        radius=jnp.array([radius, 0.3]),
    )

    ld = [0.1 if ld_order > 0 else 0.0, 0.3 if ld_order > 1 else 0.0]
    lc0 = light_curves.QuadLightCurve.init(*ld).light_curve(orbit, t)
    lc1 = light_curves.LimbDarkLightCurve.init(*ld[:ld_order]).light_curve(orbit, t)
    assert_allclose(lc0, lc1)

    lc2 = light_curves.LimbDarkLightCurve.init(jnp.array(ld[:ld_order])).light_curve(
        orbit, t
    )
    assert_allclose(lc0, lc2)