"""Radarformate: Seit dem 20.10.2026 liefert der DWD ODIM-HDF5 statt RADOLAN-Binär.

Geprüft ohne Netz mit selbst geschriebenen HDF5-Dateien: Erkennung am Inhalt, Kippen auf RADOLAN-Zeilenfolge
(Zeile 0 im Süden), Einheiten (RATE mm/h, ACRR Höhe je Intervall), Kennungen für keine Messung und kein
Niederschlag sowie die Dateinamen beider Archivformate im Verzeichnis.
"""

import io

import h5py
import numpy as np

from wetterwarte.providers import radar


def _hdf5(daten: np.ndarray, groesse: str, gain: float, nodata: float, start: str = "120000", ende: str = "120500") -> bytes:
    puffer = io.BytesIO()
    with h5py.File(puffer, "w") as datei:
        satz = datei.create_dataset("dataset1/data1/data", data=daten)
        was = datei["dataset1/data1"].create_group("what")
        was.attrs["quantity"] = np.bytes_(groesse)
        was.attrs["gain"] = gain
        was.attrs["offset"] = 0.0
        was.attrs["nodata"] = nodata
        was.attrs["undetect"] = 0.0
        zeit = datei["dataset1"].create_group("what")
        zeit.attrs["starttime"] = np.bytes_(start)
        zeit.attrs["endtime"] = np.bytes_(ende)
        assert satz is not None
    return puffer.getvalue()


def test_rate_wird_gekippt_und_bleibt_mm_je_stunde() -> None:
    roh = np.zeros((1200, 1100), dtype="u2")
    roh[0, 5] = 250          # oberste Zeile in HDF5 = Norden
    roh[1, 6] = 65535        # keine Messung
    wert = radar.werte(_hdf5(roh, "RATE", 0.01, 65535.0))
    assert wert.shape == (1200, 1100)
    assert wert[-1, 5] == np.float32(2.5)      # im RADOLAN-Gitter unten = Norden
    assert np.isnan(wert[-2, 6])
    assert wert[0, 0] == 0.0
    assert radar.index_fuer(wert) is radar._IDX_1200


def test_acrr_wird_auf_die_stunde_hochgerechnet() -> None:
    roh = np.zeros((1200, 1100), dtype="u4")
    roh[600, 500] = 1000     # 1,0 mm in 5 Minuten
    wert = radar.werte(_hdf5(roh, "ACRR", 0.001, 4294967295.0))
    assert abs(float(wert[1200 - 1 - 600, 500]) - 12.0) < 1e-4


def test_acrr_ueber_mitternacht() -> None:
    roh = np.zeros((1200, 1100), dtype="u4")
    roh[0, 0] = 500
    wert = radar.werte(_hdf5(roh, "ACRR", 0.001, 4294967295.0, start="235500", ende="000000"))
    assert abs(float(wert[-1, 0]) - 6.0) < 1e-4


def test_werte_an_einzelnen_punkten() -> None:
    roh = np.zeros((1200, 1100), dtype="u2")
    roh[1199, 3] = 100       # unterste HDF5-Zeile = Zeile 0 im RADOLAN-Gitter
    datei = _hdf5(roh, "RATE", 0.01, 65535.0)
    ergebnis = radar.werte_an(datei, np.array([3, -1, 4], dtype=np.int64))
    assert ergebnis[0] == np.float32(1.0)
    assert np.isnan(ergebnis[1])
    assert ergebnis[2] == 0.0


def test_archive_beider_formate_im_verzeichnis() -> None:
    listing = (
        '<a href="DE1200_RV2610200755.tar.bz2">'
        '<a href="composite_rv_20261020_1650.tar">'
        '<a href="composite_rv_LATEST.tar">'
    )
    archive = radar.rv_archive(listing)
    assert archive == {"2610200755": "DE1200_RV2610200755.tar.bz2", "2610201650": "composite_rv_20261020_1650.tar"}
    assert sorted(archive)[-1] == "2610201650"


def test_stufen_beider_formate() -> None:
    assert radar.RV_STUFE.search("DE1200_RV2610200755_005").group(1) == "005"
    assert radar.RV_STUFE.search("composite_rv_20261020_1650_120-hd5").group(1) == "120"
    assert radar.RV_STUFE.search("composite_rv_20261020_1650") is None
