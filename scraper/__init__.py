"""
LCRA Flood Status Web Scraper

This module contains the LCRAFloodDataScraper class for extracting data from the LCRA API.
"""

import re
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import HTTPException

from lcra import (
    DataSource,
    FloodgateOperation,
    FloodOperationsReport,
    LakeLevel,
    RiverCondition,
)


class LCRAFloodDataScraper:
    """
    Web scraper for LCRA flood status data using the API endpoints
    """

    BASE_URL = "https://hydromet.lcra.org"
    TIMEOUT = 30.0

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=self.TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def fetch_api_data(self, endpoint: str) -> dict:
        """Fetch data from LCRA API endpoints"""
        if not self.session:
            raise RuntimeError("Scraper must be used as async context manager")
        url = f"{self.BASE_URL}/api/{endpoint}"
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, detail=f"Failed to fetch data from LCRA API: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error parsing LCRA API data: {str(e)}"
            )

    async def scrape_lake_levels(self) -> List[LakeLevel]:
        """Extract current lake levels from API"""
        try:
            data = await self.fetch_api_data("FloodStatus/GetLakeLevelsGateOps")
            lake_levels = []
            for record in data.get("records", []):
                lake_level = LakeLevel(
                    dam_lake_name=f"{record.get('dam', '')}/{record.get('lake', '')}",
                    measurement_time=self.parse_datetime(record.get("lastDataUpdate")),
                    head_elevation=self.parse_float(record.get("head")),
                    tail_elevation=self.parse_float(record.get("tail")),
                    gate_operations=record.get("gateOps"),
                )
                lake_levels.append(lake_level)
            return lake_levels
        except Exception as e:
            print(f"Error fetching lake levels: {e}")
            return []

    async def scrape_river_conditions(self) -> List[RiverCondition]:
        """Extract current river conditions from API"""
        try:
            data = await self.fetch_api_data("GetForecastReferences")
            river_conditions = []
            for site in data.get("sites", []):
                condition = RiverCondition(
                    location=site.get("location", ""),
                    current_stage=self.parse_float(site.get("stage")),
                    current_flow=self.parse_float(site.get("flow")),
                    bankfull_stage=self.parse_float(site.get("bankfull")),
                    flood_stage=self.parse_float(site.get("floodStage")),
                    action_stage=self.parse_float(site.get("bankfull")),
                    measurement_time=self.parse_datetime(site.get("dateTime")),
                    data_source=DataSource.LCRA,
                )
                river_conditions.append(condition)
            return river_conditions
        except Exception as e:
            print(f"Error fetching river conditions: {e}")
            return []

    async def scrape_floodgate_operations(self) -> List[FloodgateOperation]:
        """Extract floodgate operations data from API"""
        try:
            data = await self.fetch_api_data("FloodStatus/GetLakeLevelsGateOps")
            operations = []
            for record in data.get("records", []):
                operation = FloodgateOperation(
                    dam_name=record.get("dam", "Unknown Dam"),
                    last_update=self.parse_datetime(record.get("lastUpdate")),
                    inflows=self.parse_float(record.get("inflows")),
                    gate_operations=record.get("gateOps"),
                    lake_level_forecast=record.get("forecast"),
                    current_elevation=self.parse_float(record.get("head")),
                )
                operations.append(operation)
            return operations
        except Exception as e:
            print(f"Error fetching floodgate operations: {e}")
            return []

    async def get_narrative_summary(self) -> tuple[Optional[datetime], Optional[str]]:
        """Get narrative summary and last update time"""
        try:
            data = await self.fetch_api_data("FloodStatus/GetNarrativeSummary")
            if data and len(data) > 0:
                record = data[0]
                last_update = self.parse_datetime(record.get("lastUpdate"))
                narrative = record.get("narrive_sum")
                return last_update, narrative
            return None, None
        except Exception as e:
            print(f"Error fetching narrative summary: {e}")
            return None, None

    @staticmethod
    def parse_datetime(text: str) -> Optional[datetime]:
        """Parse various datetime formats found on the site"""
        if not text or text.strip() == "" or text == "/":
            return None
        try:
            if "T" in text:
                clean_text = (
                    text.split("T")[0]
                    + " "
                    + text.split("T")[1].split("+")[0].split("-")[0].split("Z")[0]
                )
                return datetime.fromisoformat(clean_text.replace("Z", ""))
        except:
            pass
        patterns = [
            r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2})\s*(AM|PM)?",
            r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})\s*(AM|PM)?",
            r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})",
            r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) >= 3 and match.group(3):
                        date_str = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                        if "/" in match.group(1):
                            return datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p")
                        else:
                            return datetime.strptime(date_str, "%Y-%m-%d %I:%M:%S %p")
                    else:
                        date_str = f"{match.group(1)} {match.group(2)}"
                        if "/" in match.group(1):
                            if (
                                ":" in match.group(2)
                                and len(match.group(2).split(":")) == 3
                            ):
                                return datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")
                            else:
                                return datetime.strptime(date_str, "%m/%d/%Y %H:%M")
                        else:
                            if (
                                ":" in match.group(2)
                                and len(match.group(2).split(":")) == 3
                            ):
                                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                            else:
                                return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
        return None

    @staticmethod
    def parse_float(text: str) -> Optional[float]:
        """Parse float values from text, handling various formats"""
        if not text or text in ["/", "N/A", "n/a", "--", None]:
            return None
        if isinstance(text, (int, float)):
            return float(text)
        if isinstance(text, str):
            cleaned = re.sub(r"[^\d.-]", "", text.strip())
            if not cleaned:
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    async def scrape_all_data(self) -> FloodOperationsReport:
        """Scrape all available data from the flood status APIs"""
        last_update, narrative = await self.get_narrative_summary()
        lake_levels = await self.scrape_lake_levels()
        river_conditions = await self.scrape_river_conditions()
        floodgate_operations = await self.scrape_floodgate_operations()
        return FloodOperationsReport(
            report_time=datetime.now(),
            last_update=last_update,
            lake_levels=lake_levels,
            river_conditions=river_conditions,
            river_forecasts=[],
            floodgate_operations=floodgate_operations,
        )
