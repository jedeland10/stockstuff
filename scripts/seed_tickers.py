#!/usr/bin/env python3
"""Seed the database with top Nordic tickers."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, DB_PATH, DATA_DIR
from app.services.fetcher import fetch_stock_info
import aiosqlite
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# Nordic tickers — comprehensive list
TICKERS = [
    # ── Sweden (.ST) — Large Cap ──
    "VOLV-B.ST", "ERIC-B.ST", "ASSA-B.ST", "HEXA-B.ST", "ATCO-A.ST",
    "SEB-A.ST", "SWED-A.ST", "SHB-A.ST", "INVE-B.ST", "ABB.ST",
    "SAND.ST", "ALFA.ST", "ESSITY-B.ST", "TELIA.ST", "SKF-B.ST",
    "ELUX-B.ST", "BOL.ST", "SCA-B.ST", "KINV-B.ST", "HM-B.ST",
    "SAAB-B.ST", "SINCH.ST", "EVO.ST", "NIBE-B.ST", "GETI-B.ST",
    "LIFCO-B.ST", "LUND-B.ST", "LATOUR-B.ST", "INDU-A.ST", "TREL-B.ST",
    "SSAB-A.ST", "SWEC-B.ST", "AXFO.ST", "BILL.ST", "BALD-B.ST",
    "FABG.ST", "EPRO-B.ST", "HPOL-B.ST", "SECT-B.ST", "SAGA-B.ST",
    "ADDV-B.ST", "SOBI.ST", "THULE.ST", "BIOT.ST", "LIME.ST",
    "MTRS-B.ST", "DIOS.ST", "WIHL.ST", "CAST.ST", "WALL-B.ST",
    # Sweden — Mid Cap
    "LAGR-B.ST", "COOR.ST", "MEKO.ST", "BOOZT.ST", "ARJO-B.ST",
    "BONAV-B.ST", "BRAV.ST", "HMS.ST", "NOLA-B.ST", "PNDX-B.ST",
    "RESURS.ST", "SYSR.ST", "CATE.ST", "BALCO.ST", "BMAX.ST",
    "CAMX.ST", "CIBUS.ST", "CLAS-B.ST", "COIC.ST", "DUROC-B.ST",
    "ELTEL.ST", "ENEA.ST", "GREEN.ST", "HEMF-B.ST", "HANZA.ST",
    "IAR-B.ST", "INDT.ST", "IRLAB-A.ST", "KABE-B.ST", "KFAST-B.ST",
    "KNOW.ST", "LATO-B.ST", "LOOM-B.ST", "LUND-B.ST", "MANG.ST",
    "NEWA-B.ST", "NMAN.ST", "NOTE.ST", "OEM-B.ST", "PRIC-B.ST",
    "PROB.ST", "RATO-B.ST", "SAVE.ST", "SDIP-B.ST", "SECU-B.ST",
    "SOLT.ST", "STE-R.ST", "SVED-B.ST", "TIGO-SDB.ST", "VIT-B.ST",
    # ── Denmark (.CO) — Large Cap ──
    "NOVO-B.CO", "MAERSK-B.CO", "DSV.CO", "VWS.CO", "CARL-B.CO",
    "PNDORA.CO", "COLO-B.CO", "ORSTED.CO", "TRYG.CO", "GN.CO",
    "DEMANT.CO", "ROCK-B.CO", "AMBU-B.CO", "FLS.CO", "DANSKE.CO",
    "ISS.CO", "JYSK.CO", "RBREW.CO", "NETC.CO", "GMAB.CO",
    "BAVA.CO", "TOP.CO", "NKT.CO", "DNORD.CO", "RILBA.CO",
    # Denmark — Mid/Small Cap
    "NNIT.CO", "PAAL-B.CO", "RORBA.CO", "SOLAR-B.CO", "SPNO.CO",
    "ALK-B.CO", "ASTK.CO", "BNORD.CO", "CBRAIN.CO", "CEMAT.CO",
    "CPHCAP.CO", "DFDS.CO", "FYNBK.CO", "GRLA.CO", "HART.CO",
    "HUSCO.CO", "JUTBK.CO", "KBHL.CO", "LUXOR-B.CO", "MATAS.CO",
    "MTCH-B.CO", "NORTH.CO", "NSIS-B.CO", "ONXO.CO", "PENM.CO",
    "ROCK-A.CO", "SCHUR.CO", "SAS-DKK.CO", "SKJE.CO", "STGT.CO",
    "SVAN.CO", "TFBANK.CO", "TIVOLI.CO", "VER.CO", "ZEAL.CO",
    # ── Finland (.HE) — Large Cap ──
    "NOKIA.HE", "SAMPO.HE", "NESTE.HE", "FORTUM.HE", "UPM.HE",
    "KNEBV.HE", "STERV.HE", "WRT1V.HE", "ELISA.HE", "ORNBV.HE",
    "OUT1V.HE", "TYRES.HE", "KESKOB.HE", "METSO.HE", "METSB.HE",
    "KEMIRA.HE", "HUH1V.HE", "VALMT.HE", "TIETO.HE", "QTCOM.HE",
    "SSABBH.HE", "KOJAMO.HE", "TEM1V.HE",
    # Finland — Mid/Small Cap
    "AKTIA.HE", "ALMA.HE", "APETIT.HE", "ASPO.HE", "BITTI.HE",
    "CAPMAN.HE", "CTH1V.HE", "DIGIGR.HE", "DIGIA.HE", "EFORAF.HE",
    "ETTE.HE", "FSKRS.HE", "GOFORE.HE", "HARVIA.HE", "IFA1V.HE",
    "KAMUX.HE", "KSLAV.HE", "LEHTO.HE", "MARAS.HE", "MUSTI.HE",
    "OLVAS.HE", "OKDAV.HE", "PIHLIS.HE", "PON1V.HE", "RAIKV.HE",
    "REG1V.HE", "REMEDY.HE", "ROVIO.HE", "SAGCV.HE", "SIILI.HE",
    "SOPRA.HE", "STOCKA.HE", "TNOM.HE", "TOKMAN.HE", "TRH1V.HE",
    "TULAV.HE", "UPONOR.HE", "VAlmt.HE", "VINCIT.HE", "WITH.HE",
    # ── Norway (.OL) — Large Cap ──
    "EQNR.OL", "DNB.OL", "TEL.OL", "MOWI.OL", "ORK.OL",
    "AKRBP.OL", "YAR.OL", "SALM.OL", "SUBC.OL", "AKER.OL",
    "GJF.OL", "KOG.OL", "SCATC.OL", "BWLPG.OL", "NHY.OL",
    "AUTO.OL", "MEDI.OL", "ENTRA.OL", "RECSI.OL", "HAFNI.OL",
    "TGS.OL", "BAKKA.OL", "SOFF.OL", "KIT.OL", "NSKOG.OL",
    # Norway — Mid/Small Cap
    "AKSO.OL", "ATEA.OL", "AUSS.OL", "BELCO.OL", "BONHR.OL",
    "BORR.OL", "BWO.OL", "CADLR.OL", "CRAYN.OL", "ELK.OL",
    "ENDUR.OL", "EPR.OL", "FROY.OL", "GOGL.OL", "HAUTO.OL",
    "HEX.OL", "HMONY.OL", "IDEX.OL", "KAHOT.OL", "KOA.OL",
    "LSG.OL", "MPCC.OL", "MULTI.OL", "NAPA.OL", "NAS.OL",
    "NOD.OL", "NOFI.OL", "OET.OL", "OKEA.OL", "OLT.OL",
    "PARB.OL", "PROT.OL", "PGS.OL", "SDRL.OL", "SRBNK.OL",
    "STB.OL", "SCHA.OL", "VOW.OL", "WSTEP.OL", "XXL.OL",
]


COUNTRY_MAP = {
    ".ST": "SE",
    ".HE": "FI",
    ".CO": "DK",
    ".OL": "NO",
}


async def seed():
    await init_db()
    async with aiosqlite.connect(str(DB_PATH)) as db:
        total = len(TICKERS)
        success = 0
        for i, ticker in enumerate(TICKERS, 1):
            logger.info(f"[{i}/{total}] Fetching {ticker}...")
            info = fetch_stock_info(ticker)
            if info is None:
                logger.warning(f"  Skipped {ticker}")
                continue

            # Determine country from suffix
            country = info.get("country", "")
            for suffix, code in COUNTRY_MAP.items():
                if ticker.endswith(suffix):
                    country = code
                    break

            await db.execute("""
                INSERT OR REPLACE INTO stocks
                (ticker, name, exchange, country, sector, industry, market_cap, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker, info["name"], info["exchange"], country,
                info["sector"], info["industry"], info["market_cap"],
                info["description"],
            ))

            await db.execute("""
                INSERT OR REPLACE INTO fundamentals
                (ticker, price, change_pct, pe, pb, ps, ev_ebitda,
                 div_yield, roe, margin, eps, revenue, revenue_growth,
                 perf_1y, report_quarter, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                ticker, info["price"], info["change_pct"],
                info["pe"], info["pb"], info["ps"], info["ev_ebitda"],
                info["div_yield"], info["roe"], info["margin"],
                info["eps"], info["revenue"], info["revenue_growth"],
                info["perf_1y"], info["report_quarter"],
            ))
            success += 1

        await db.commit()
        logger.info(f"Seeded {success}/{total} stocks.")


if __name__ == "__main__":
    asyncio.run(seed())
