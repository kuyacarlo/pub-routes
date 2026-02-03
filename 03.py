from multiprocessing import Pool
import pandas as pd
import pdfplumber
from pathlib import Path
from enum import Enum, auto
from typing import Literal, Optional

class Action(Enum):
    SKIP = auto()
    COLUMN = auto()

_ALLOWED = {"PUJ","UVX"}
class PUVParser:
    def __init__(
        self,
        region: str,
        puv_type: str = "PUJ",
        is_consolidated: bool = True
    ):
        if puv_type not in _ALLOWED:
            raise ValueError(f"puv_type must be one of {_ALLOWED}")
        self.transpo_type = puv_type
        self.is_consolidated = is_consolidated
        self.headers = [
            "region",
            "transpo_type",
            "route_name",
            "route_status",
            "is_consolidated",
            "is_above_consolidation_threshold",
        ]
        self.region = region
        self.current_status = None
        self.current_consolidation = None
        self.converters = [
            self._parse_consolidation,
            self._parse_route_status,
        ]
        self.skip_filters = [
            lambda r: "franchising regulatory board" in r[0].lower(),
            lambda r: "puj routes" in r[0].lower(),
            lambda r: "count" in r[0].lower() and r[1] is not None and "route name" in r[1].lower()
        ]
    def _parse_route_status(self, row) -> bool:
        text = row[0].lower()
        mapping = {
            "with approved lptrp": "approved_lptrp",
            "no lptrp": "no_lptrp",
            "with approved mucep rrp/irip": "approved_mucep_rrp_irip",
            "no mucep rrp/irip": "no_mucep_rrp_irip",
            "new/developmental/missionary routes": "new_developmental_missionary_route",
        }
        for k, v in mapping.items():
            if k in text:
                self.current_status = v
                self.current_consolidation = None
                return True

    def _parse_consolidation(self, row) -> bool:
        if not self.is_consolidated:
            return False
        text = (row[0] or "").lower()
        if "60%" in text:
            self.current_consolidation = "above" in text
            return True
    
    def _parser(self, row: list) -> Optional[list]:
        if any(f(row) for f in self.skip_filters):
            return None

        for converter in self.converters:
            if converter(row):
                return None
        return [
            self.region,
            self.transpo_type,
            row[1], # The data col(first col is index)
            self.current_status,
            self.is_consolidated,
            self.current_consolidation,
        ]
        
    def parse(self, rows: list) -> Optional[list]:
        output_list = []

        for row in rows:
            parsed_row = self._parser(row)
            if parsed_row is None:
                continue
            output_list.append(parsed_row)

        return output_list
    
    def get_dataframe(self, rows:list) -> pd.DataFrame:
        return pd.DataFrame(self.parse(rows), columns=self.headers)

def parse_file(
    filename: str | Path,
    region: str,
    puv_type: str = "PUJ",
    is_consolidated: bool = True
) -> pd.DataFrame:
    if puv_type not in _ALLOWED:
        raise ValueError(f"puv_type must be one of {_ALLOWED}")
    with pdfplumber.open(filename) as pdf:
        all_rows = []
        for page in pdf.pages:
            table = page.extract_table()
            all_rows.extend(table)
    manager = PUVParser(
        region = region,
        puv_type = puv_type,
        is_consolidated = is_consolidated
    )
    
    return manager.get_dataframe(all_rows)

def get_region_name(folder_name:str) -> str:
    """Gets the region name slug, uses LTFRB naming logic"""
    folder_name_parts = folder_name.split(" ")
    region_name_parts = []
    is_parenthesized = "(" in folder_name and ")" in folder_name
    
    for part in folder_name_parts:
        if is_parenthesized:
            if "(" in part:
                region_name_parts.append(part[1:])
            elif ")" in part:
                region_name_parts.append(part[:-1])
        else:
            if "Routes" not in part:
                region_name_parts.append(part)
    return "_".join(region_name_parts).lower().replace(")", "")

def get_output_path(filename_parts: tuple, output_folder: Path):
    folder, file = filename_parts
    file = Path(file).with_suffix(".csv").name
    
    output_folder = output_folder / folder
    output_folder.mkdir(parents=True, exist_ok=True)
    
    output_file = output_folder / file
    
    return output_file

def parse_file_worker(args):
    file_name, region_name, puv_type, is_consolidated, output_file = args
    try:
        cleaned_data = parse_file(
            filename=file_name,
            region=region_name,
            puv_type=puv_type,
            is_consolidated=is_consolidated
        )
        cleaned_data.to_csv(output_file, index=False)

        return (file_name, "success", None)
    except Exception as e:
        # print(str(e))
        return (file_name, "failed", str(e))

def main(main_folder, output_folder):
    jobs = []
    
    # Loop over files
    # check its metadata
    # do the parsing
    # output onto a csv file

    for region in Path(main_folder).iterdir():
        if not region.is_dir():
            continue
        region_name = get_region_name(region.name)
        
        for file in region.iterdir():
            if not file.is_file():
                continue
            puv_type = "PUJ" if "puj" in file.name.lower() else "UVX"
            consolidated = "with consolidated" in file.name.lower()
            output_file = get_output_path((region.name, file.name), Path(output_folder))
            jobs.append(
                (
                    file, region_name, puv_type, consolidated, output_file
                )
            )
    with Pool(processes = 16) as pool:
        results = pool.map(parse_file_worker, jobs)
    for fname, status, msg in results:
        print(f"{fname.name}: {status}" + (f" | {msg}" if msg else ""))
    # do the file finding(and checking) process

if __name__ == '__main__':
    main("./Regions", "./output")
    # print(parse_file(
    #     'Regions/Cordillera Routes/PUJ Routes with Consolidated Entities.pdf',
    #     "cordillera",
    #     "PUJ",
    #     True
    # ))
    